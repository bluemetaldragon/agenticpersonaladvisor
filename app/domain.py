"""Domain models — the entities from spec §7.

Pure data. No behaviour, no I/O. Every module speaks in these types.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class Committee(str, Enum):
    AUDIT = "audit"
    RISK = "risk"
    REMUNERATION = "remuneration"
    OTHER = "other"


class RetentionMode(str, Enum):
    PERSIST = "persist"
    EPHEMERAL = "ephemeral"


class DirectorProfile(BaseModel):
    """Spec: DirectorProfile. Shapes pre-read emphasis and challenge questions."""
    id: str = Field(default_factory=lambda: _id("prof"))
    committee: Committee = Committee.OTHER
    focus_areas: list[str] = Field(default_factory=list)
    depth: str = "standard"
    bank_context: str | None = None


class PackSection(BaseModel):
    section_ref: str
    title: str
    text: str


class BoardPack(BaseModel):
    """Spec: BoardPack. The confidential input, sectioned."""
    id: str = Field(default_factory=lambda: _id("pack"))
    title: str
    uploaded_at: datetime = Field(default_factory=_now)
    sections: list[PackSection] = Field(default_factory=list)
    retention_mode: RetentionMode = RetentionMode.PERSIST


class PackChunk(BaseModel):
    """Spec: PackChunk. Pack-derived — MNPI. Lives in-zone only."""
    id: str = Field(default_factory=lambda: _id("chunk"))
    pack_id: str
    section_ref: str
    chunk_text: str
    embedding: list[float] | None = None


class PreReadItem(BaseModel):
    item_ref: str
    heading: str
    body: str
    source_section_ref: str


class PreRead(BaseModel):
    """Spec: PreRead."""
    id: str = Field(default_factory=lambda: _id("preread"))
    pack_id: str
    profile_id: str
    items: list[PreReadItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=_now)


class Source(BaseModel):
    """Spec §5.5 refined shape: {url, snippet, retrieved_at}."""
    url: str
    snippet: str
    retrieved_at: datetime = Field(default_factory=_now)


class DeepDive(BaseModel):
    """Spec: DeepDive. Analysis + sources persist; raw payload is trace-only (FR-GV-4)."""
    id: str = Field(default_factory=lambda: _id("dd"))
    pack_id: str
    question: str
    source_item_ref: str | None = None
    analysis: str = ""
    sources: list[Source] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
