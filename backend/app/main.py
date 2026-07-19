"""FastAPI surface — complete API for the frontend (A: contract-complete)."""
from __future__ import annotations

import asyncio
import json

from fastapi import Body, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.domain import (
    DirectorProfile, JobStatus, Lens, RetentionMode, UserSettings,
)
from app.engine.engine import BoardPrepEngine
from app.engine.jobs import JobRunner
from app.providers.factory import build_providers

app = FastAPI(title="Board-Prep Agent", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_providers = build_providers()
_engine = BoardPrepEngine(_providers)
_runner = JobRunner(_providers, _engine)
_repo = _providers.repository


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "providers": {
        "parser": settings.parser, "inference": settings.inference,
        "research": settings.research, "repository": settings.repository}}


# --- packs / jobs -----------------------------------------------------------
@app.post("/packs")
async def upload_pack(
    file: UploadFile,
    title: str = Form("Board pack"),
    lens_id: str = Form("lens_fullboard"),
    retention: RetentionMode = Form(RetentionMode(settings.default_retention)),
) -> dict:
    raw = await file.read()
    job = _runner.enqueue(raw, title, file.filename, lens_id, retention)
    return {"job_id": job.id, "status": job.status.value}


@app.get("/jobs")
def list_jobs() -> list[dict]:
    return [j.model_dump(mode="json") for j in _repo.list_jobs()]


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = _repo.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return job.model_dump(mode="json")


@app.get("/jobs/{job_id}/events")
async def job_events(job_id: str):
    async def gen():
        last = None
        while True:
            job = await asyncio.to_thread(_repo.get_job, job_id)
            if job is None:
                yield f"data: {json.dumps({'error': 'job not found'})}\n\n"
                return
            snap = job.model_dump(mode="json")
            if snap != last:
                yield f"data: {json.dumps(snap)}\n\n"
                last = snap
            if job.status in (JobStatus.READY, JobStatus.FAILED):
                return
            await asyncio.sleep(settings.job_poll_seconds)
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/packs")
def list_packs() -> list[dict]:
    return [{"pack_id": p.id, "title": p.title, "uploaded_at": p.uploaded_at.isoformat(),
             "retention_mode": p.retention_mode.value} for p in _repo.list_packs()]

@app.get("/traces")
def list_all_traces() -> list[dict]:
    return [t.model_dump(mode="json") for t in _repo.list_all_runtraces()]
    
@app.get("/packs/{pack_id}")
def get_pack(pack_id: str) -> dict:
    pack = _repo.get_pack(pack_id)
    if pack is None:
        raise HTTPException(404, "pack not found")
    pre_read = _repo.get_preread(pack_id)
    challenge = _repo.get_challenge(pack_id)
    deepdives = _repo.list_deepdives(pack_id)
    return {"pack": pack.model_dump(mode="json"),
            "pre_read": pre_read.model_dump(mode="json") if pre_read else None,
            "challenge": challenge.model_dump(mode="json") if challenge else None,
            "deepdives": [d.model_dump(mode="json") for d in deepdives]}


@app.delete("/packs/{pack_id}")
def delete_pack(pack_id: str) -> dict:
    if _repo.get_pack(pack_id) is None:
        raise HTTPException(404, "pack not found")
    _repo.delete_pack(pack_id)
    _providers.retriever.drop(pack_id)   # FR-LB-3/5 + TR-INV-5: vectors gone too
    return {"deleted": pack_id}


@app.post("/packs/{pack_id}/preread")
def regenerate_preread(pack_id: str, lens_id: str = Form(...)) -> dict:
    pack = _repo.get_pack(pack_id)
    if pack is None:
        raise HTTPException(404, "pack not found")
    pre_read = _engine.regenerate_preread(pack, DirectorProfile(lens_id=lens_id))
    return pre_read.model_dump(mode="json")


# --- challenge --------------------------------------------------------------
@app.post("/packs/{pack_id}/challenge")
def generate_challenge(pack_id: str, lens_id: str = Form("lens_fullboard")) -> dict:
    pack = _repo.get_pack(pack_id)
    if pack is None:
        raise HTTPException(404, "pack not found")
    pre_read = _repo.get_preread(pack_id)
    if pre_read is None:
        raise HTTPException(409, "pre-read not generated yet")
    profile = DirectorProfile(lens_id=lens_id)
    challenge = _engine.generate_challenge(pack, profile, pre_read)
    return challenge.model_dump(mode="json")


@app.get("/packs/{pack_id}/challenge")
def get_challenge(pack_id: str) -> dict:
    c = _repo.get_challenge(pack_id)
    if c is None:
        raise HTTPException(404, "challenge not found")
    return c.model_dump(mode="json")


# --- deep-dive --------------------------------------------------------------
@app.post("/packs/{pack_id}/deepdives")
def create_deepdive(pack_id: str, question: str = Form(...),
                    source_item_ref: str | None = Form(None)) -> dict:
    if _repo.get_pack(pack_id) is None:
        raise HTTPException(404, "pack not found")
    dd, query = _engine.deep_dive(pack_id, question, source_item_ref)
    out = dd.model_dump(mode="json")
    out["sanitised_query"] = query   # NFR-4: expose the exact external query
    return out


@app.get("/packs/{pack_id}/deepdives")
def list_deepdives(pack_id: str) -> list[dict]:
    return [d.model_dump(mode="json") for d in _repo.list_deepdives(pack_id)]


@app.delete("/deepdives/{deepdive_id}")
def delete_deepdive(deepdive_id: str) -> dict:
    _repo.delete_deepdive(deepdive_id)   # FR-LB-4
    return {"deleted": deepdive_id}


# --- lenses / settings / activity -------------------------------------------
@app.get("/lenses")
def list_lenses() -> list[dict]:
    return [l.model_dump(mode="json") for l in _repo.list_lenses()]


@app.post("/lenses")
def create_lens(lens: Lens = Body(...)) -> dict:
    lens.builtin = False
    _repo.save_lens(lens)
    return lens.model_dump(mode="json")


@app.patch("/lenses/{lens_id}")
def update_lens(lens_id: str, lens: Lens = Body(...)) -> dict:
    existing = _repo.get_lens(lens_id)
    if existing is None:
        raise HTTPException(404, "lens not found")
    if existing.builtin:
        raise HTTPException(409, "cannot edit a built-in lens")
    lens.id = lens_id
    lens.builtin = False
    _repo.save_lens(lens)
    return lens.model_dump(mode="json")


@app.delete("/lenses/{lens_id}")
def delete_lens(lens_id: str) -> dict:
    existing = _repo.get_lens(lens_id)
    if existing and existing.builtin:
        raise HTTPException(409, "cannot delete a built-in lens")
    _repo.delete_lens(lens_id)
    return {"deleted": lens_id}


@app.get("/settings")
def get_settings() -> dict:
    return _repo.get_settings().model_dump(mode="json")


@app.patch("/settings")
def update_settings(patch: dict = Body(...)) -> dict:
    current = _repo.get_settings().model_dump()
    current.update(patch)
    s = UserSettings(**current)
    _repo.save_settings(s)
    return s.model_dump(mode="json")


@app.get("/packs/{pack_id}/traces")
def list_traces(pack_id: str) -> list[dict]:
    return [t.model_dump(mode="json") for t in _repo.list_runtraces(pack_id)]