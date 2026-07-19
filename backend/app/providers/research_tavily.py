"""M8 research provider — Tavily. Lives outside the confidential zone (FR-RE-3):
receives only the sanitised query from the firewall, never pack content.

Returns the same {url, snippet, retrieved_at} Source shape as the stub, so it's
a drop-in swap behind the ResearchProvider interface (NFR-2). SDK imported
lazily so the stub path runs without tavily-python installed.
"""
from __future__ import annotations

from app.domain import Source


class TavilyResearch:
    def __init__(self, api_key: str, max_results: int = 5) -> None:
        if not api_key:
            raise ValueError("TavilyResearch requires a tavily_api_key")
        self._api_key = api_key
        self._max_results = max_results
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from tavily import TavilyClient  # lazy: only on the prod path
            self._client = TavilyClient(api_key=self._api_key)
        return self._client

    def search(self, query: str) -> list[Source]:
        client = self._ensure_client()
        resp = client.search(
            query=query,
            max_results=self._max_results,
            search_depth="advanced",   # richer snippets for grounding
        )
        results = resp.get("results", []) if isinstance(resp, dict) else []
        sources: list[Source] = []
        for r in results:
            url = r.get("url")
            if not url:
                continue
            # snippet is the text that grounds the claim (FR-DD-5)
            snippet = (r.get("content") or r.get("title") or "").strip()
            sources.append(Source(url=url, snippet=snippet[:600]))
        return sources