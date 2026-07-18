"""Build the compiled LangGraph. Pre-read flow: START -> ingest -> preread -> END.

Deep-dive (Slice 3) will add a second entry with firewall -> research -> synthesis.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.engine.nodes import make_nodes
from app.engine.state import BoardPrepState
from app.providers.factory import Providers


def build_graph(providers: Providers):
    ingest_node, preread_node = make_nodes(providers)

    builder = StateGraph(BoardPrepState)
    builder.add_node("ingest", ingest_node)
    builder.add_node("preread", preread_node)
    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "preread")
    builder.add_edge("preread", END)
    return builder.compile()
