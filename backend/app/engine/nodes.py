"""Graph nodes. ingest (idempotent parse+index) + preread (shared drafting)."""
from __future__ import annotations

from app.engine.drafting import draft_preread
from app.engine.state import BoardPrepState
from app.providers.factory import Providers


def make_nodes(providers: Providers):
    def ingest_node(state: BoardPrepState) -> dict:
        if state.get("pack") is not None:
            return {}  # idempotent
        pack = providers.parser.parse(state["raw"], state.get("title", "Untitled pack"))
        providers.retriever.index(pack)
        return {"pack": pack}

    def preread_node(state: BoardPrepState) -> dict:
        pre_read = draft_preread(providers.inference, providers.repository,
                                 state["pack"], state["profile"])
        return {"pre_read": pre_read}

    return ingest_node, preread_node