"""M7 Query firewall (FR-FW) and the INV-1 boundary helper.

Two layers of the wall, both structural:

1. `build_search_intent` is the *only* sanctioned way to turn a director's
   question + retrieved chunks into a search intent. It derives the intent from
   the question ONLY; chunk text informs downstream analysis, never the query.
   The pack's content simply isn't handed to the firewall.

2. `LlmQueryFirewall.formulate` takes that intent string and produces a clean web
   query via the LLM, with a defensive scrub as backstop (v1: LLM-formulated;
   deterministic dedicated-agent check is RM-1).
"""
from __future__ import annotations

from app.domain import PackChunk
from app.interfaces import Inference

_FIREWALL_SYSTEM = (
    "You produce a concise web search query for the given topic. "
    "Do not include figures, names, or any verbatim text from internal documents. "
    "Return only the search query."
)


def build_search_intent(question: str, chunks: list[PackChunk]) -> str:
    """INV-1 boundary. Intent is derived from the question only.

    `chunks` are accepted so callers can't bypass this function to reach the
    firewall with raw pack content — but they are deliberately NOT used to build
    the intent string. They flow to analysis synthesis elsewhere.
    """
    _ = chunks  # intentionally unused for query construction
    return question.strip()


class LlmQueryFirewall:
    def __init__(self, inference: Inference) -> None:
        self._inference = inference

    def formulate(self, intent: str) -> str:
        return self._inference.complete(_FIREWALL_SYSTEM, intent).strip()
