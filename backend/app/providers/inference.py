"""Inference providers. StubInference deterministic; DeepSeekInference is the prod swap."""
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
        if "challenge" in task:
            return self._as_challenge(user)
        if "deep-dive" in task or "synthesis" in task:
            return self._as_analysis(user)
        if "pre-read" in task or "preread" in task:
            return self._as_preread_body(user)
        return user.strip()[:280]

    @staticmethod
    def _as_query(intent: str) -> str:
        cleaned = _CANARY_LIKE.sub("", intent)
        cleaned = _FIGURE_LIKE.sub("", cleaned)
        words = re.findall(r"[A-Za-z][A-Za-z\-]+", cleaned)
        return " ".join(words[:10]).strip()

    @staticmethod
    def _as_preread_body(user: str) -> str:
        first = user.strip().split("\n", 1)[0]
        return f"Key points for the board: {first[:180]}"

    @staticmethod
    def _as_challenge(user: str) -> str:
        first = user.strip().split("\n", 1)[0]
        return f"What assurance supports the position on {first[:120]}?"

    @staticmethod
    def _as_analysis(user: str) -> str:
        first = user.strip().split("\n", 1)[0]
        return (f"Peer picture: external comparators contextualise {first[:120]}. "
                f"Implication for the director: monitor against the peer trend. "
                f"Note: where public sources are thin, this is stated rather than inferred.")


class DeepSeekInference:
    """Prod swap. DeepSeek V4 via the OpenAI-compatible endpoint (thinking off by default)."""

    def __init__(self, api_key: str, model: str = "deepseek-v4-flash",
                 base_url: str = "https://api.deepseek.com", thinking: bool = False) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._thinking = thinking
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def complete(self, system: str, user: str) -> str:
        client = self._ensure_client()
        # DeepSeek V4 expects a ThinkingOptions object, not a bare boolean.
        thinking_config = {"type": "enabled"} if self._thinking else {"type": "disabled"}
        resp = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            extra_body={"thinking": thinking_config},
        )
        return (resp.choices[0].message.content or "").strip()

