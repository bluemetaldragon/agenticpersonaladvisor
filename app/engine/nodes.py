"""Graph nodes. Built as closures over the provider set.

- ingest_node: parse + index. Idempotent (skips if a pack is already in state),
  so the graph can be entered for pre-read regeneration without re-ingesting.
- preread_node: orders sections by committee relevance (deterministic emphasis,
  FR-PRE-1) then drafts each item body via inference.
"""
from __future__ import annotations

from app.domain import Committee, PreRead, PreReadItem
from app.engine.state import BoardPrepState
from app.providers.factory import Providers

# Committee -> keywords that raise a section's priority in the pre-read.
_EMPHASIS: dict[Committee, list[str]] = {
    Committee.RISK: ["risk", "capital", "credit", "cet1", "provision", "liquidity"],
    Committee.AUDIT: ["control", "provision", "audit", "compliance", "restatement"],
    Committee.REMUNERATION: ["remuneration", "pay", "incentive", "bonus", "compensation"],
    Committee.OTHER: [],
}

_PREREAD_SYSTEM = (
    "You are drafting a personalised board pre-read item. Summarise the section "
    "for a director in two or three sentences. This is a pre-read."
)


def _score(text: str, keywords: list[str]) -> int:
    low = text.lower()
    return sum(low.count(k) for k in keywords)


def make_nodes(providers: Providers):
    def ingest_node(state: BoardPrepState) -> dict:
        if state.get("pack") is not None:
            return {}  # idempotent
        pack = providers.parser.parse(state["raw"], state.get("title", "Untitled pack"))
        providers.retriever.index(pack)
        return {"pack": pack}

    def preread_node(state: BoardPrepState) -> dict:
        pack = state["pack"]
        profile = state["profile"]
        keywords = _EMPHASIS.get(profile.committee, [])

        ordered = sorted(
            pack.sections,
            key=lambda s: _score(s.title + " " + s.text, keywords),
            reverse=True,
        )

        from app.config import settings

        items: list[PreReadItem] = []
        for i, section in enumerate(ordered[: settings.preread_max_items], start=1):
            body = providers.inference.complete(
                _PREREAD_SYSTEM, f"{section.title}\n{section.text}"
            )
            items.append(
                PreReadItem(
                    item_ref=f"PR-{i}",
                    heading=section.title,
                    body=body,
                    source_section_ref=section.section_ref,
                )
            )

        pre_read = PreRead(pack_id=pack.id, profile_id=profile.id, items=items)
        return {"pre_read": pre_read}

    return ingest_node, preread_node
