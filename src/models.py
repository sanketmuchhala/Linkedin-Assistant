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
    request_reason = Column(Text, nullable=True)  # Why you sent the request
    message_sent = Column(Integer, default=0)  # 0 = not sent, 1 = sent
    last_message_date = Column(DateTime, nullable=True)
    
    # Premium Analytics Fields
    response_received = Column(Integer, default=0)  # 0 = no response, 1 = responded
    response_date = Column(DateTime, nullable=True)
    connection_strength = Column(Integer, default=1)  # 1-5 scale
    industry = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    mutual_connections = Column(Integer, default=0)
    profile_views = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    priority_level = Column(String(50), default='medium')  # high, medium, low
    follow_up_scheduled = Column(DateTime, nullable=True)
    outreach_status = Column(String(50), default='pending')  # pending, contacted, responded, connected, closed
    
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
    
    # Message Performance Analytics
    was_sent = Column(Integer, default=0)  # Track if this specific message was sent
    sent_date = Column(DateTime, nullable=True)
    response_received = Column(Integer, default=0)
    response_time_hours = Column(Integer, nullable=True)
    message_length = Column(Integer, nullable=True)
    
    # Relationships
    contact = relationship("Contact", back_populates="messages")
    touchpoint = relationship("Touchpoint", back_populates="messages")


class OutreachAnalytics(Base):
    __tablename__ = "outreach_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Daily metrics
    contacts_added = Column(Integer, default=0)
    messages_generated = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    connections_made = Column(Integer, default=0)
    
    # Response rates
    response_rate = Column(Integer, default=0)  # Percentage
    connection_rate = Column(Integer, default=0)  # Percentage
    
    # Industry breakdown (JSON string)
    industry_stats = Column(Text, nullable=True)
    
    # Top performing message tones
    best_performing_tone = Column(String(50), nullable=True)