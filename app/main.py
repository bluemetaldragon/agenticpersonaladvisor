"""FastAPI surface for Slice 1 (M1/M2 seam).

Endpoints map to spec §8; the granular deep-dive/library routes arrive in later
slices. The client (Next.js) is a thin consumer of these.
"""
from __future__ import annotations

from fastapi import FastAPI, Form, HTTPException, UploadFile

from app.config import settings
from app.domain import Committee, DirectorProfile, RetentionMode
from app.engine.engine import BoardPrepEngine
from app.providers.factory import build_providers

app = FastAPI(title="Board-Prep Agent", version="0.1.0")

_providers = build_providers()
_engine = BoardPrepEngine(_providers)
_repo = _providers.repository


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "providers": {
        "parser": settings.parser, "inference": settings.inference,
        "research": settings.research, "repository": settings.repository,
    }}


@app.post("/packs")
async def upload_pack(
    file: UploadFile,
    title: str = Form("Board pack"),
    committee: Committee = Form(Committee.OTHER),
    retention: RetentionMode = Form(RetentionMode(settings.default_retention)),
) -> dict:
    raw = await file.read()
    profile = DirectorProfile(committee=committee)
    pack, pre_read = _engine.ingest_and_preread(raw, title, profile, retention)
    return {"pack_id": pack.id, "sections": len(pack.sections),
            "pre_read": pre_read.model_dump(mode="json")}


@app.get("/packs")
def list_packs() -> list[dict]:
    return [{"pack_id": p.id, "title": p.title, "uploaded_at": p.uploaded_at.isoformat()}
            for p in _repo.list_packs()]


@app.get("/packs/{pack_id}")
def get_pack(pack_id: str) -> dict:
    pack = _repo.get_pack(pack_id)
    if pack is None:
        raise HTTPException(404, "pack not found")
    pre_read = _repo.get_preread(pack_id)
    return {"pack": pack.model_dump(mode="json"),
            "pre_read": pre_read.model_dump(mode="json") if pre_read else None}


@app.post("/packs/{pack_id}/preread")
def regenerate_preread(pack_id: str, committee: Committee = Form(...)) -> dict:
    pack = _repo.get_pack(pack_id)
    if pack is None:
        raise HTTPException(404, "pack not found")
    profile = DirectorProfile(committee=committee)
    pre_read = _engine.regenerate_preread(pack, profile)
    return pre_read.model_dump(mode="json")
