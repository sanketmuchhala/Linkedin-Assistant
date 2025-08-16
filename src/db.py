import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Contact, Touchpoint, Message

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./followup.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except SQLAlchemyError as e:
        print(f"Error initializing database: {e}")
        return False


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def close_db(db: Session):
    """Close a database session."""
    try:
        db.close()
    except Exception:
        pass


class DatabaseManager:
    """Context manager for database operations."""
    
    def __init__(self):
        self.db = None
    
    def __enter__(self) -> Session:
        self.db = get_db()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            if exc_type:
                self.db.rollback()
            else:
                self.db.commit()
            close_db(self.db)


def get_or_create_contact(db: Session, name: str, company: str = None) -> Contact:
    """Get existing contact or create a new one."""
    contact = db.query(Contact).filter(
        Contact.name == name,
        Contact.company == (company or "")
    ).first()
    
    if not contact:
        contact = Contact(name=name, company=company)
        db.add(contact)
        db.flush()  # Get the ID without committing
    
    return contact