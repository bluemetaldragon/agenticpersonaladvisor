"""M9 Supabase repository. Implements the Repository Protocol against 0001/0002/0003."""
from __future__ import annotations

from app.domain import (
    BoardPack, ChallengeSheet, DeepDive, DirectorProfile, Job, Lens, PreRead,
    RunTrace, UserSettings,
)

_USER = "single_user"  # A2; RLS-ready (NFR-6)


class SupabaseRepository:
    def __init__(self, url: str, key: str) -> None:
        if not url or not key:
            raise ValueError("SupabaseRepository requires supabase_url and supabase_key")
        from supabase import create_client
        self._client = create_client(url, key)

    def _t(self, name): return self._client.table(name)

    @staticmethod
    def _row(model, **extra): return {**model.model_dump(mode="json"), "user_id": _USER, **extra}

    @staticmethod
    def _one(res):
        data = getattr(res, "data", None) or []
        return data[0] if data else None

    # packs
    def save_pack(self, pack): self._t("board_pack").upsert(self._row(pack)).execute()
    def get_pack(self, pack_id):
        r = self._one(self._t("board_pack").select("*").eq("id", pack_id).execute())
        return BoardPack(**r) if r else None
    def list_packs(self):
        res = self._t("board_pack").select("*").order("uploaded_at", desc=True).execute()
        return [BoardPack(**r) for r in (res.data or [])]
    def delete_pack(self, pack_id):
        self._t("board_pack").delete().eq("id", pack_id).execute()  # cascade handles children

    # profiles
    def save_profile(self, p): self._t("director_profile").upsert(self._row(p)).execute()
    def get_profile(self, pid):
        r = self._one(self._t("director_profile").select("*").eq("id", pid).execute())
        return DirectorProfile(**r) if r else None

    # prereads (overwrite: one current per pack)
    def save_preread(self, pr):
        self._t("pre_read").delete().eq("pack_id", pr.pack_id).execute()
        self._t("pre_read").insert(self._row(pr)).execute()
    def get_preread(self, pack_id):
        r = self._one(self._t("pre_read").select("*").eq("pack_id", pack_id)
                      .order("generated_at", desc=True).limit(1).execute())
        return PreRead(**r) if r else None

    # challenge (overwrite: one current per pack)
    def save_challenge(self, c):
        self._t("challenge_sheet").delete().eq("pack_id", c.pack_id).execute()
        self._t("challenge_sheet").insert(self._row(c)).execute()
    def get_challenge(self, pack_id):
        r = self._one(self._t("challenge_sheet").select("*").eq("pack_id", pack_id)
                      .order("generated_at", desc=True).limit(1).execute())
        return ChallengeSheet(**r) if r else None

    # deepdives (thread)
    def save_deepdive(self, d): self._t("deep_dive").upsert(self._row(d)).execute()
    def list_deepdives(self, pack_id):
        res = self._t("deep_dive").select("*").eq("pack_id", pack_id).order("created_at").execute()
        return [DeepDive(**r) for r in (res.data or [])]
    def delete_deepdive(self, ddid): self._t("deep_dive").delete().eq("id", ddid).execute()

    # lenses
    def save_lens(self, l): self._t("lens").upsert(self._row(l)).execute()
    def get_lens(self, lid):
        r = self._one(self._t("lens").select("*").eq("id", lid).execute())
        return Lens(**r) if r else None
    def list_lenses(self):
        res = self._t("lens").select("*").execute()
        return [Lens(**r) for r in (res.data or [])]
    def delete_lens(self, lid): self._t("lens").delete().eq("id", lid).execute()

    # jobs
    def save_job(self, j): self._t("job").upsert(self._row(j)).execute()
    def get_job(self, jid):
        r = self._one(self._t("job").select("*").eq("id", jid).execute())
        return Job(**r) if r else None
    def list_jobs(self):
        res = self._t("job").select("*").order("created_at", desc=True).execute()
        return [Job(**r) for r in (res.data or [])]

    # traces
    def save_runtrace(self, t): self._t("run_trace").insert(self._row(t)).execute()
    def list_runtraces(self, pack_id):
        res = self._t("run_trace").select("*").eq("pack_id", pack_id).order("created_at", desc=True).execute()
        return [RunTrace(**r) for r in (res.data or [])]

    def list_all_runtraces(self):
        res = self._t("run_trace").select("*").order("created_at", desc=True).limit(200).execute()
        return [RunTrace(**r) for r in (res.data or [])]

    # settings (singleton)
    def get_settings(self):
        r = self._one(self._t("user_settings").select("*").eq("id", "settings_singleton").execute())
        return UserSettings(**r) if r else UserSettings()
    def save_settings(self, s):
        self._t("user_settings").upsert(self._row(s)).execute()