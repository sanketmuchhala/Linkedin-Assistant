import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typer.testing import CliRunner

from src.app import app
from src.models import Base, Contact, Touchpoint, Message
from src.db import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_file.close()
    
    # Set up database URL
    db_url = f"sqlite:///{temp_db_file.name}"
    
    # Create engine and tables
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    
    # Set environment variable for tests
    old_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = db_url
    
    yield db_url
    
    # Cleanup
    if old_db_url:
        os.environ["DATABASE_URL"] = old_db_url
    else:
        os.environ.pop("DATABASE_URL", None)
    
    Path(temp_db_file.name).unlink(missing_ok=True)


@pytest.fixture
def cli_runner():
    """Create CLI test runner."""
    return CliRunner()


def test_add_contact_basic(temp_db, cli_runner):
    """Test basic contact addition."""
    result = cli_runner.invoke(app, [
        "add-contact",
        "--name", "John Doe",
        "--company", "Tech Corp",
        "--role", "Engineer"
    ])
    
    assert result.exit_code == 0
    assert "Contact saved: John Doe" in result.stdout
    assert "Company: Tech Corp" in result.stdout


def test_add_contact_minimal(temp_db, cli_runner):
    """Test adding contact with minimal info."""
    result = cli_runner.invoke(app, [
        "add-contact",
        "--name", "Jane Smith"
    ])
    
    assert result.exit_code == 0
    assert "Contact saved: Jane Smith" in result.stdout


def test_add_contact_with_url_and_tags(temp_db, cli_runner):
    """Test adding contact with URL and tags."""
    result = cli_runner.invoke(app, [
        "add-contact",
        "--name", "Alice Johnson",
        "--company", "AI Startup",
        "--url", "linkedin.com/in/alice",
        "--tags", "ai,startup,hiring"
    ])
    
    assert result.exit_code == 0
    assert "Contact saved: Alice Johnson" in result.stdout


def test_add_context(temp_db, cli_runner):
    """Test adding context to a contact."""
    # First add a contact
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Bob Wilson",
        "--company", "Data Co"
    ])
    
    # Then add context
    result = cli_runner.invoke(app, [
        "add-context",
        "--contact", "Bob Wilson",
        "--text", "met at NYC MLOps meetup, discussed data quality challenges"
    ])
    
    assert result.exit_code == 0
    assert "New context added" in result.stdout or "Context grouped" in result.stdout
    assert "Contact: Bob Wilson" in result.stdout


def test_add_context_nonexistent_contact(temp_db, cli_runner):
    """Test adding context to non-existent contact."""
    result = cli_runner.invoke(app, [
        "add-context",
        "--contact", "Nobody",
        "--text", "some context"
    ])
    
    assert result.exit_code == 1
    assert "Contact not found" in result.stdout


def test_suggest_basic(temp_db, cli_runner):
    """Test basic suggestion generation."""
    # Add contact and context
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Charlie Brown",
        "--company", "Analytics Inc"
    ])
    
    cli_runner.invoke(app, [
        "add-context",
        "--contact", "Charlie Brown", 
        "--text", "connected at AI conference, building ML platform"
    ])
    
    # Generate suggestions
    result = cli_runner.invoke(app, [
        "suggest",
        "--contact", "Charlie Brown",
        "--tone", "friendly",
        "--ask", "a quick coffee chat"
    ])
    
    assert result.exit_code == 0
    assert "Generated 3 follow-up variants" in result.stdout
    assert "Follow-up suggestions for Charlie Brown" in result.stdout
    assert "Variant 1" in result.stdout
    assert "Variant 2" in result.stdout
    assert "Variant 3" in result.stdout


def test_suggest_no_context(temp_db, cli_runner):
    """Test suggestion generation without context."""
    # Add contact but no context
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Diana Prince"
    ])
    
    result = cli_runner.invoke(app, [
        "suggest",
        "--contact", "Diana Prince"
    ])
    
    assert result.exit_code == 1
    assert "No context found" in result.stdout


def test_suggest_invalid_tone(temp_db, cli_runner):
    """Test suggestion generation with invalid tone."""
    result = cli_runner.invoke(app, [
        "suggest",
        "--contact", "Anyone",
        "--tone", "invalid_tone"
    ])
    
    assert result.exit_code == 1
    assert "Invalid tone" in result.stdout


