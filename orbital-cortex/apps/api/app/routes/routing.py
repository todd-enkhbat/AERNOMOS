"""Routing API routes."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core import storage
from app.db import get_db
from app.models.routing import RoutingResponse


router = APIRouter(prefix="/v1", tags=["routing"])


@router.get("/routing/{job_id}", response_model=RoutingResponse)
def get_routing(
    job_id: str,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.get_job(connection, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    decision = storage.get_routing_decision(connection, job_id)
    if decision is None:
        raise _api_error(
            404,
            "routing_not_found",
            f"No routing decision exists for job id {job_id}.",
        )
    return {"routing_decision": decision}


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
