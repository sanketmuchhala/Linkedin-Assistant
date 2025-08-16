from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .db import DatabaseManager, get_or_create_contact, init_db
from .models import Contact, Touchpoint, Message
from .dedupe import create_or_merge_touchpoint, merge_duplicate_touchpoints
from .generator import generate_variants, save_messages
from .reports.export import export_contacts_csv, export_contacts_markdown, get_export_stats
from .utils import clean_linkedin_url, parse_tags, format_tags
from .analytics import LinkedInAnalytics
from .follow_up import FollowUpSequencer, ConnectionScorer, IndustryInsights

app = FastAPI(title="LinkedIn Follow-Up Assistant API", version="0.1.0")

init_db()


class ContactCreate(BaseModel):
    name: str
    company: Optional[str] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    request_reason: Optional[str] = None
    connection_status: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    company: Optional[str]
    role: Optional[str]
    linkedin_url: Optional[str]
    tags: Optional[str]
    notes: Optional[str]
    request_reason: Optional[str]
    connection_status: Optional[str]
    message_sent: bool
    last_message_date: Optional[datetime]
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


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main HTML interface."""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>LinkedIn Follow-Up Assistant</h1><p>Frontend not found. API is running at /docs</p>")

@app.get("/api")
def read_api_root():
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
        if contact.request_reason:
            contact_obj.request_reason = contact.request_reason
        if contact.connection_status:
            contact_obj.connection_status = contact.connection_status
        
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
            request_reason=contact_obj.request_reason,
            connection_status=contact_obj.connection_status,
            message_sent=bool(contact_obj.message_sent),
            last_message_date=contact_obj.last_message_date,
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
            request_reason=contact.request_reason,
            connection_status=contact.connection_status,
            message_sent=bool(contact.message_sent),
            last_message_date=contact.last_message_date,
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
        request_reason=contact.request_reason,
        connection_status=contact.connection_status,
        message_sent=bool(contact.message_sent),
        last_message_date=contact.last_message_date,
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
                request_reason=contact.request_reason,
                connection_status=contact.connection_status,
                message_sent=bool(contact.message_sent),
                last_message_date=contact.last_message_date,
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


@app.post("/contacts/{contact_id}/mark-message-sent")
def mark_message_sent(contact_id: int, db: Session = Depends(get_db)):
    """Mark that a message has been sent to this contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.message_sent = 1
    contact.last_message_date = datetime.utcnow()
    contact.outreach_status = "contacted"
    contact.connection_status = "message_sent"
    db.commit()
    db.refresh(contact)
    
    return {"message": "Contact marked as message sent", "contact_id": contact_id}


@app.post("/contacts/{contact_id}/mark-response")
def mark_response_received(contact_id: int, db: Session = Depends(get_db)):
    """Mark that a response was received from this contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.response_received = 1
    contact.response_date = datetime.utcnow()
    contact.outreach_status = "responded"
    db.commit()
    db.refresh(contact)
    
    return {"message": "Response marked", "contact_id": contact_id}


@app.post("/contacts/{contact_id}/mark-request-sent")
def mark_request_sent(contact_id: int, db: Session = Depends(get_db)):
    """Mark that a connection request has been sent to this contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.connection_status = "request_sent"
    db.commit()
    db.refresh(contact)
    
    return {"message": "Connection request marked as sent", "contact_id": contact_id}


@app.post("/contacts/{contact_id}/mark-request-accepted")
def mark_request_accepted(contact_id: int, db: Session = Depends(get_db)):
    """Mark that the connection request was accepted."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.connection_status = "request_accepted"
    db.commit()
    db.refresh(contact)
    
    return {"message": "Connection request marked as accepted", "contact_id": contact_id}


@app.get("/pending-followup")
def get_pending_followup_contacts(db: Session = Depends(get_db)):
    """Get contacts that have accepted connection requests but haven't been messaged."""
    contacts = db.query(Contact).filter(
        Contact.connection_status == "request_accepted",
        Contact.message_sent == 0
    ).all()
    
    return [
        {
            "id": contact.id,
            "name": contact.name,
            "company": contact.company,
            "request_reason": contact.request_reason,
            "days_since_accepted": (datetime.utcnow() - contact.updated_at).days if contact.updated_at else None
        }
        for contact in contacts
    ]