def test_list_contacts_empty(temp_db, cli_runner):
    """Test listing contacts when none exist."""
    result = cli_runner.invoke(app, ["list"])
    
    assert result.exit_code == 0
    assert "No contacts found" in result.stdout


def test_list_contacts(temp_db, cli_runner):
    """Test listing contacts."""
    # Add some contacts
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Contact One",
        "--company", "Company A"
    ])
    
    cli_runner.invoke(app, [
        "add-contact", 
        "--name", "Contact Two",
        "--company", "Company B"
    ])
    
    result = cli_runner.invoke(app, ["list"])
    
    assert result.exit_code == 0
    assert "Contacts (2)" in result.stdout
    assert "Contact One" in result.stdout
    assert "Contact Two" in result.stdout


def test_list_messages(temp_db, cli_runner):
    """Test listing messages."""
    # Add contact, context, and generate messages
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Message Test",
        "--company", "Test Co"
    ])
    
    cli_runner.invoke(app, [
        "add-context",
        "--contact", "Message Test",
        "--text", "test context for messages"
    ])
    
    cli_runner.invoke(app, [
        "suggest",
        "--contact", "Message Test"
    ])
    
    # List messages
    result = cli_runner.invoke(app, ["list", "--messages"])
    
    assert result.exit_code == 0
    assert "Messages" in result.stdout
    assert "Message Test" in result.stdout


def test_export_csv(temp_db, cli_runner):
    """Test CSV export."""
    # Add some test data
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Export Test",
        "--company", "Export Co"
    ])
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        temp_file = f.name
    
    result = cli_runner.invoke(app, [
        "export",
        "--format", "csv",
        "--out", temp_file
    ])
    
    assert result.exit_code == 0
    assert "exported to" in result.stdout
    
    # Check file exists and has content
    assert Path(temp_file).exists()
    content = Path(temp_file).read_text()
    assert "Export Test" in content
    
    # Cleanup
    Path(temp_file).unlink()


def test_merge_dupes(temp_db, cli_runner):
    """Test duplicate merging."""
    # Add contact
    cli_runner.invoke(app, [
        "add-contact",
        "--name", "Dupe Test",
        "--company", "Dupe Co"
    ])
    
    # Add similar contexts
    cli_runner.invoke(app, [
        "add-context",
        "--contact", "Dupe Test",
        "--text", "met at conference about AI"
    ])
    
    cli_runner.invoke(app, [
        "add-context", 
        "--contact", "Dupe Test",
        "--text", "talked at AI conference"
    ])
    
    # Merge duplicates
    result = cli_runner.invoke(app, [
        "merge-dupes",
        "--contact", "Dupe Test"
    ])
    
    assert result.exit_code == 0
    assert "Merge completed" in result.stdout


def test_full_workflow(temp_db, cli_runner):
    """Test complete workflow: add contact -> context -> suggest -> export."""
    # 1. Add contact
    result1 = cli_runner.invoke(app, [
        "add-contact",
        "--name", "Workflow Test",
        "--company", "Flow Corp",
        "--role", "CTO"
    ])
    assert result1.exit_code == 0
    
    # 2. Add context
    result2 = cli_runner.invoke(app, [
        "add-context",
        "--contact", "Workflow Test",
        "--text", "met at startup event, launching new AI product"
    ])
    assert result2.exit_code == 0
    
    # 3. Generate suggestions
    result3 = cli_runner.invoke(app, [
        "suggest",
        "--contact", "Workflow Test",
        "--tone", "warm",
        "--ask", "a brief call next week"
    ])
    assert result3.exit_code == 0
    assert "Generated 3 follow-up variants" in result3.stdout
    
    # 4. List to verify
    result4 = cli_runner.invoke(app, ["list"])
    assert result4.exit_code == 0
    assert "Workflow Test" in result4.stdout
    
    # 5. Export
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        temp_file = f.name
    
    result5 = cli_runner.invoke(app, [
        "export",
        "--format", "csv", 
        "--out", temp_file
    ])
    assert result5.exit_code == 0
    
    # Verify export content
    content = Path(temp_file).read_text()
    assert "Workflow Test" in content
    assert "Flow Corp" in content
    
    # Cleanup
    Path(temp_file).unlink()