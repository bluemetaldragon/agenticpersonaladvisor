"""M8 default research provider. Deterministic stub; Tavily is the prod swap."""
from __future__ import annotations
from app.domain import Source


class StubResearch:
    def search(self, query: str) -> list[Source]:
        q = query.strip() or "market"
        return [
            Source(
                url=f"https://reuters.com/markets?q={q.replace(' ', '+')}",
                snippet=f"Peer/market context relevant to '{q}'.",
            ),
            Source(
                url=f"https://ft.com/search?q={q.replace(' ', '+')}",
                snippet=f"Sector commentary bearing on '{q}'.",
            ),
        ]