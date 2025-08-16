from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import Contact, Message
from .generator import generate_variants, save_messages


class FollowUpSequencer:
    """Automated follow-up sequence management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_pending_followups(self, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """Get contacts that need follow-up messages."""
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        contacts_needing_followup = self.db.query(Contact).filter(
            and_(
                Contact.message_sent == 1,
                Contact.response_received == 0,
                Contact.last_message_date < threshold_date,
                Contact.outreach_status.in_(['contacted', 'pending'])
            )
        ).all()
        
        followup_list = []
        for contact in contacts_needing_followup:
            days_since_contact = (datetime.utcnow() - contact.last_message_date).days
            priority = self._calculate_followup_priority(contact, days_since_contact)
            
            followup_list.append({
                "contact_id": contact.id,
                "name": contact.name,
                "company": contact.company,
                "days_since_contact": days_since_contact,
                "priority": priority,
                "suggested_action": self._get_suggested_action(contact, days_since_contact),
                "next_message_tone": self._suggest_next_tone(contact)
            })
        
        # Sort by priority (high priority first)
        return sorted(followup_list, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
    
    def _calculate_followup_priority(self, contact: Contact, days_since_contact: int) -> str:
        """Calculate follow-up priority based on various factors."""
        score = 0
        
        # Time urgency
        if days_since_contact >= 14:
            score += 3
        elif days_since_contact >= 10:
            score += 2
        elif days_since_contact >= 7:
            score += 1
        
        # Connection strength
        score += contact.connection_strength or 1
        
        # Company importance (could be enhanced with a company scoring system)
        if contact.company and any(keyword in contact.company.lower() for keyword in ['google', 'microsoft', 'amazon', 'apple', 'meta']):
            score += 2
        
        # Priority level set by user
        if contact.priority_level == 'high':
            score += 3
        elif contact.priority_level == 'medium':
            score += 1
        
        # Request reason importance
        if contact.request_reason and any(keyword in contact.request_reason.lower() for keyword in ['referral', 'job', 'opportunity', 'hiring']):
            score += 2
        
        if score >= 7:
            return "high"
        elif score >= 4:
            return "medium"
        else:
            return "low"
    
    def _get_suggested_action(self, contact: Contact, days_since_contact: int) -> str:
        """Get suggested follow-up action based on context."""
        if days_since_contact >= 21:
            return "final_followup"
        elif days_since_contact >= 14:
            return "value_add_message"
        elif days_since_contact >= 10:
            return "soft_reminder"
        else:
            return "gentle_followup"
    
    def _suggest_next_tone(self, contact: Contact) -> str:
        """Suggest the next message tone based on previous messages."""
        # Get previous message tones for this contact
        previous_messages = self.db.query(Message).filter(
            Message.contact_id == contact.id
        ).order_by(Message.created_at.desc()).limit(3).all()
        
        previous_tones = [msg.tone for msg in previous_messages]
        
        # Suggest progression: friendly -> warm -> direct
        if not previous_tones:
            return "friendly"
        elif "friendly" in previous_tones and "warm" not in previous_tones:
            return "warm"
        elif "warm" in previous_tones and "direct" not in previous_tones:
            return "direct"
        else:
            return "formal"  # Final attempt
    
    def generate_followup_message(self, contact_id: int, message_type: str = "gentle_followup") -> List[Message]:
        """Generate follow-up message based on type."""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            return []
        
        # Get latest touchpoint
        from .models import Touchpoint
        touchpoint = self.db.query(Touchpoint).filter(
            Touchpoint.contact_id == contact_id,
            Touchpoint.is_canonical == 1
        ).order_by(Touchpoint.created_at.desc()).first()
        
        if not touchpoint:
            return []
        
        # Customize ask based on message type
        ask_mapping = {
            "gentle_followup": "a quick follow-up call",
            "soft_reminder": "a brief check-in",
            "value_add_message": "to share some insights that might help",
            "final_followup": "one final conversation"
        }
        
        tone = self._suggest_next_tone(contact)
        ask = ask_mapping.get(message_type, "a quick call")
        
        # Generate messages
        messages = generate_variants(self.db, contact, touchpoint, tone, ask, n=3)
        return save_messages(self.db, messages)
    
    def schedule_followup(self, contact_id: int, follow_up_date: datetime) -> bool:
        """Schedule a follow-up for a specific date."""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            contact.follow_up_scheduled = follow_up_date
            self.db.commit()
            return True
        return False
    
    def get_scheduled_followups(self, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get contacts scheduled for follow-up on a specific date."""
        if not date:
            date = datetime.utcnow().date()
        
        scheduled_contacts = self.db.query(Contact).filter(
            and_(
                Contact.follow_up_scheduled.isnot(None),
                Contact.follow_up_scheduled >= date,
                Contact.follow_up_scheduled < date + timedelta(days=1)
            )
        ).all()
        
        return [
            {
                "contact_id": contact.id,
                "name": contact.name,
                "company": contact.company,
                "scheduled_time": contact.follow_up_scheduled,
                "priority": contact.priority_level,
                "reason": contact.request_reason
            }
            for contact in scheduled_contacts
        ]
    
    def auto_update_outreach_status(self):
        """Automatically update outreach status based on time elapsed."""
        # Mark as "stale" if no response after 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        stale_contacts = self.db.query(Contact).filter(
            and_(
                Contact.message_sent == 1,
                Contact.response_received == 0,
                Contact.last_message_date < thirty_days_ago,
                Contact.outreach_status == 'contacted'
            )
        ).all()
        
        for contact in stale_contacts:
            contact.outreach_status = 'closed'
        
        self.db.commit()
        return len(stale_contacts)


