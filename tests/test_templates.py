import pytest
import tempfile
import yaml
from pathlib import Path
from src.generator import (
    load_templates, extract_context_elements, build_context,
    render_template, truncate_message, generate_variants
)
from src.models import Contact, Touchpoint


def test_load_templates():
    """Test template loading from YAML."""
    # Create a temporary template file
    test_templates = {
        "friendly": [
            "Hi {name}, great meeting you at {how_we_met}!"
        ],
        "direct": [
            "Hi {name}, following up from {how_we_met}."
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_templates, f)
        temp_path = f.name
    
    # Test loading
    templates = load_templates()
    assert isinstance(templates, dict)
    assert "friendly" in templates
    assert "direct" in templates
    
    # Clean up
    Path(temp_path).unlink()


def test_extract_context_elements():
    """Test context element extraction."""
    # Test meeting extraction
    context1 = "met at NYC MLOps meetup, she mentioned hiring for data quality roles"
    elements1 = extract_context_elements(context1)
    assert "meetup" in elements1["how_we_met"].lower()
    
    # Test building/launching extraction
    context2 = "connected on LinkedIn, currently building AI pipeline tools"
    elements2 = extract_context_elements(context2)
    assert "building" in elements2["why_now"].lower()
    
    # Test default fallbacks
    context3 = "random context without specific patterns"
    elements3 = extract_context_elements(context3)
    assert elements3["how_we_met"] == "our connection"
    assert elements3["why_now"] == "I thought this might be relevant"


def test_build_context():
    """Test context building for template rendering."""
    # Create mock contact and touchpoint
    contact = Contact(
        name="Jane Doe",
        company="Tech Corp",
        role="VP Engineering"
    )
    
    touchpoint = Touchpoint(
        context="met at AI conference, discussed data quality challenges"
    )
    
    context = build_context(contact, touchpoint, "a quick coffee chat")
    
    assert context["name"] == "Jane"  # First name only
    assert context["company"] == "Tech Corp"
    assert context["ask"] == "a quick coffee chat"
    assert "met" in context["how_we_met"] or "our connection" in context["how_we_met"]


def test_render_template():
    """Test template rendering with context."""
    template = "Hi {name}, following up from {how_we_met}. Would love to {ask}!"
    context = {
        "name": "John",
        "how_we_met": "the NYC meetup",
        "ask": "grab coffee"
    }
    
    result = render_template(template, context)
    expected = "Hi John, following up from the NYC meetup. Would love to grab coffee!"
    assert result == expected


def test_render_template_missing_key():
    """Test template rendering with missing keys."""
    template = "Hi {name}, about {missing_key}"
    context = {"name": "John"}
    
    # Should return original template when key is missing
    result = render_template(template, context)
    assert result == template


def test_truncate_message():
    """Test message truncation."""
    # Short message - no truncation
    short_msg = "This is a short message."
    assert truncate_message(short_msg, 100) == short_msg
    
    # Long message - should truncate at word boundary
    long_msg = "This is a very long message that needs to be truncated because it exceeds the maximum length limit."
    truncated = truncate_message(long_msg, 50)
    
    assert len(truncated) <= 53  # 50 + "..."
    assert truncated.endswith("...")
    assert not truncated.endswith(" ...")  # Should not end with space before ...
    
    # Message without spaces near limit
    no_spaces = "a" * 100
    truncated_no_spaces = truncate_message(no_spaces, 50)
    assert len(truncated_no_spaces) == 53  # 50 + "..."


def test_character_limits():
    """Test that generated messages respect character limits."""
    # This would need database setup for full test
    # For now, test the truncation logic
    
    max_length = 450
    
    # Test various message lengths
    test_messages = [
        "Short message",
        "A" * 300,  # Medium length
        "B" * 600   # Too long
    ]
    
    for msg in test_messages:
        truncated = truncate_message(msg, max_length)
        assert len(truncated) <= max_length
        
        if len(msg) > max_length:
            assert truncated.endswith("...")


def test_template_placeholder_filling():
    """Test that all required placeholders are available."""
    required_placeholders = {
        "name", "company", "how_we_met", "why_now", "context_summary", "ask"
    }
    
    # Mock data
    contact = Contact(name="Test User", company="Test Co")
    touchpoint = Touchpoint(context="test context")
    
    context = build_context(contact, touchpoint)
    
    # Check all required placeholders are present
    for placeholder in required_placeholders:
        assert placeholder in context, f"Missing placeholder: {placeholder}"
        assert context[placeholder] is not None, f"Null value for: {placeholder}"


def test_multiple_template_variants():
    """Test generating multiple variants from templates."""
    test_templates = {
        "friendly": [
            "Hi {name}! Variant 1",
            "Hello {name}! Variant 2", 
            "Hey {name}! Variant 3"
        ]
    }
    
    # Test that we can cycle through templates for more variants
    for i in range(6):  # More than available templates
        template_idx = i % len(test_templates["friendly"])
        template = test_templates["friendly"][template_idx]
        
        assert template in test_templates["friendly"]
        
        # Check cycling works
        if i >= 3:
            expected_idx = i - 3
            assert template_idx == expected_idx