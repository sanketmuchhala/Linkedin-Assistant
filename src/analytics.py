from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json
from .models import Contact, Message, OutreachAnalytics


class LinkedInAnalytics:
    """Premium LinkedIn analytics and insights."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics."""
        # Basic counts
        total_contacts = self.db.query(Contact).count()
        contacts_contacted = self.db.query(Contact).filter(Contact.message_sent == 1).count()
        contacts_responded = self.db.query(Contact).filter(Contact.response_received == 1).count()
        total_messages = self.db.query(Message).count()
        
        # Calculate rates
        contact_rate = (contacts_contacted / total_contacts * 100) if total_contacts > 0 else 0
        response_rate = (contacts_responded / contacts_contacted * 100) if contacts_contacted > 0 else 0
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_contacts = self.db.query(Contact).filter(Contact.created_at >= week_ago).count()
        recent_messages = self.db.query(Contact).filter(Contact.last_message_date >= week_ago).count()
        
        # Industry breakdown
        industry_stats = self._get_industry_breakdown()
        
        # Top performing tones
        tone_performance = self._get_tone_performance()
        
        # Outreach pipeline
        pipeline_stats = self._get_pipeline_stats()
        
        return {
            "overview": {
                "total_contacts": total_contacts,
                "contacts_contacted": contacts_contacted,
                "contacts_responded": contacts_responded,
                "total_messages": total_messages,
                "contact_rate": round(contact_rate, 1),
                "response_rate": round(response_rate, 1)
            },
            "recent_activity": {
                "new_contacts_week": recent_contacts,
                "messages_sent_week": recent_messages
            },
            "industry_breakdown": industry_stats,
            "tone_performance": tone_performance,
            "pipeline": pipeline_stats,
            "recommendations": self._get_recommendations()
        }
    
    def _get_industry_breakdown(self) -> List[Dict[str, Any]]:
        """Get breakdown of contacts by industry."""
        industries = self.db.query(
            Contact.industry,
            func.count(Contact.id).label('count'),
            func.avg(Contact.connection_strength).label('avg_strength'),
            func.sum(Contact.response_received).label('responses')
        ).filter(Contact.industry.isnot(None)).group_by(Contact.industry).all()
        
        return [
            {
                "industry": industry or "Unknown",
                "count": count,
                "avg_strength": round(avg_strength or 0, 1),
                "response_rate": round((responses / count * 100) if count > 0 else 0, 1)
            }
            for industry, count, avg_strength, responses in industries
        ]
    
    def _get_tone_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics by message tone."""
        # Get message tones with response rates
        tone_stats = self.db.query(
            Message.tone,
            func.count(Message.id).label('total_messages'),
            func.sum(Message.response_received).label('responses'),
            func.avg(func.length(Message.body)).label('avg_length')
        ).group_by(Message.tone).all()
        
        return [
            {
                "tone": tone,
                "total_messages": total,
                "responses": responses or 0,
                "response_rate": round((responses / total * 100) if total > 0 and responses else 0, 1),
                "avg_length": round(avg_length or 0)
            }
            for tone, total, responses, avg_length in tone_stats
        ]
    
    def _get_pipeline_stats(self) -> Dict[str, int]:
        """Get outreach pipeline statistics."""
        pipeline = {}
        
        # Count contacts by outreach status
        statuses = ['pending', 'contacted', 'responded', 'connected', 'closed']
        for status in statuses:
            count = self.db.query(Contact).filter(Contact.outreach_status == status).count()
            pipeline[status] = count
        
        return pipeline
    
    def _get_recommendations(self) -> List[str]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        # Analyze response rates by tone
        tone_performance = self._get_tone_performance()
        if tone_performance:
            best_tone = max(tone_performance, key=lambda x: x['response_rate'])
            if best_tone['response_rate'] > 0:
                recommendations.append(f"Your '{best_tone['tone']}' tone has the best response rate ({best_tone['response_rate']}%). Consider using it more often.")
        
        # Check for pending follow-ups
        pending_followups = self.db.query(Contact).filter(
            and_(
                Contact.message_sent == 1,
                Contact.response_received == 0,
                Contact.last_message_date < datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        if pending_followups > 0:
            recommendations.append(f"You have {pending_followups} contacts who haven't responded in over a week. Consider sending follow-up messages.")
        
        # Industry insights
        industry_stats = self._get_industry_breakdown()
        if industry_stats:
            best_industry = max(industry_stats, key=lambda x: x['response_rate'])
            if best_industry['response_rate'] > 0:
                recommendations.append(f"Contacts in {best_industry['industry']} have your highest response rate ({best_industry['response_rate']}%). Focus on this industry.")
        
        # Weekly activity recommendation
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = self.db.query(Contact).filter(Contact.last_message_date >= week_ago).count()
        if recent_activity < 5:
            recommendations.append("Consider reaching out to more contacts this week. Aim for 5-10 new connections.")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_contact_insights(self, contact_id: int) -> Dict[str, Any]:
        """Get detailed insights for a specific contact."""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            return {}
        
        # Get all messages for this contact
        messages = self.db.query(Message).filter(Message.contact_id == contact_id).all()
        
        # Calculate insights
        total_messages = len(messages)
        avg_message_length = sum(len(msg.body) for msg in messages) / total_messages if total_messages > 0 else 0
        
        # Days since last contact
        days_since_contact = None
        if contact.last_message_date:
            days_since_contact = (datetime.utcnow() - contact.last_message_date).days
        
        # Generate recommendations for this contact
        contact_recommendations = []
        
        if days_since_contact and days_since_contact > 14 and not contact.response_received:
            contact_recommendations.append("It's been over 2 weeks since your last message. Consider a different approach or timing.")
        
        if contact.connection_strength < 3:
            contact_recommendations.append("Low connection strength. Try engaging with their content before messaging.")
        
        if not contact.industry:
            contact_recommendations.append("Add industry information to get better message personalization.")
        
        return {
            "contact": {
                "name": contact.name,
                "company": contact.company,
                "connection_strength": contact.connection_strength,
                "outreach_status": contact.outreach_status,
                "response_received": bool(contact.response_received)
            },
            "message_stats": {
                "total_messages": total_messages,
                "avg_length": round(avg_message_length),
                "days_since_contact": days_since_contact
            },
            "recommendations": contact_recommendations
        }
    
    def track_message_performance(self, message_id: int, was_sent: bool = True, response_received: bool = False, response_time_hours: int = None):
        """Track performance of a specific message."""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.was_sent = 1 if was_sent else 0
            message.sent_date = datetime.utcnow() if was_sent else None
            message.response_received = 1 if response_received else 0
            message.response_time_hours = response_time_hours
            message.message_length = len(message.body)
            
            self.db.commit()
    
    def update_daily_analytics(self):
        """Update daily analytics summary."""
        today = datetime.utcnow().date()
        
        # Check if today's analytics already exist
        existing = self.db.query(OutreachAnalytics).filter(
            func.date(OutreachAnalytics.date) == today
        ).first()
        
        if existing:
            return existing
        
        # Calculate today's metrics
        contacts_added = self.db.query(Contact).filter(
            func.date(Contact.created_at) == today
        ).count()
        
        messages_generated = self.db.query(Message).filter(
            func.date(Message.created_at) == today
        ).count()
        
        messages_sent = self.db.query(Contact).filter(
            func.date(Contact.last_message_date) == today
        ).count()
        
        responses_received = self.db.query(Contact).filter(
            and_(
                Contact.response_received == 1,
                func.date(Contact.response_date) == today
            )
        ).count()
        
        # Calculate rates
        total_contacted = self.db.query(Contact).filter(Contact.message_sent == 1).count()
        total_responded = self.db.query(Contact).filter(Contact.response_received == 1).count()
        
        response_rate = (total_responded / total_contacted * 100) if total_contacted > 0 else 0
        
        # Create new analytics record
        analytics = OutreachAnalytics(
            date=datetime.utcnow(),
            contacts_added=contacts_added,
            messages_generated=messages_generated,
            messages_sent=messages_sent,
            responses_received=responses_received,
            response_rate=round(response_rate)
        )
        
        self.db.add(analytics)
        self.db.commit()
        return analytics