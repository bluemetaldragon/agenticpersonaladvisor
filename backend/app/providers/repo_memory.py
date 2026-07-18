"""M9 default repository. In-memory; Supabase is the swap."""
from __future__ import annotations

from app.domain import (
    BUILTIN_LENSES, BoardPack, ChallengeSheet, DeepDive, DirectorProfile, Job, Lens,
    PreRead, RunTrace, UserSettings,
)


class InMemoryRepository:
    def __init__(self) -> None:
        self._packs: dict[str, BoardPack] = {}
        self._profiles: dict[str, DirectorProfile] = {}
        self._prereads: dict[str, PreRead] = {}
        self._challenges: dict[str, ChallengeSheet] = {}
        self._deepdives: dict[str, DeepDive] = {}
        self._lenses: dict[str, Lens] = {l.id: l.model_copy() for l in BUILTIN_LENSES}
        self._jobs: dict[str, Job] = {}
        self._traces: list[RunTrace] = []
        self._settings = UserSettings()

    # packs
    def save_pack(self, pack: BoardPack) -> None: self._packs[pack.id] = pack
    def get_pack(self, pack_id): return self._packs.get(pack_id)
    def list_packs(self): return list(self._packs.values())

    def delete_pack(self, pack_id: str) -> None:
        self._packs.pop(pack_id, None)
        self._prereads.pop(pack_id, None)
        self._challenges.pop(pack_id, None)
        for dd in [d.id for d in self._deepdives.values() if d.pack_id == pack_id]:
            self._deepdives.pop(dd, None)
        self._traces = [t for t in self._traces if t.pack_id != pack_id]

    # profiles
    def save_profile(self, p): self._profiles[p.id] = p
    def get_profile(self, pid): return self._profiles.get(pid)

    # prereads
    def save_preread(self, pr): self._prereads[pr.pack_id] = pr
    def get_preread(self, pack_id): return self._prereads.get(pack_id)

    # challenge
    def save_challenge(self, c): self._challenges[c.pack_id] = c
    def get_challenge(self, pack_id): return self._challenges.get(pack_id)

    # deepdives
    def save_deepdive(self, d): self._deepdives[d.id] = d
    def list_deepdives(self, pack_id): return [d for d in self._deepdives.values() if d.pack_id == pack_id]
    def delete_deepdive(self, ddid): self._deepdives.pop(ddid, None)

    # lenses
    def save_lens(self, l): self._lenses[l.id] = l
    def get_lens(self, lid): return self._lenses.get(lid)
    def list_lenses(self): return list(self._lenses.values())
    def delete_lens(self, lid): self._lenses.pop(lid, None)

    # jobs
    def save_job(self, j): self._jobs[j.id] = j
    def get_job(self, jid): return self._jobs.get(jid)
    def list_jobs(self): return list(self._jobs.values())

    # traces
    def save_runtrace(self, t): self._traces.append(t)
    def list_runtraces(self, pack_id): return [t for t in self._traces if t.pack_id == pack_id]

    # settings
    def get_settings(self): return self._settings
    def save_settings(self, s): self._settings = s