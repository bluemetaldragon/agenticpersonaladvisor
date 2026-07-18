"""Provider contracts (NFR-2: everything below is swappable behind these).

Each Protocol names the module it realises (§8 component register) so the
implementation can be replaced without touching callers.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain import (
    BoardPack,
    DeepDive,
    DirectorProfile,
    PackChunk,
    PreRead,
    Source,
)


@runtime_checkable
class PackParser(Protocol):
    """M3 Ingestion. Swap: PyPdfParser (now) -> Docling (prod)."""

    def parse(self, raw: bytes, title: str) -> BoardPack: ...


@runtime_checkable
class Retriever(Protocol):
    """M4 Retrieval index. Swap: LocalRetriever (now) -> local embedder + pgvector.

    Embeddings are pack-derived MNPI and stay in-zone (FR-IN-8).
    """

    def index(self, pack: BoardPack) -> list[PackChunk]: ...

    def retrieve(self, pack_id: str, query: str, k: int = 4) -> list[PackChunk]: ...

    def drop(self, pack_id: str) -> None: ...


@runtime_checkable
class Inference(Protocol):
    """Shared inference. Swap: StubInference (now) -> Claude via Anthropic API."""

    def complete(self, system: str, user: str) -> str: ...


@runtime_checkable
class QueryFirewall(Protocol):
    """M7 Query firewall. Sole exit to external search (FR-FW-3).

    Receives a director *intent* string only — never pack chunks (INV-1).
    """

    def formulate(self, intent: str) -> str: ...


@runtime_checkable
class ResearchProvider(Protocol):
    """M8 Research module. Swap: StubResearch (now) -> Tavily. Lives outside the zone."""

    def search(self, query: str) -> list[Source]: ...


@runtime_checkable
class Repository(Protocol):
    """M9 Persistence substrate. Swap: InMemoryRepository (now) -> Supabase."""

    def save_pack(self, pack: BoardPack) -> None: ...
    def get_pack(self, pack_id: str) -> BoardPack | None: ...
    def list_packs(self) -> list[BoardPack]: ...
    def delete_pack(self, pack_id: str) -> None: ...

    def save_profile(self, profile: DirectorProfile) -> None: ...
    def get_profile(self, profile_id: str) -> DirectorProfile | None: ...

    def save_preread(self, preread: PreRead) -> None: ...
    def get_preread(self, pack_id: str) -> PreRead | None: ...

    def save_deepdive(self, deepdive: DeepDive) -> None: ...
    def list_deepdives(self, pack_id: str) -> list[DeepDive]: ...
    def delete_deepdive(self, deepdive_id: str) -> None: ...
