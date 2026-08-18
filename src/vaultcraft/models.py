"""Pydantic models for VaultCraft."""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class NoteMetadata(BaseModel):
    """Metadata extracted from note frontmatter and content analysis."""
    title: str
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    outgoing_links: List[str] = Field(default_factory=list, description="Wikilinks pointing out from this note")


class Note(BaseModel):
    """Full representation of a markdown note."""
    title: str
    content: str
    metadata: NoteMetadata
    raw_markdown: str


class DailyEntry(BaseModel):
    """Structured entry in a daily journal."""
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    category: str = "General"
    content: str


class VaultMetrics(BaseModel):
    """Graph statistics and structural health of the vault."""
    total_notes: int
    total_links: int
    total_tags: int
    tags: Dict[str, int]
    orphan_notes: List[str] = Field(
        default_factory=list,
        description="Notes that neither link to other notes nor are linked by any note"
    )
    most_linked_notes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Hub notes with the most backlinks"
    )
