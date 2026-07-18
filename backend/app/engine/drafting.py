"""Core drafting logic shared by graph nodes, the engine, and the job runner.

Pure functions: providers in, domain objects out, no persistence. This is the
single source of the pre-read / challenge logic so the sync graph path and the
async job runner never diverge.
"""
from __future__ import annotations

from app.config import settings
from app.domain import (
    BoardPack, ChallengeItem, ChallengeSheet, DirectorProfile, PreRead, PreReadItem,
)
from app.interfaces import Inference, Repository

_PREREAD_SYSTEM = (
    "You are drafting a personalised board pre-read item. Summarise the section "
    "for a director in two or three sentences. This is a pre-read."
)
_CHALLENGE_SYSTEM = (
    "You are drafting a single board-level challenge question for a non-executive "
    "director. Given a pre-read item, produce one sharp challenge question. "
    "Return only the question."
)


def _score(text: str, keywords: list[str]) -> int:
    low = text.lower()
    return sum(low.count(k) for k in keywords)


def _lens_keywords(repo: Repository, lens_id: str) -> list[str]:
    lens = repo.get_lens(lens_id)
    return lens.keywords if lens else []


def draft_preread(inference: Inference, repo: Repository,
                  pack: BoardPack, profile: DirectorProfile) -> PreRead:
    """FR-PRE. Emphasis is lens-driven (FR-PR-4); pack-derived only (FR-PRE-2)."""
    keywords = _lens_keywords(repo, profile.lens_id)
    ordered = sorted(
        pack.sections,
        key=lambda s: _score(s.title + " " + s.text, keywords),
        reverse=True,
    )
    items: list[PreReadItem] = []
    for i, section in enumerate(ordered[: settings.preread_max_items], start=1):
        body = inference.complete(_PREREAD_SYSTEM, f"{section.title}\n{section.text}")
        items.append(PreReadItem(item_ref=f"PR-{i}", heading=section.title,
                                 body=body, source_section_ref=section.section_ref))
    return PreRead(pack_id=pack.id, profile_id=profile.id, items=items)


def draft_challenge(inference: Inference, pack: BoardPack, profile: DirectorProfile,
                    preread: PreRead) -> ChallengeSheet:
    """FR-CH. One challenge per pre-read item, linked back (FR-CH-2). Pack-only (FR-CH-4)."""
    items: list[ChallengeItem] = []
    for i, pr in enumerate(preread.items[: settings.challenge_max_items], start=1):
        question = inference.complete(_CHALLENGE_SYSTEM, f"{pr.heading}\n{pr.body}")
        items.append(ChallengeItem(item_ref=f"CH-{i}", question=question,
                                   source_item_ref=pr.item_ref))
    return ChallengeSheet(pack_id=pack.id, profile_id=profile.id, items=items)