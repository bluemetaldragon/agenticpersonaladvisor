"""M11 async job runner (FR-JOB). In-process; the job row is the source of truth.

Progress is polled by the SSE endpoint every settings.job_poll_seconds (10s v1).
Upgrade path if the Processing screen feels sluggish: push updates to an
in-process asyncio.Queue and drain it in the SSE endpoint (no schema change).
"""
from __future__ import annotations

import asyncio

from app.domain import (
    DirectorProfile, Job, JobLogEntry, JobStatus, JobStep, RetentionMode, StepState,
)
from app.engine.engine import BoardPrepEngine
from app.providers.factory import Providers

_STEPS = [
    ("Document parsing", JobStatus.PARSING, 25),
    ("Vector indexing", JobStatus.INDEXING, 50),
    ("Drafting pre-read", JobStatus.DRAFTING_PREREAD, 75),
    ("Drafting challenge sheet", JobStatus.DRAFTING_CHALLENGE, 90),
]


class JobRunner:
    def __init__(self, providers: Providers, engine: BoardPrepEngine) -> None:
        self._providers = providers
        self._engine = engine
        self._repo = providers.repository

    def enqueue(self, raw: bytes, title: str, filename: str | None,
                lens_id: str, retention: RetentionMode) -> Job:
        job = Job(title=title, source_filename=filename, status=JobStatus.QUEUED,
                  steps=[JobStep(name=name) for name, _, _ in _STEPS])
        self._repo.save_job(job)
        asyncio.create_task(self._run(job.id, raw, title, lens_id, retention))
        return job

    async def _run(self, job_id, raw, title, lens_id, retention) -> None:
        try:
            await asyncio.to_thread(self._run_sync, job_id, raw, title, lens_id, retention)
        except Exception as e:  # FR-JOB-5: clear error + safe state, nothing shown ready
            self._fail(job_id, str(e))


    def _run_sync(self, job_id, raw, title, lens_id, retention) -> None:
        job = self._repo.get_job(job_id)
        persist = retention == RetentionMode.PERSIST

        self._enter(job, 0)                                   # parsing
        pack = self._providers.parser.parse(raw, title)
        pack.retention_mode = retention
        # Persist the pack NOW so the job's pack_id FK is satisfiable. For
        # ephemeral packs the pack is never stored, so we must not set pack_id
        # (it would violate job_pack_id_fkey against board_pack).
        if persist:
            self._repo.save_pack(pack)
            job.pack_id = pack.id
        self._done(job, 0)

        self._enter(job, 1)                                   # indexing
        self._providers.retriever.index(pack)
        self._done(job, 1)

        self._enter(job, 2)                                   # pre-read
        profile = DirectorProfile(lens_id=lens_id)
        pre_read = self._engine.generate_preread(pack, profile)
        if persist:
            self._repo.save_profile(profile)
            self._repo.save_preread(pre_read)
        self._done(job, 2)

        self._enter(job, 3)                                   # challenge
        challenge = self._engine.generate_challenge(pack, profile, pre_read)
        self._done(job, 3)

        if not persist:
            self._providers.retriever.drop(pack.id)           # ephemeral: no residue

        job.status = JobStatus.READY
        job.percent = 100
        job.log.append(JobLogEntry(message="Analysis ready."))
        self._repo.save_job(job)

    # helpers
    def _enter(self, job: Job, i: int) -> None:
        name, status, _ = _STEPS[i]
        job.status = status
        job.steps[i].state = StepState.ACTIVE
        job.log.append(JobLogEntry(message=f"{name}…"))
        self._repo.save_job(job)

    def _done(self, job: Job, i: int) -> None:
        name, _, pct = _STEPS[i]
        job.steps[i].state = StepState.DONE
        job.percent = pct
        job.log.append(JobLogEntry(message=f"{name} complete."))
        self._repo.save_job(job)

    def _fail(self, job_id: str, msg: str) -> None:
        job = self._repo.get_job(job_id)
        if job is None:
            return
        job.status = JobStatus.FAILED
        job.error = msg
        job.log.append(JobLogEntry(message=f"Failed: {msg}"))
        self._repo.save_job(job)