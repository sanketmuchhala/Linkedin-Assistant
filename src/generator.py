import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from .models import Contact, Touchpoint, Message
from .normalizer import normalize_text

# Load environment variables
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "none")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "450"))

# Load templates
TEMPLATES_PATH = Path(__file__).parent / "templates" / "followups.yaml"

def load_templates() -> Dict[str, List[str]]:
    """Load message templates from YAML file."""
    try:
        with open(TEMPLATES_PATH, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading templates: {e}")
        return {
            "friendly": [
                "Hi {name}, following up from {how_we_met}. Would love to {ask}?"
            ]
        }


def extract_context_elements(context: str) -> Dict[str, str]:
    """
    Extract key elements from the context text.
    
    This is a simple implementation that tries to identify:
    - How we met
    - Why now
    - Context summary
    """
    context_lower = context.lower()
    
    # Simple patterns to extract information
    how_we_met = "our connection"
    why_now = "I thought this might be relevant"
    context_summary = "your work"
    
    # Look for meeting patterns
    meeting_patterns = [
        r"met at (.+?)(?:\.|,|$)",
        r"connected at (.+?)(?:\.|,|$)", 
        r"saw you at (.+?)(?:\.|,|$)",
        r"talked at (.+?)(?:\.|,|$)"
    ]
    
    for pattern in meeting_patterns:
        match = re.search(pattern, context_lower)
        if match:
            how_we_met = match.group(1).strip()
            break
    
    # Look for urgency/timing patterns
    timing_patterns = [
        r"(launching|starting|building|working on) (.+?)(?:\.|,|$)",
        r"(need|looking for|hiring for) (.+?)(?:\.|,|$)",
        r"(planning|considering) (.+?)(?:\.|,|$)"
    ]
    
    for pattern in timing_patterns:
        match = re.search(pattern, context_lower)
        if match:
            why_now = f"I saw you're {match.group(1)} {match.group(2)}"
            break
    
    # Extract main topic/summary (first 30 chars or until punctuation)
    summary_match = re.match(r"([^.!?]{1,30})", context.strip())
    if summary_match:
        context_summary = summary_match.group(1).strip()
    
    return {
        "how_we_met": how_we_met,
        "why_now": why_now,
        "context_summary": context_summary
    }


def build_context(contact: Contact, touchpoint: Touchpoint, ask: str = "a quick 15-min call") -> Dict[str, str]:
    """Build context dictionary for template rendering."""
    context_elements = extract_context_elements(touchpoint.context)
    
    return {
        "name": contact.name.split()[0],  # First name only
        "company": contact.company or "your company",
        "role": contact.role or "your role",
        "how_we_met": context_elements["how_we_met"],
        "why_now": context_elements["why_now"],
        "context_summary": context_elements["context_summary"],
        "ask": ask
    }


def render_template(template: str, context: Dict[str, str]) -> str:
    """Render a template with the given context."""
    try:
        return template.format(**context)
    except KeyError as e:
        print(f"Missing template variable: {e}")
        return template


def truncate_message(message: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """Truncate message to max length, preserving word boundaries."""
    if len(message) <= max_length:
        return message
    
    # Find the last space before max_length
    truncated = message[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return message[:last_space] + "..."
    else:
        return message[:max_length-3] + "..."


def refine_with_llm(message: str, tone: str) -> str:
    """Refine message using LLM if available."""
    if MODEL_PROVIDER == "none":
        return message
    
    try:
        if MODEL_PROVIDER == "openai":
            return refine_with_openai(message, tone)
        elif MODEL_PROVIDER == "anthropic":
            return refine_with_anthropic(message, tone)
    except Exception as e:
        print(f"LLM refinement failed: {e}")
    
    return message


def refine_with_openai(message: str, tone: str) -> str:
    """Refine message using OpenAI."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""Refine this LinkedIn follow-up message to be more {tone} and professional:

Original: {message}

Requirements:
- 2-3 sentences maximum
- Under 450 characters
- No excessive flattery
- Single clear ask
- American business tone
- Keep it natural and authentic

Refined message:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        refined = response.choices[0].message.content.strip()
        return truncate_message(refined)
        
    except Exception as e:
        print(f"OpenAI refinement error: {e}")
        return message


def refine_with_anthropic(message: str, tone: str) -> str:
    """Refine message using Anthropic."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        prompt = f"""Refine this LinkedIn follow-up message to be more {tone} and professional:

Original: {message}

Requirements:
- 2-3 sentences maximum  
- Under 450 characters
- No excessive flattery
- Single clear ask
- American business tone
- Keep it natural and authentic

Refined message:"""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        
        refined = response.content[0].text.strip()
        return truncate_message(refined)
        
    except Exception as e:
        print(f"Anthropic refinement error: {e}")
        return message


def generate_variants(db: Session, contact: Contact, touchpoint: Touchpoint, 
                     tone: str = "friendly", ask: str = "a quick 15-min call", n: int = 3) -> List[Message]:
    """
    Generate n message variants for the given contact and touchpoint.
    
    Returns list of Message objects (not yet committed to DB).
    """
    templates = load_templates()
    tone_templates = templates.get(tone, templates.get("friendly", []))
    
    if not tone_templates:
        raise ValueError(f"No templates found for tone: {tone}")
    
    # Build context for rendering
    context = build_context(contact, touchpoint, ask)
    
    messages = []
    
    # Generate variants (cycle through templates if we need more than available)
    for i in range(n):
        template_idx = i % len(tone_templates)
        template = tone_templates[template_idx]
        
        # Render template
        rendered = render_template(template, context)
        
        # Refine with LLM if available
        refined = refine_with_llm(rendered, tone)
        
        # Truncate to max length
        final_message = truncate_message(refined)
        
        # Create Message object
        message = Message(
            contact_id=contact.id,
            touchpoint_id=touchpoint.id,
            variant=i + 1,
            body=final_message,
            tone=tone
        )
        
        messages.append(message)
    
    return messages


def save_messages(db: Session, messages: List[Message]) -> List[Message]:
    """Save messages to the database."""
    for message in messages:
        db.add(message)
    
    db.commit()
    
    # Refresh to get IDs
    for message in messages:
        db.refresh(message)
    
    return messages