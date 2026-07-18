"""M9 default repository. In-memory; Supabase (Postgres + pgvector + Storage) is the swap."""
from __future__ import annotations

from app.domain import BoardPack, DeepDive, DirectorProfile, PreRead


class InMemoryRepository:
    def __init__(self) -> None:
        self._packs: dict[str, BoardPack] = {}
        self._profiles: dict[str, DirectorProfile] = {}
        self._prereads: dict[str, PreRead] = {}
        self._deepdives: dict[str, DeepDive] = {}

    def save_pack(self, pack: BoardPack) -> None:
        self._packs[pack.id] = pack

    def get_pack(self, pack_id: str) -> BoardPack | None:
        return self._packs.get(pack_id)

    def list_packs(self) -> list[BoardPack]:
        return list(self._packs.values())

    def delete_pack(self, pack_id: str) -> None:
        self._packs.pop(pack_id, None)
        self._prereads.pop(pack_id, None)
        for dd_id in [d.id for d in self._deepdives.values() if d.pack_id == pack_id]:
            self._deepdives.pop(dd_id, None)

    def save_profile(self, profile: DirectorProfile) -> None:
        self._profiles[profile.id] = profile

    def get_profile(self, profile_id: str) -> DirectorProfile | None:
        return self._profiles.get(profile_id)

    def save_preread(self, preread: PreRead) -> None:
        self._prereads[preread.pack_id] = preread

    def get_preread(self, pack_id: str) -> PreRead | None:
        return self._prereads.get(pack_id)

    def save_deepdive(self, deepdive: DeepDive) -> None:
        self._deepdives[deepdive.id] = deepdive

    def list_deepdives(self, pack_id: str) -> list[DeepDive]:
        return [d for d in self._deepdives.values() if d.pack_id == pack_id]

    def delete_deepdive(self, deepdive_id: str) -> None:
        self._deepdives.pop(deepdive_id, None)
