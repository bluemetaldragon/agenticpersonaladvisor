"""Inference providers.

StubInference is deterministic so gating tests don't depend on model variance.
AnthropicInference is the prod swap (Claude); it imports the SDK lazily so the
stub path runs with nothing installed.
"""
from __future__ import annotations

import re

_CANARY_LIKE = re.compile(r"\b[A-Z][A-Z0-9]{2,}-CANARY-\d+\b")
_FIGURE_LIKE = re.compile(r"\b[A-Z]{3,}-\d{3,}\b|\b\d+\.\d+%\b")


class StubInference:
    """Deterministic. Branches on the system prompt's declared task."""

    def complete(self, system: str, user: str) -> str:
        task = system.lower()
        if "search query" in task or "web search" in task:
            return self._as_query(user)
        if "pre-read" in task or "preread" in task:
            return self._as_preread_body(user)
        return user.strip()[:280]

    @staticmethod
    def _as_query(intent: str) -> str:
        # Defensive scrub: even if an intent carries canary/figure-like tokens
        # (e.g. adversarial director input), they never reach the query.
        cleaned = _CANARY_LIKE.sub("", intent)
        cleaned = _FIGURE_LIKE.sub("", cleaned)
        words = re.findall(r"[A-Za-z][A-Za-z\-]+", cleaned)
        return " ".join(words[:10]).strip()

    @staticmethod
    def _as_preread_body(user: str) -> str:
        first = user.strip().split("\n", 1)[0]
        return f"Key points for the board: {first[:180]}"


class AnthropicInference:
    """Prod swap. Claude via the Anthropic API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5") -> None:
        self._api_key = api_key
        self._model = model
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import anthropic  # lazy: only needed on the prod path

            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def complete(self, system: str, user: str) -> str:
        client = self._ensure_client()
        msg = client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in msg.content if block.type == "text")
