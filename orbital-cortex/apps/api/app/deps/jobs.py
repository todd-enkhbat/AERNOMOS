"""Authorization for legacy demo jobs (example vs private access token)."""

from __future__ import annotations

import hmac
from typing import Any, Dict, Optional

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core import storage
from app.core.tokens import hash_token
from app.db import get_db


def _api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message}},
    )


def require_job_access(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    x_nomos_job_token: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Load a job if the caller may read it.

    - Curated ``is_example`` jobs are public (no token).
    - Visitor submissions require ``X-Nomos-Job-Token`` matching the
      SHA-256 hash stored at create time.
    """
    job = storage.get_job(db, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")

    if job.get("is_example"):
        return job

    raw = (x_nomos_job_token or "").strip()
    expected = storage.get_job_access_token_hash(db, job_id)
    if not raw or not expected:
        raise _api_error(
            401,
            "job_token_required",
            "A job access token is required to read this private demo job.",
        )
    if not hmac.compare_digest(hash_token(raw), expected):
        raise _api_error(
            403,
            "job_forbidden",
            "Job access token is invalid.",
        )
    # Header is accepted; never echo it back or log it.
    _ = request
    return job
