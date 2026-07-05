"""Job API routes."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core import storage
from app.core.pagination import InvalidCursorError, encode_cursor
from app.core.pipeline import run_pipeline
from app.core.queue import enqueue_job_execution
from app.core.ratelimit import jobs_rate_limit, limiter
from app.core.state import IllegalTransitionError
from app.db import get_db
from app.models.errors import ErrorResponse
from app.models.event import JobEventsResponse
from app.models.job import (
    JobCreate,
    JobCreateResponse,
    JobDetailResponse,
    JobsListResponse,
    SimulateRunResponse,
)
from app.models.scene import SceneResponse
from app.services.scenes import get_scene, list_detections_geojson

router = APIRouter(prefix="/v1", tags=["jobs"])

NOT_FOUND: Dict[Union[int, str], Dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Job not found"}
}


@router.post(
    "/jobs",
    response_model=JobCreateResponse,
    status_code=201,
    summary="Submit a job",
    description=(
        "Accepts a versioned job spec, persists it as `queued`, and hands "
        "execution to the async worker. Returns immediately; poll the job "
        "until it reaches a terminal state."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Invalid job spec"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
@limiter.limit(jobs_rate_limit)
def create_job(
    request: Request,
    payload: JobCreate,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.create_job(session, _model_to_dict(payload))
    storage.create_event(
        session,
        job["id"],
        "job_created",
        (
            f"Accepted {job['sensor']} {job['job_type']} request with "
            f"{job['priority']} priority and ${job['max_cost_usd']:.2f} max budget."
        ),
        payload={"job_type": job["job_type"], "priority": job["priority"]},
    )
    session.commit()

    # Execution happens off the request path: the ARQ worker drives the
    # state machine. If Redis is unreachable (bare local dev), the job stays
    # queued and can be driven manually via POST /v1/simulate/run/{id}.
    enqueued = enqueue_job_execution(job["id"])
    storage.create_event(
        session,
        job["id"],
        "execution_enqueued" if enqueued else "execution_enqueue_failed",
        (
            "Job handed to the async execution worker."
            if enqueued
            else "Async queue unavailable; run manually via /v1/simulate/run."
        ),
        payload={"enqueued": enqueued},
    )
    session.commit()

    return {
        "job": job,
        "routing_decision": None,
    }


@router.get(
    "/jobs",
    response_model=JobsListResponse,
    summary="List jobs (cursor-paginated)",
    responses={400: {"model": ErrorResponse, "description": "Malformed cursor"}},
)
def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: Optional[str] = Query(
        default=None, description="Opaque cursor from a previous page's next_cursor"
    ),
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        jobs = storage.list_jobs(session, limit=limit, cursor=cursor)
    except InvalidCursorError:
        raise _api_error(400, "invalid_cursor", "The provided cursor is malformed.")
    next_cursor = None
    if len(jobs) == limit:
        next_cursor = encode_cursor(jobs[-1]["created_at"], jobs[-1]["id"])
    return {"jobs": jobs, "next_cursor": next_cursor}


@router.get(
    "/jobs/{job_id}",
    response_model=JobDetailResponse,
    summary="Get a job with its routing decision",
    responses=NOT_FOUND,
)
def get_job(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    job = _require_job(session, job_id)
    result = storage.get_result(session, job_id)
    return {
        "job": job,
        "routing_decision": storage.get_routing_decision(session, job_id),
        "result_summary": result["summary"] if result else None,
    }


@router.get(
    "/jobs/{job_id}/events",
    response_model=JobEventsResponse,
    summary="Get the append-only event trail for a job",
    responses=NOT_FOUND,
)
def get_job_events(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(session, job_id)
    return {"events": storage.list_events(session, job_id)}


@router.get(
    "/jobs/{job_id}/scene",
    response_model=SceneResponse,
    summary="Get the SAR scene provenance for a job",
    responses=NOT_FOUND,
)
def get_job_scene(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(session, job_id)
    return {"scene": get_scene(session, job_id)}


@router.get(
    "/jobs/{job_id}/detections",
    summary="Get job detections as GeoJSON",
    description="Returns an `application/geo+json` FeatureCollection.",
    responses=NOT_FOUND,
)
def get_job_detections(
    job_id: str,
    session: Session = Depends(get_db),
) -> JSONResponse:
    _require_job(session, job_id)
    geojson = list_detections_geojson(session, job_id)
    return JSONResponse(content=geojson, media_type="application/geo+json")


@router.post(
    "/simulate/run/{job_id}",
    response_model=SimulateRunResponse,
    summary="Drive a queued job to completion synchronously (dev fallback)",
    responses={
        **NOT_FOUND,
        409: {"model": ErrorResponse, "description": "Illegal state transition"},
    },
)
def simulate_run(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(session, job_id)
    try:
        response = run_pipeline(session, job_id)
        session.commit()
        return response
    except IllegalTransitionError as exc:
        session.rollback()
        raise _api_error(409, "illegal_state_transition", str(exc))
    except ValueError as exc:
        session.rollback()
        raise _api_error(400, "simulation_failed", str(exc))


def _require_job(session: Session, job_id: str) -> Dict[str, Any]:
    job = storage.get_job(session, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    return job


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


def _model_to_dict(model: JobCreate) -> Dict[str, Any]:
    return model.model_dump()
