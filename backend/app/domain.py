"""Domain models — entities from spec §7 + §14.7. Pure data, no I/O."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class RetentionMode(str, Enum):
    PERSIST = "persist"
    EPHEMERAL = "ephemeral"


# --- Lens (§14.7) ------------------------------------------------------------
class Lens(BaseModel):
    id: str = Field(default_factory=lambda: _id("lens"))
    name: str
    keywords: list[str] = Field(default_factory=list)
    builtin: bool = False


BUILTIN_LENSES: list[Lens] = [
    Lens(id="lens_risk", name="Risk",
         keywords=["risk", "capital", "credit", "cet1", "provision", "liquidity"], builtin=True),
    Lens(id="lens_audit", name="Audit",
         keywords=["control", "provision", "audit", "compliance", "restatement"], builtin=True),
    Lens(id="lens_remuneration", name="Remuneration",
         keywords=["remuneration", "pay", "incentive", "bonus", "compensation"], builtin=True),
    Lens(id="lens_nomination", name="Nomination/Governance",
         keywords=["governance", "board", "succession", "nomination", "composition"], builtin=True),
    Lens(id="lens_fullboard", name="Full board", keywords=[], builtin=True),
    Lens(id="lens_techcyber", name="Technology/Cyber",
         keywords=["cyber", "technology", "resilience", "vulnerability", "infrastructure"], builtin=True),
    Lens(id="lens_esg", name="ESG",
         keywords=["esg", "sustainability", "emissions", "scope", "climate"], builtin=True),
]


class DirectorProfile(BaseModel):
    id: str = Field(default_factory=lambda: _id("prof"))
    lens_id: str = "lens_fullboard"
    focus_areas: list[str] = Field(default_factory=list)
    depth: str = "standard"
    bank_context: str | None = None


class PackSection(BaseModel):
    section_ref: str
    title: str
    text: str


class BoardPack(BaseModel):
    id: str = Field(default_factory=lambda: _id("pack"))
    title: str
    uploaded_at: datetime = Field(default_factory=_now)
    sections: list[PackSection] = Field(default_factory=list)
    retention_mode: RetentionMode = RetentionMode.PERSIST


class PackChunk(BaseModel):
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
    id: str = Field(default_factory=lambda: _id("preread"))
    pack_id: str
    profile_id: str
    items: list[PreReadItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=_now)


# --- Challenge sheet (Slice 2, FR-CH) ---------------------------------------
class ChallengeItem(BaseModel):
    item_ref: str                       # CH-n
    question: str
    source_item_ref: str                # FR-CH-2: links back to a PreReadItem / section


class ChallengeSheet(BaseModel):
    id: str = Field(default_factory=lambda: _id("chsheet"))
    pack_id: str
    profile_id: str
    items: list[ChallengeItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=_now)


# --- Deep-dive (Slice 3, FR-DD) ---------------------------------------------
class Source(BaseModel):
    url: str
    snippet: str
    retrieved_at: datetime = Field(default_factory=_now)


class DeepDive(BaseModel):
    id: str = Field(default_factory=lambda: _id("dd"))
    pack_id: str
    question: str
    source_item_ref: str | None = None          # internal anchor ("Launched from")
    analysis: str = ""
    sources: list[Source] = Field(default_factory=list)   # external only
    created_at: datetime = Field(default_factory=_now)


# --- Governance / Activity (RunTrace, M10) ----------------------------------
class RunType(str, Enum):
    INGEST = "ingest"
    PREREAD = "preread"
    CHALLENGE = "challenge"
    DEEPDIVE = "deepdive"


class RunTrace(BaseModel):
    id: str = Field(default_factory=lambda: _id("trace"))
    pack_id: str
    run_type: RunType
    firewall_query: str | None = None           # NFR-4: exact external query (deep-dive)
    trace_ref: str | None = None                # Langfuse pointer
    created_at: datetime = Field(default_factory=_now)


# --- Async job (M11, FR-JOB) ------------------------------------------------
class JobStatus(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    INDEXING = "indexing"
    DRAFTING_PREREAD = "drafting_preread"
    DRAFTING_CHALLENGE = "drafting_challenge"
    READY = "ready"
    FAILED = "failed"


class StepState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"


class JobStep(BaseModel):
    name: str
    state: StepState = StepState.PENDING


class JobLogEntry(BaseModel):
    ts: datetime = Field(default_factory=_now)
    message: str


class Job(BaseModel):
    id: str = Field(default_factory=lambda: _id("job"))
    pack_id: str | None = None
    title: str = "Board pack"
    source_filename: str | None = None
    status: JobStatus = JobStatus.QUEUED
    percent: int = 0
    steps: list[JobStep] = Field(default_factory=list)
    log: list[JobLogEntry] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)


# --- Settings & branding (FR-SET) -------------------------------------------
class UserSettings(BaseModel):
    id: str = "settings_singleton"
    default_lens: str = "lens_fullboard"
    focus_areas: list[str] = Field(default_factory=list)
    depth: str = "standard"
    accent: str = "#003366"
    favicon_ref: str | None = None
    app_name: str = "Board Preparation Dashboard"
    logo_ref: str | None = None
    onboarding_seen_version: str | None = None