@app.get("/analytics/dashboard")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive analytics dashboard."""
    analytics = LinkedInAnalytics(db)
    return analytics.get_dashboard_metrics()


@app.get("/analytics/contact/{contact_id}")
def get_contact_insights(contact_id: int, db: Session = Depends(get_db)):
    """Get detailed insights for a specific contact."""
    analytics = LinkedInAnalytics(db)
    insights = analytics.get_contact_insights(contact_id)
    if not insights:
        raise HTTPException(status_code=404, detail="Contact not found")
    return insights


@app.post("/analytics/update-daily")
def update_daily_analytics(db: Session = Depends(get_db)):
    """Update daily analytics summary."""
    analytics = LinkedInAnalytics(db)
    result = analytics.update_daily_analytics()
    return {"message": "Daily analytics updated", "date": result.date}


# Follow-up Automation Endpoints
@app.get("/followup/pending")
def get_pending_followups(days_threshold: int = 7, db: Session = Depends(get_db)):
    """Get contacts that need follow-up messages."""
    sequencer = FollowUpSequencer(db)
    return sequencer.get_pending_followups(days_threshold)


@app.post("/followup/generate/{contact_id}")
def generate_automated_followup(contact_id: int, message_type: str = "gentle_followup", db: Session = Depends(get_db)):
    """Generate automated follow-up message."""
    sequencer = FollowUpSequencer(db)
    messages = sequencer.generate_followup_message(contact_id, message_type)
    if not messages:
        raise HTTPException(status_code=404, detail="Contact not found or no touchpoints available")
    
    return {
        "contact_id": contact_id,
        "message_type": message_type,
        "messages": [
            {
                "id": msg.id,
                "variant": msg.variant,
                "body": msg.body,
                "tone": msg.tone
            }
            for msg in messages
        ]
    }


class ScheduleFollowUp(BaseModel):
    follow_up_date: str

@app.post("/followup/schedule/{contact_id}")
def schedule_followup(contact_id: int, schedule_data: ScheduleFollowUp, db: Session = Depends(get_db)):
    """Schedule a follow-up for a specific contact."""
    try:
        from datetime import datetime
        follow_up_datetime = datetime.fromisoformat(schedule_data.follow_up_date)
        sequencer = FollowUpSequencer(db)
        success = sequencer.schedule_followup(contact_id, follow_up_datetime)
        if success:
            return {"message": "Follow-up scheduled", "contact_id": contact_id, "scheduled_date": schedule_data.follow_up_date}
        else:
            raise HTTPException(status_code=404, detail="Contact not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS")


@app.get("/followup/scheduled")
def get_scheduled_followups(date: str = None, db: Session = Depends(get_db)):
    """Get contacts scheduled for follow-up."""
    sequencer = FollowUpSequencer(db)
    target_date = None
    if date:
        try:
            from datetime import datetime
            target_date = datetime.fromisoformat(date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    return sequencer.get_scheduled_followups(target_date)


# Connection Scoring Endpoints
@app.post("/scoring/update-all")
def update_connection_scores(db: Session = Depends(get_db)):
    """Update connection strength scores for all contacts."""
    scorer = ConnectionScorer(db)
    updated_count = scorer.update_all_connection_scores()
    return {"message": f"Updated {updated_count} contact scores"}


@app.get("/scoring/high-value")
def get_high_value_contacts(min_score: int = 4, db: Session = Depends(get_db)):
    """Get high-value contacts based on connection strength."""
    scorer = ConnectionScorer(db)
    return scorer.get_high_value_contacts(min_score)


class PriorityUpdate(BaseModel):
    priority: str

@app.post("/contacts/{contact_id}/priority")
def update_contact_priority(contact_id: int, priority_data: PriorityUpdate, db: Session = Depends(get_db)):
    """Update contact priority level."""
    priority = priority_data.priority
    if priority not in ["high", "medium", "low"]:
        raise HTTPException(status_code=400, detail="Priority must be 'high', 'medium', or 'low'")
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.priority_level = priority
    db.commit()
    return {"message": "Priority updated", "contact_id": contact_id, "priority": priority}


# Industry Insights Endpoints
@app.get("/insights/industry")
def get_industry_insights(db: Session = Depends(get_db)):
    """Get performance insights by industry."""
    insights = IndustryInsights(db)
    return insights.get_industry_performance()


@app.get("/insights/roles")
def get_role_insights(db: Session = Depends(get_db)):
    """Get insights by job roles."""
    insights = IndustryInsights(db)
    return insights.get_role_insights()


# Bulk Operations
@app.post("/contacts/bulk-update-industry")
def bulk_update_industries(db: Session = Depends(get_db)):
    """Bulk update industries based on company names (AI-powered)."""
    contacts = db.query(Contact).filter(
        Contact.industry.is_(None),
        Contact.company.isnot(None)
    ).all()
    
    updated_count = 0
    # Simple industry mapping based on company names
    industry_keywords = {
        "Technology": ["google", "microsoft", "amazon", "apple", "meta", "netflix", "uber", "airbnb", "stripe", "salesforce"],
        "Finance": ["goldman sachs", "jp morgan", "bank", "capital", "financial", "investment"],
        "Healthcare": ["hospital", "medical", "health", "pharma", "biotech"],
        "Consulting": ["mckinsey", "bcg", "bain", "deloitte", "pwc", "accenture"],
        "E-commerce": ["shopify", "ebay", "etsy", "amazon"],
        "Media": ["disney", "warner", "netflix", "spotify"]
    }
    
    for contact in contacts:
        company_lower = contact.company.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in company_lower for keyword in keywords):
                contact.industry = industry
                updated_count += 1
                break
    
    db.commit()
    return {"message": f"Updated {updated_count} contact industries"}