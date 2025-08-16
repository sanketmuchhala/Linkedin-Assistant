import os
from datetime import datetime
from typing import Optional
from pathlib import Path

def ensure_dir(path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def parse_tags(tags_str: Optional[str]) -> list:
    """Parse comma-separated tags string."""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


def format_tags(tags: list) -> str:
    """Format tags list as comma-separated string."""
    return ", ".join(tags) if tags else ""


def validate_url(url: str) -> bool:
    """Basic URL validation."""
    if not url:
        return False
    return url.startswith(("http://", "https://", "linkedin.com", "www.linkedin.com"))


def clean_linkedin_url(url: str) -> str:
    """Clean and normalize LinkedIn URL."""
    if not url:
        return ""
    
    # Remove trailing slashes and query parameters
    url = url.rstrip("/").split("?")[0]
    
    # Ensure https://
    if url.startswith("linkedin.com") or url.startswith("www.linkedin.com"):
        url = "https://" + url
    elif not url.startswith("http"):
        url = "https://linkedin.com/in/" + url
    
    return url


def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent / "data"


def get_reports_dir() -> Path:
    """Get the reports directory path."""
    reports_dir = Path("./reports")
    ensure_dir(str(reports_dir))
    return reports_dir