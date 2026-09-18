"""
Async job tracking for long-running background operations.

All LLM generation tasks return a job_id immediately (202 Accepted).
Callers poll GET /api/jobs/{job_id} until status is 'done' or 'failed'.

This in-memory store is sufficient for single-process development/demo.
For Phase 2 (multi-process / Kubernetes), replace _jobs with a Redis-backed
store without changing the HTTP contract.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ---------------------------------------------------------------------------
# In-memory job store
# Schema: {job_id: {status, created_at, updated_at, result, error}}
# ---------------------------------------------------------------------------

_jobs: dict[str, dict[str, Any]] = {}


def create_job() -> str:
    """Create a new job entry; returns the job_id."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
        "error": None,
    }
    return job_id


def set_job_running(job_id: str) -> None:
    if job_id in _jobs:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()


def complete_job(job_id: str, result: Any) -> None:
    if job_id in _jobs:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["result"] = result
        _jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()


def fail_job(job_id: str, error: str) -> None:
    if job_id in _jobs:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = error
        _jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# HTTP endpoint
# ---------------------------------------------------------------------------


@router.get("/{job_id}")
def get_job(job_id: str):
    """
    Poll the status of an async background job.

    Returns:
      - status: queued | running | done | failed
      - result: populated when status == done
      - error: populated when status == failed
    """
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job
