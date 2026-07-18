"""M4 default retriever. In-memory, deterministic token-overlap scoring.

Swap for prod (FR-IN-6/7/8): a local embedding model writing to pgvector. The
embeddings are pack-derived MNPI and never leave the zone; retrieval returns the
minimal relevant chunks (NFR-7) rather than the whole pack. Interface unchanged.
"""
from __future__ import annotations

import re

from app.domain import BoardPack, PackChunk

_WORD = re.compile(r"[a-z0-9]+")
_CHUNK_CHARS = 320


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


class LocalRetriever:
    def __init__(self) -> None:
        self._chunks: dict[str, list[PackChunk]] = {}

    def index(self, pack: BoardPack) -> list[PackChunk]:
        chunks: list[PackChunk] = []
        for section in pack.sections:
            for piece in self._split(section.text):
                chunks.append(
                    PackChunk(
                        pack_id=pack.id,
                        section_ref=section.section_ref,
                        chunk_text=piece,
                    )
                )
        self._chunks[pack.id] = chunks
        return chunks

    def retrieve(self, pack_id: str, query: str, k: int = 4) -> list[PackChunk]:
        chunks = self._chunks.get(pack_id, [])
        q = _tokens(query)
        scored = sorted(
            chunks,
            key=lambda c: len(_tokens(c.chunk_text) & q),
            reverse=True,
        )
        return [c for c in scored if _tokens(c.chunk_text) & q][:k]

    def drop(self, pack_id: str) -> None:
        self._chunks.pop(pack_id, None)

    @staticmethod
    def _split(text: str) -> list[str]:
        out, buf = [], ""
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
            if not sentence:
                continue
            if len(buf) + len(sentence) > _CHUNK_CHARS and buf:
                out.append(buf.strip())
                buf = ""
            buf += " " + sentence
        if buf.strip():
            out.append(buf.strip())
        return out
