#!/usr/bin/env python3
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .db import DatabaseManager, init_db, get_or_create_contact
from .models import Contact, Touchpoint, Message
from .dedupe import create_or_merge_touchpoint, merge_duplicate_touchpoints
from .generator import generate_variants, save_messages
from .reports.export import export_contacts_csv, export_contacts_markdown, export_touchpoints_summary, get_export_stats
from .utils import clean_linkedin_url, parse_tags, format_tags, format_datetime, truncate_text

app = typer.Typer(help="LinkedIn Follow-Up Assistant - Generate tailored follow-up messages")
console = Console()

@app.callback()
def main():
    """LinkedIn Follow-Up Assistant CLI"""
    # Initialize database on first run
    if not init_db():
        rprint("[red]Error: Could not initialize database[/red]")
        raise typer.Exit(1)


@app.command()
def add_contact(
    name: str = typer.Option(..., "--name", "-n", help="Contact's full name"),
    company: Optional[str] = typer.Option(None, "--company", "-c", help="Company name"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Job title/role"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="LinkedIn URL"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    notes: Optional[str] = typer.Option(None, "--notes", help="Additional notes")
):
    """Add or update a contact."""
    with DatabaseManager() as db:
        try:
            # Get or create contact
            contact = get_or_create_contact(db, name, company)
            
            # Update fields if provided
            if role:
                contact.role = role
            if url:
                contact.linkedin_url = clean_linkedin_url(url)
            if tags:
                contact.tags = tags
            if notes:
                contact.notes = notes
            
            db.add(contact)
            db.commit()
            db.refresh(contact)
            
            rprint(f"[green]✓[/green] Contact saved: {contact.name} (ID: {contact.id})")
            if company:
                rprint(f"  Company: {company}")
            if role:
                rprint(f"  Role: {role}")
            
        except Exception as e:
            rprint(f"[red]Error adding contact: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def add_context(
    contact: str = typer.Option(..., "--contact", "-c", help="Contact name"),
    text: str = typer.Option(..., "--text", "-t", help="Context/reason text"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name (if multiple contacts with same name)")
):
    """Add context/reason for connecting with a contact."""
    with DatabaseManager() as db:
        try:
            # Find contact
            query = db.query(Contact).filter(Contact.name == contact)
            if company:
                query = query.filter(Contact.company == company)
            
            contact_obj = query.first()
            if not contact_obj:
                rprint(f"[red]Contact not found: {contact}[/red]")
                raise typer.Exit(1)
            
            # Create or merge touchpoint
            touchpoint, was_merged = create_or_merge_touchpoint(db, contact_obj.id, text)
            
            if was_merged:
                rprint(f"[yellow]→[/yellow] Context grouped with existing touchpoint (ID: {touchpoint.id})")
                rprint(f"  Similarity group: {touchpoint.similarity_group}")
            else:
                rprint(f"[green]✓[/green] New context added (ID: {touchpoint.id})")
            
            rprint(f"  Contact: {contact_obj.name}")
            rprint(f"  Context: {truncate_text(text, 80)}")
            
        except Exception as e:
            rprint(f"[red]Error adding context: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def suggest(
    contact: str = typer.Option(..., "--contact", "-c", help="Contact name"),
    tone: str = typer.Option("friendly", "--tone", "-t", help="Message tone"),
    ask: str = typer.Option("a quick 15-min call", "--ask", "-a", help="What you're asking for"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name (if multiple contacts)"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save messages to database")
):
    """Generate follow-up message suggestions."""
    valid_tones = ["friendly", "direct", "formal", "warm", "playful", "short-n-sweet"]
    if tone not in valid_tones:
        rprint(f"[red]Invalid tone. Choose from: {', '.join(valid_tones)}[/red]")
        raise typer.Exit(1)
    
    with DatabaseManager() as db:
        try:
            # Find contact
            query = db.query(Contact).filter(Contact.name == contact)
            if company:
                query = query.filter(Contact.company == company)
            
            contact_obj = query.first()
            if not contact_obj:
                rprint(f"[red]Contact not found: {contact}[/red]")
                raise typer.Exit(1)
            
            # Get latest canonical touchpoint
            touchpoint = db.query(Touchpoint).filter(
                Touchpoint.contact_id == contact_obj.id,
                Touchpoint.is_canonical == 1
            ).order_by(Touchpoint.created_at.desc()).first()
            
            if not touchpoint:
                rprint(f"[red]No context found for {contact}. Add context first with 'add-context'.[/red]")
                raise typer.Exit(1)
            
            # Generate messages
            messages = generate_variants(db, contact_obj, touchpoint, tone, ask, n=3)
            
            # Save to database if requested
            if save:
                save_messages(db, messages)
                rprint(f"[green]✓[/green] Generated 3 follow-up variants (saved to database)")
            else:
                rprint(f"[green]✓[/green] Generated 3 follow-up variants")
            
            # Display messages
            rprint(f"\n[bold]Follow-up suggestions for {contact_obj.name}[/bold]")
            rprint(f"Tone: {tone} | Ask: {ask}")
            rprint(f"Context: {truncate_text(touchpoint.context, 80)}")
            
            for i, message in enumerate(messages, 1):
                panel = Panel(
                    message.body,
                    title=f"Variant {i} ({len(message.body)} chars)",
                    border_style="blue"
                )
                rprint(panel)
            
        except Exception as e:
            rprint(f"[red]Error generating suggestions: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def list(
    contact: Optional[str] = typer.Option(None, "--contact", "-c", help="Filter by contact name"),
    messages: bool = typer.Option(False, "--messages", help="Show messages instead of contacts"),
    touchpoints: bool = typer.Option(False, "--touchpoints", help="Show touchpoints instead of contacts"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results")
):
    """List contacts, touchpoints, or messages."""
    with DatabaseManager() as db:
        try:
            if messages:
                _list_messages(db, contact, limit)
            elif touchpoints:
                _list_touchpoints(db, contact, limit)
            else:
                _list_contacts(db, contact, limit)
                
        except Exception as e:
            rprint(f"[red]Error listing data: {e}[/red]")
            raise typer.Exit(1)


def _list_contacts(db, contact_filter: Optional[str], limit: int):
    """List contacts."""
    query = db.query(Contact)
    if contact_filter:
        query = query.filter(Contact.name.ilike(f"%{contact_filter}%"))
    
    contacts = query.order_by(Contact.updated_at.desc()).limit(limit).all()
    
    if not contacts:
        rprint("[yellow]No contacts found.[/yellow]")
        return
    
    table = Table(title=f"Contacts ({len(contacts)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Company")
    table.add_column("Role")
    table.add_column("Touchpoints", style="green")
    table.add_column("Messages", style="blue")
    table.add_column("Updated")
    
    for contact in contacts:
        touchpoint_count = len([tp for tp in contact.touchpoints if tp.is_canonical])
        message_count = len(contact.messages)
        
        table.add_row(
            str(contact.id),
            contact.name,
            contact.company or "-",
            contact.role or "-",
            str(touchpoint_count),
            str(message_count),
            format_datetime(contact.updated_at)
        )
    
    console.print(table)


def _list_touchpoints(db, contact_filter: Optional[str], limit: int):
    """List touchpoints."""
    query = db.query(Touchpoint).join(Contact)
    if contact_filter:
        query = query.filter(Contact.name.ilike(f"%{contact_filter}%"))
    
    touchpoints = query.order_by(Touchpoint.created_at.desc()).limit(limit).all()
    
    if not touchpoints:
        rprint("[yellow]No touchpoints found.[/yellow]")
        return
    
    table = Table(title=f"Touchpoints ({len(touchpoints)})")
    table.add_column("ID", style="cyan")
    table.add_column("Contact", style="bold")
    table.add_column("Context Preview")
    table.add_column("Canonical", style="green")
    table.add_column("Group")
    table.add_column("Created")
    
    for tp in touchpoints:
        table.add_row(
            str(tp.id),
            tp.contact.name,
            truncate_text(tp.context, 50),
            "Yes" if tp.is_canonical else "No",
            tp.similarity_group or "-",
            format_datetime(tp.created_at)
        )
    
    console.print(table)


def _list_messages(db, contact_filter: Optional[str], limit: int):
    """List messages."""
    query = db.query(Message).join(Contact)
    if contact_filter:
        query = query.filter(Contact.name.ilike(f"%{contact_filter}%"))
    
    messages = query.order_by(Message.created_at.desc()).limit(limit).all()
    
    if not messages:
        rprint("[yellow]No messages found.[/yellow]")
        return
    
    table = Table(title=f"Messages ({len(messages)})")
    table.add_column("ID", style="cyan")
    table.add_column("Contact", style="bold")
    table.add_column("Variant")
    table.add_column("Tone")
    table.add_column("Message Preview")
    table.add_column("Created")
    
    for msg in messages:
        table.add_row(
            str(msg.id),
            msg.contact.name,
            str(msg.variant),
            msg.tone,
            truncate_text(msg.body, 60),
            format_datetime(msg.created_at)
        )
    
    console.print(table)


@app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv or md"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Output file path"),
    touchpoints: bool = typer.Option(False, "--touchpoints", help="Export touchpoints instead of contacts"),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", help="Export touchpoints for specific contact ID")
):
    """Export data to CSV or Markdown."""
    valid_formats = ["csv", "md", "markdown"]
    if format not in valid_formats:
        rprint(f"[red]Invalid format. Choose from: csv, md[/red]")
        raise typer.Exit(1)
    
    with DatabaseManager() as db:
        try:
            if touchpoints:
                output_path = export_touchpoints_summary(db, contact_id, out)
                rprint(f"[green]✓[/green] Touchpoints exported to: {output_path}")
            else:
                if format in ["md", "markdown"]:
                    output_path = export_contacts_markdown(db, out)
                else:
                    output_path = export_contacts_csv(db, out)
                
                # Show stats
                stats = get_export_stats(db)
                rprint(f"[green]✓[/green] Contacts exported to: {output_path}")
                rprint(f"  {stats['total_contacts']} contacts, {stats['total_touchpoints']} touchpoints, {stats['total_messages']} messages")
            
        except Exception as e:
            rprint(f"[red]Error exporting data: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def merge_dupes(
    contact: str = typer.Option(..., "--contact", "-c", help="Contact name"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name (if multiple contacts)")
):
    """Find and merge duplicate touchpoints for a contact."""
    with DatabaseManager() as db:
        try:
            # Find contact
            query = db.query(Contact).filter(Contact.name == contact)
            if company:
                query = query.filter(Contact.company == company)
            
            contact_obj = query.first()
            if not contact_obj:
                rprint(f"[red]Contact not found: {contact}[/red]")
                raise typer.Exit(1)
            
            # Merge duplicates
            result = merge_duplicate_touchpoints(db, contact_obj.id)
            
            rprint(f"[green]✓[/green] Merge completed for {contact_obj.name}")
            rprint(f"  Total touchpoints: {result['total']}")
            rprint(f"  Merged duplicates: {result['merged']}")
            rprint(f"  Similarity groups: {result['groups']}")
            
            if result['merged'] > 0:
                rprint(f"[yellow]→[/yellow] {result['merged']} duplicate touchpoints were merged")
            else:
                rprint("[blue]ℹ[/blue] No duplicates found")
            
        except Exception as e:
            rprint(f"[red]Error merging duplicates: {e}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()