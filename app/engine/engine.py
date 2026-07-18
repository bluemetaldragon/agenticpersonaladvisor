"""Engine facade. Wraps the compiled graph and the repository for the API layer."""
from __future__ import annotations

from app.domain import BoardPack, DirectorProfile, PreRead, RetentionMode
from app.engine.graph import build_graph
from app.providers.factory import Providers


class BoardPrepEngine:
    def __init__(self, providers: Providers) -> None:
        self._providers = providers
        self._graph = build_graph(providers)
        self._repo = providers.repository

    def ingest_and_preread(
        self, raw: bytes, title: str, profile: DirectorProfile, retention: RetentionMode
    ) -> tuple[BoardPack, PreRead]:
        result = self._graph.invoke({"raw": raw, "title": title, "profile": profile})
        pack: BoardPack = result["pack"]
        pack.retention_mode = retention
        pre_read: PreRead = result["pre_read"]

        if retention == RetentionMode.PERSIST:
            self._repo.save_pack(pack)
            self._repo.save_profile(profile)
            self._repo.save_preread(pre_read)
        else:
            self._providers.retriever.drop(pack.id)  # ephemeral: no residue
        return pack, pre_read

    def regenerate_preread(self, pack: BoardPack, profile: DirectorProfile) -> PreRead:
        # ingest node is idempotent, so this runs preread only.
        result = self._graph.invoke({"pack": pack, "profile": profile})
        pre_read: PreRead = result["pre_read"]
        if pack.retention_mode == RetentionMode.PERSIST:
            self._repo.save_preread(pre_read)
        return pre_read