class ConnectionScorer:
    """Advanced connection strength and engagement scoring."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_connection_strength(self, contact: Contact) -> int:
        """Calculate connection strength score (1-5)."""
        score = 1  # Base score
        
        # Mutual connections boost
        if contact.mutual_connections:
            if contact.mutual_connections >= 10:
                score += 2
            elif contact.mutual_connections >= 5:
                score += 1
        
        # Response history
        if contact.response_received:
            score += 2
        
        # Profile completeness
        profile_completeness = sum([
            1 if contact.company else 0,
            1 if contact.role else 0,
            1 if contact.linkedin_url else 0,
            1 if contact.industry else 0,
            1 if contact.location else 0
        ])
        score += min(profile_completeness // 2, 1)
        
        # Recent activity
        if contact.last_activity and contact.last_activity > datetime.utcnow() - timedelta(days=30):
            score += 1
        
        return min(score, 5)  # Cap at 5
    
    def update_all_connection_scores(self) -> int:
        """Update connection strength for all contacts."""
        contacts = self.db.query(Contact).all()
        updated_count = 0
        
        for contact in contacts:
            new_score = self.calculate_connection_strength(contact)
            if contact.connection_strength != new_score:
                contact.connection_strength = new_score
                updated_count += 1
        
        self.db.commit()
        return updated_count
    
    def get_high_value_contacts(self, min_score: int = 4) -> List[Dict[str, Any]]:
        """Get contacts with high connection strength."""
        high_value_contacts = self.db.query(Contact).filter(
            Contact.connection_strength >= min_score
        ).order_by(Contact.connection_strength.desc()).all()
        
        return [
            {
                "contact_id": contact.id,
                "name": contact.name,
                "company": contact.company,
                "connection_strength": contact.connection_strength,
                "outreach_status": contact.outreach_status,
                "mutual_connections": contact.mutual_connections,
                "response_received": bool(contact.response_received)
            }
            for contact in high_value_contacts
        ]


class IndustryInsights:
    """Industry and role-based insights and analytics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_industry_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics by industry."""
        # This would be enhanced with actual industry data
        industries = {}
        contacts = self.db.query(Contact).all()
        
        for contact in contacts:
            industry = contact.industry or "Unknown"
            if industry not in industries:
                industries[industry] = {
                    "total_contacts": 0,
                    "messages_sent": 0,
                    "responses_received": 0,
                    "avg_connection_strength": 0,
                    "top_companies": set()
                }
            
            industries[industry]["total_contacts"] += 1
            if contact.message_sent:
                industries[industry]["messages_sent"] += 1
            if contact.response_received:
                industries[industry]["responses_received"] += 1
            industries[industry]["avg_connection_strength"] += contact.connection_strength or 1
            if contact.company:
                industries[industry]["top_companies"].add(contact.company)
        
        # Calculate rates and averages
        result = []
        for industry, data in industries.items():
            total = data["total_contacts"]
            result.append({
                "industry": industry,
                "total_contacts": total,
                "response_rate": round((data["responses_received"] / data["messages_sent"] * 100) if data["messages_sent"] > 0 else 0, 1),
                "contact_rate": round((data["messages_sent"] / total * 100) if total > 0 else 0, 1),
                "avg_connection_strength": round(data["avg_connection_strength"] / total, 1) if total > 0 else 0,
                "top_companies": list(data["top_companies"])[:5]
            })
        
        return sorted(result, key=lambda x: x["response_rate"], reverse=True)
    
    def get_role_insights(self) -> List[Dict[str, Any]]:
        """Get insights by job role/title."""
        roles = {}
        contacts = self.db.query(Contact).all()
        
        for contact in contacts:
            role = contact.role or "Unknown"
            # Normalize role titles
            role_keywords = self._extract_role_keywords(role)
            
            for keyword in role_keywords:
                if keyword not in roles:
                    roles[keyword] = {
                        "contacts": [],
                        "response_rate": 0,
                        "avg_connection_strength": 0
                    }
                roles[keyword]["contacts"].append(contact)
        
        # Calculate metrics
        result = []
        for role, data in roles.items():
            contacts = data["contacts"]
            total = len(contacts)
            if total >= 2:  # Only include roles with 2+ contacts
                responses = sum(1 for c in contacts if c.response_received)
                messages_sent = sum(1 for c in contacts if c.message_sent)
                avg_strength = sum(c.connection_strength or 1 for c in contacts) / total
                
                result.append({
                    "role": role,
                    "total_contacts": total,
                    "response_rate": round((responses / messages_sent * 100) if messages_sent > 0 else 0, 1),
                    "avg_connection_strength": round(avg_strength, 1)
                })
        
        return sorted(result, key=lambda x: x["total_contacts"], reverse=True)[:10]
    
    def _extract_role_keywords(self, role: str) -> List[str]:
        """Extract meaningful keywords from job titles."""
        if not role:
            return ["Unknown"]
        
        role_lower = role.lower()
        keywords = []
        
        # Common role patterns
        role_patterns = {
            "engineer": ["engineer", "engineering"],
            "manager": ["manager", "management"],
            "director": ["director"],
            "vp": ["vp", "vice president"],
            "ceo": ["ceo", "chief executive"],
            "cto": ["cto", "chief technology"],
            "data": ["data scientist", "data analyst", "data engineer"],
            "product": ["product manager", "product owner"],
            "software": ["software engineer", "software developer"],
            "senior": ["senior", "sr."],
            "lead": ["lead", "principal"]
        }
        
        for category, patterns in role_patterns.items():
            if any(pattern in role_lower for pattern in patterns):
                keywords.append(category.title())
        
        return keywords if keywords else [role.title()]