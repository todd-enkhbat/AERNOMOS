"""Result API routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import storage
from app.core.object_store import get_object_store
from app.db import get_db
from app.models.errors import ErrorResponse
from app.models.result import ResultResponse

router = APIRouter(prefix="/v1", tags=["results"])


@router.get(
    "/jobs/{job_id}/result",
    response_model=ResultResponse,
    summary="Get the result manifest for a completed job",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found or result not ready"}
    },
)
def get_result(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.get_job(session, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    result = storage.get_result(session, job_id)
    if result is None:
        raise _api_error(
            404,
            "result_not_ready",
            f"Result is not ready for job id {job_id}.",
        )
    store = get_object_store()
    artifacts = [
        {"key": key, "url": store.signed_url(key)}
        for key in result["output_files"]
        if "://" not in key  # skip legacy mock:// URIs from pre-F1 rows
    ]
    return {"result": result, "artifacts": artifacts}


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
