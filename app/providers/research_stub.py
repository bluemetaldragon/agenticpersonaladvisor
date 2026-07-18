"""M8 default research provider. Deterministic stub; Tavily is the prod swap.

Lives outside the confidential zone and receives only the sanitised query.
"""
from __future__ import annotations

from app.domain import Source


class StubResearch:
    def search(self, query: str) -> list[Source]:
        q = query.strip() or "market"
        return [
            Source(
                url=f"https://example.com/research?q={q.replace(' ', '+')}",
                snippet=f"Illustrative peer/market context for '{q}'.",
            )
        ]
