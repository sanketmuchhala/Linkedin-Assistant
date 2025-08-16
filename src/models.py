from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    tags = Column(Text, nullable=True)  # CSV format
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    touchpoints = relationship("Touchpoint", back_populates="contact", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="contact", cascade="all, delete-orphan")


class Touchpoint(Base):
    __tablename__ = "touchpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    context = Column(Text, nullable=False)
    dedupe_hash = Column(String(64), nullable=True)  # For exact matches
    similarity_group = Column(String(64), nullable=True)  # For near-duplicates
    is_canonical = Column(Integer, default=1)  # 1 = canonical, 0 = duplicate
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="touchpoints")
    messages = relationship("Message", back_populates="touchpoint", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    touchpoint_id = Column(Integer, ForeignKey("touchpoints.id"), nullable=False)
    variant = Column(Integer, nullable=False)  # 1, 2, or 3
    body = Column(Text, nullable=False)
    tone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="messages")
    touchpoint = relationship("Touchpoint", back_populates="messages")