"""Result API routes."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core import storage
from app.db import get_db
from app.models.result import ResultResponse


router = APIRouter(prefix="/v1", tags=["results"])


@router.get("/jobs/{job_id}/result", response_model=ResultResponse)
def get_result(
    job_id: str,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.get_job(connection, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    result = storage.get_result(connection, job_id)
    if result is None:
        raise _api_error(
            404,
            "result_not_ready",
            f"Result is not ready for job id {job_id}.",
        )
    return {"result": result}


def _api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )
