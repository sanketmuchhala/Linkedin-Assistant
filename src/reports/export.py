import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models import Contact, Touchpoint, Message
from ..utils import get_reports_dir, format_datetime, truncate_text


def export_contacts_csv(db: Session, output_path: Optional[str] = None) -> str:
    """Export contacts and their latest messages to CSV."""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = get_reports_dir() / f"contacts_{timestamp}.csv"
    
    # Query contacts with their latest canonical touchpoint and messages
    contacts = db.query(Contact).all()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'name', 'company', 'role', 'linkedin_url', 'tags',
            'latest_reason', 'latest_touchpoint_date',
            'variant_1', 'variant_2', 'variant_3',
            'tone', 'message_date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for contact in contacts:
            # Get latest canonical touchpoint
            latest_touchpoint = db.query(Touchpoint).filter(
                and_(
                    Touchpoint.contact_id == contact.id,
                    Touchpoint.is_canonical == 1
                )
            ).order_by(Touchpoint.created_at.desc()).first()
            
            # Get latest messages for this touchpoint
            messages = []
            if latest_touchpoint:
                messages = db.query(Message).filter(
                    Message.touchpoint_id == latest_touchpoint.id
                ).order_by(Message.created_at.desc(), Message.variant).limit(3).all()
            
            # Prepare row data
            row = {
                'name': contact.name,
                'company': contact.company or '',
                'role': contact.role or '',
                'linkedin_url': contact.linkedin_url or '',
                'tags': contact.tags or '',
                'latest_reason': latest_touchpoint.context if latest_touchpoint else '',
                'latest_touchpoint_date': format_datetime(latest_touchpoint.created_at) if latest_touchpoint else '',
                'variant_1': '',
                'variant_2': '',
                'variant_3': '',
                'tone': '',
                'message_date': ''
            }
            
            # Fill in message variants
            for msg in messages:
                if msg.variant <= 3:
                    row[f'variant_{msg.variant}'] = msg.body
                    if not row['tone']:  # Use tone from first message
                        row['tone'] = msg.tone
                        row['message_date'] = format_datetime(msg.created_at)
            
            writer.writerow(row)
    
    return str(output_path)


def export_contacts_markdown(db: Session, output_path: Optional[str] = None) -> str:
    """Export contacts and their latest messages to Markdown."""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = get_reports_dir() / f"contacts_{timestamp}.md"
    
    contacts = db.query(Contact).all()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# LinkedIn Follow-Up Assistant - Contact Export\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total contacts: {len(contacts)}\n\n")
        f.write("---\n\n")
        
        for contact in contacts:
            f.write(f"## {contact.name}\n\n")
            
            # Contact details
            f.write("**Contact Info:**\n")
            f.write(f"- Company: {contact.company or 'N/A'}\n")
            f.write(f"- Role: {contact.role or 'N/A'}\n")
            if contact.linkedin_url:
                f.write(f"- LinkedIn: {contact.linkedin_url}\n")
            if contact.tags:
                f.write(f"- Tags: {contact.tags}\n")
            f.write(f"- Added: {format_datetime(contact.created_at)}\n\n")
            
            # Latest touchpoint
            latest_touchpoint = db.query(Touchpoint).filter(
                and_(
                    Touchpoint.contact_id == contact.id,
                    Touchpoint.is_canonical == 1
                )
            ).order_by(Touchpoint.created_at.desc()).first()
            
            if latest_touchpoint:
                f.write("**Latest Context:**\n")
                f.write(f"> {latest_touchpoint.context}\n")
                f.write(f"*Added: {format_datetime(latest_touchpoint.created_at)}*\n\n")
                
                # Latest messages
                messages = db.query(Message).filter(
                    Message.touchpoint_id == latest_touchpoint.id
                ).order_by(Message.created_at.desc(), Message.variant).limit(3).all()
                
                if messages:
                    f.write("**Generated Follow-ups:**\n\n")
                    for msg in messages:
                        f.write(f"**Variant {msg.variant}** _{msg.tone}_:\n")
                        f.write(f"{msg.body}\n\n")
                    f.write(f"*Generated: {format_datetime(messages[0].created_at)}*\n\n")
            else:
                f.write("*No contexts added yet.*\n\n")
            
            # Notes
            if contact.notes:
                f.write("**Notes:**\n")
                f.write(f"{contact.notes}\n\n")
            
            f.write("---\n\n")
    
    return str(output_path)


def export_touchpoints_summary(db: Session, contact_id: Optional[int] = None, 
                              output_path: Optional[str] = None) -> str:
    """Export touchpoints summary with deduplication info."""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_contact_{contact_id}" if contact_id else "_all"
        output_path = get_reports_dir() / f"touchpoints{suffix}_{timestamp}.csv"
    
    # Build query
    query = db.query(Touchpoint)
    if contact_id:
        query = query.filter(Touchpoint.contact_id == contact_id)
    
    touchpoints = query.order_by(Touchpoint.contact_id, Touchpoint.created_at).all()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'contact_id', 'contact_name', 'context_preview', 
            'is_canonical', 'similarity_group', 'created_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for tp in touchpoints:
            writer.writerow({
                'contact_id': tp.contact_id,
                'contact_name': tp.contact.name,
                'context_preview': truncate_text(tp.context, 100),
                'is_canonical': 'Yes' if tp.is_canonical else 'No',
                'similarity_group': tp.similarity_group or '',
                'created_at': format_datetime(tp.created_at)
            })
    
    return str(output_path)


def get_export_stats(db: Session) -> Dict[str, int]:
    """Get summary statistics for export."""
    stats = {}
    
    stats['total_contacts'] = db.query(Contact).count()
    stats['total_touchpoints'] = db.query(Touchpoint).count()
    stats['canonical_touchpoints'] = db.query(Touchpoint).filter(Touchpoint.is_canonical == 1).count()
    stats['total_messages'] = db.query(Message).count()
    
    # Contacts with messages
    contacts_with_messages = db.query(Contact.id).join(Message).distinct().count()
    stats['contacts_with_messages'] = contacts_with_messages
    
    return stats