"""LangGraph state for the pre-read flow.

The state carries the confidential pack and the derived pre-read. Nodes return
partial updates which LangGraph merges.
"""
from __future__ import annotations

from typing import TypedDict

from app.domain import BoardPack, DirectorProfile, PreRead


class BoardPrepState(TypedDict, total=False):
    raw: bytes
    title: str
    pack: BoardPack
    profile: DirectorProfile
    pre_read: PreRead
