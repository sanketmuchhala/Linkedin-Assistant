from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from .db import DatabaseManager, get_or_create_contact, init_db
from .models import Contact, Touchpoint, Message
from .dedupe import create_or_merge_touchpoint, merge_duplicate_touchpoints
from .generator import generate_variants, save_messages
from .reports.export import export_contacts_csv, export_contacts_markdown, get_export_stats
from .utils import clean_linkedin_url, parse_tags, format_tags

app = FastAPI(title="LinkedIn Follow-Up Assistant API", version="0.1.0")

init_db()


class ContactCreate(BaseModel):
    name: str
    company: Optional[str] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    company: Optional[str]
    role: Optional[str]
    linkedin_url: Optional[str]
    tags: Optional[str]
    notes: Optional[str]
    touchpoint_count: int
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TouchpointCreate(BaseModel):
    contact_id: int
    context: str


class TouchpointResponse(BaseModel):
    id: int
    contact_id: int
    context: str
    is_canonical: bool
    similarity_group: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    contact_id: int
    touchpoint_id: int
    variant: int
    body: str
    tone: str
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestRequest(BaseModel):
    contact_id: int
    tone: str = "friendly"
    ask: str = "a quick 15-min call"


class SuggestResponse(BaseModel):
    contact: ContactResponse
    touchpoint: TouchpointResponse
    messages: List[MessageResponse]


def get_db():
    with DatabaseManager() as db:
        yield db


@app.get("/")
def read_root():
    return {"message": "LinkedIn Follow-Up Assistant API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    try:
        contact_obj = get_or_create_contact(db, contact.name, contact.company)
        
        if contact.role:
            contact_obj.role = contact.role
        if contact.linkedin_url:
            contact_obj.linkedin_url = clean_linkedin_url(contact.linkedin_url)
        if contact.tags:
            contact_obj.tags = contact.tags
        if contact.notes:
            contact_obj.notes = contact.notes
        
        db.add(contact_obj)
        db.commit()
        db.refresh(contact_obj)
        
        return ContactResponse(
            id=contact_obj.id,
            name=contact_obj.name,
            company=contact_obj.company,
            role=contact_obj.role,
            linkedin_url=contact_obj.linkedin_url,
            tags=contact_obj.tags,
            notes=contact_obj.notes,
            touchpoint_count=len([tp for tp in contact_obj.touchpoints if tp.is_canonical]),
            message_count=len(contact_obj.messages),
            created_at=contact_obj.created_at,
            updated_at=contact_obj.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contacts", response_model=List[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    
    return [
        ContactResponse(
            id=contact.id,
            name=contact.name,
            company=contact.company,
            role=contact.role,
            linkedin_url=contact.linkedin_url,
            tags=contact.tags,
            notes=contact.notes,
            touchpoint_count=len([tp for tp in contact.touchpoints if tp.is_canonical]),
            message_count=len(contact.messages),
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        for contact in contacts
    ]


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=contact.id,
        name=contact.name,
        company=contact.company,
        role=contact.role,
        linkedin_url=contact.linkedin_url,
        tags=contact.tags,
        notes=contact.notes,
        touchpoint_count=len([tp for tp in contact.touchpoints if tp.is_canonical]),
        message_count=len(contact.messages),
        created_at=contact.created_at,
        updated_at=contact.updated_at
    )


@app.post("/touchpoints", response_model=TouchpointResponse)
def create_touchpoint(touchpoint: TouchpointCreate, db: Session = Depends(get_db)):
    try:
        contact = db.query(Contact).filter(Contact.id == touchpoint.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        touchpoint_obj, was_merged = create_or_merge_touchpoint(
            db, touchpoint.contact_id, touchpoint.context
        )
        
        return TouchpointResponse(
            id=touchpoint_obj.id,
            contact_id=touchpoint_obj.contact_id,
            context=touchpoint_obj.context,
            is_canonical=bool(touchpoint_obj.is_canonical),
            similarity_group=touchpoint_obj.similarity_group,
            created_at=touchpoint_obj.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contacts/{contact_id}/touchpoints", response_model=List[TouchpointResponse])
def get_contact_touchpoints(contact_id: int, db: Session = Depends(get_db)):
    touchpoints = db.query(Touchpoint).filter(Touchpoint.contact_id == contact_id).all()
    
    return [
        TouchpointResponse(
            id=tp.id,
            contact_id=tp.contact_id,
            context=tp.context,
            is_canonical=bool(tp.is_canonical),
            similarity_group=tp.similarity_group,
            created_at=tp.created_at
        )
        for tp in touchpoints
    ]


@app.post("/suggest", response_model=SuggestResponse)
def generate_suggestions(request: SuggestRequest, db: Session = Depends(get_db)):
    try:
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        touchpoint = db.query(Touchpoint).filter(
            Touchpoint.contact_id == request.contact_id,
            Touchpoint.is_canonical == 1
        ).order_by(Touchpoint.created_at.desc()).first()
        
        if not touchpoint:
            raise HTTPException(status_code=400, detail="No context found for contact")
        
        messages = generate_variants(db, contact, touchpoint, request.tone, request.ask, n=3)
        saved_messages = save_messages(db, messages)
        
        return SuggestResponse(
            contact=ContactResponse(
                id=contact.id,
                name=contact.name,
                company=contact.company,
                role=contact.role,
                linkedin_url=contact.linkedin_url,
                tags=contact.tags,
                notes=contact.notes,
                touchpoint_count=len([tp for tp in contact.touchpoints if tp.is_canonical]),
                message_count=len(contact.messages),
                created_at=contact.created_at,
                updated_at=contact.updated_at
            ),
            touchpoint=TouchpointResponse(
                id=touchpoint.id,
                contact_id=touchpoint.contact_id,
                context=touchpoint.context,
                is_canonical=bool(touchpoint.is_canonical),
                similarity_group=touchpoint.similarity_group,
                created_at=touchpoint.created_at
            ),
            messages=[
                MessageResponse(
                    id=msg.id,
                    contact_id=msg.contact_id,
                    touchpoint_id=msg.touchpoint_id,
                    variant=msg.variant,
                    body=msg.body,
                    tone=msg.tone,
                    created_at=msg.created_at
                )
                for msg in saved_messages
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contacts/{contact_id}/messages", response_model=List[MessageResponse])
def get_contact_messages(contact_id: int, limit: int = 10, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        Message.contact_id == contact_id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return [
        MessageResponse(
            id=msg.id,
            contact_id=msg.contact_id,
            touchpoint_id=msg.touchpoint_id,
            variant=msg.variant,
            body=msg.body,
            tone=msg.tone,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return get_export_stats(db)


@app.get("/tones")
def get_available_tones():
    return {
        "tones": ["friendly", "direct", "formal", "warm", "playful", "short-n-sweet"]
    }