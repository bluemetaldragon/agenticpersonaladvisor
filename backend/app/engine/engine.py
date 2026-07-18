"""Engine facade. Sync pre-read graph + challenge + deep-dive, shared with the job runner."""
from __future__ import annotations

from app.domain import (
    BoardPack, ChallengeSheet, DeepDive, DirectorProfile, PreRead, RetentionMode,
    RunTrace, RunType,
)
from app.engine.drafting import draft_challenge, draft_preread
from app.engine.graph import build_graph
from app.providers.factory import Providers
from app.providers.firewall import build_search_intent

_SYNTH_SYSTEM = (
    "You are producing a deep-dive analysis for a board director. Using the "
    "external research findings, synthesise a peer/market picture and the "
    "implication for the director's position. If a point cannot be verified from "
    "the sources, say so explicitly. Do not fabricate sources."
)


def _synth_user(question: str, chunks, sources) -> str:
    # chunks inform reasoning (allowed); sources are the external evidence.
    ctx = "\n".join(f"- {c.chunk_text}" for c in chunks)
    ev = "\n".join(f"- {s.url}: {s.snippet}" for s in sources)
    return f"Question: {question}\n\nInternal context:\n{ctx}\n\nExternal findings:\n{ev}"


class BoardPrepEngine:
    def __init__(self, providers: Providers) -> None:
        self._providers = providers
        self._graph = build_graph(providers)
        self._repo = providers.repository

    # --- sync pre-read path (used by tests + regenerate) --------------------
    def ingest_and_preread(self, raw: bytes, title: str, profile: DirectorProfile,
                           retention: RetentionMode) -> tuple[BoardPack, PreRead]:
        result = self._graph.invoke({"raw": raw, "title": title, "profile": profile})
        pack: BoardPack = result["pack"]
        pack.retention_mode = retention
        pre_read: PreRead = result["pre_read"]
        if retention == RetentionMode.PERSIST:
            self._repo.save_pack(pack)
            self._repo.save_profile(profile)
            self._repo.save_preread(pre_read)
        else:
            self._providers.retriever.drop(pack.id)
        return pack, pre_read

    def regenerate_preread(self, pack: BoardPack, profile: DirectorProfile) -> PreRead:
        result = self._graph.invoke({"pack": pack, "profile": profile})
        pre_read: PreRead = result["pre_read"]
        if pack.retention_mode == RetentionMode.PERSIST:
            self._repo.save_preread(pre_read)
        return pre_read

    # --- phase methods (used by the async job runner) -----------------------
    def generate_preread(self, pack: BoardPack, profile: DirectorProfile) -> PreRead:
        return draft_preread(self._providers.inference, self._repo, pack, profile)

    def generate_challenge(self, pack: BoardPack, profile: DirectorProfile,
                           preread: PreRead) -> ChallengeSheet:
        challenge = draft_challenge(self._providers.inference, pack, profile, preread)
        if pack.retention_mode == RetentionMode.PERSIST:
            self._repo.save_challenge(challenge)
        return challenge

    # --- deep-dive (Slice 3, FR-DD; enforces INV-1) -------------------------
    def deep_dive(self, pack_id: str, question: str,
                  source_item_ref: str | None = None) -> DeepDive:
        pack = self._repo.get_pack(pack_id)
        chunks = self._providers.retriever.retrieve(pack_id, question, k=4)
        intent = build_search_intent(question, chunks)      # question only (INV-1)
        query = self._providers.firewall.formulate(intent)  # sole exit to external
        sources = self._providers.research.search(query)
        analysis = self._providers.inference.complete(
            _SYNTH_SYSTEM, _synth_user(question, chunks, sources))
        dd = DeepDive(pack_id=pack_id, question=question, source_item_ref=source_item_ref,
                      analysis=analysis, sources=sources)
        if pack is not None and pack.retention_mode == RetentionMode.PERSIST:
            self._repo.save_deepdive(dd)
            self._repo.save_runtrace(RunTrace(pack_id=pack_id, run_type=RunType.DEEPDIVE,
                                              firewall_query=query))  # NFR-4: exact query
        return dd, query