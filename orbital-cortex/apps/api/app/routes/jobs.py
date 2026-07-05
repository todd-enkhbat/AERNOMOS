"""Job API routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core import storage
from app.core.pipeline import run_pipeline
from app.core.queue import enqueue_job_execution
from app.core.state import IllegalTransitionError
from app.db import get_db
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


@router.post("/jobs", response_model=JobCreateResponse, status_code=201)
def create_job(
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


@router.get("/jobs", response_model=JobsListResponse)
def list_jobs(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {"jobs": storage.list_jobs(session)}


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
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


@router.get("/jobs/{job_id}/events", response_model=JobEventsResponse)
def get_job_events(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(session, job_id)
    return {"events": storage.list_events(session, job_id)}


@router.get("/jobs/{job_id}/scene", response_model=SceneResponse)
def get_job_scene(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(session, job_id)
    return {"scene": get_scene(session, job_id)}


@router.get("/jobs/{job_id}/detections")
def get_job_detections(
    job_id: str,
    session: Session = Depends(get_db),
) -> JSONResponse:
    _require_job(session, job_id)
    geojson = list_detections_geojson(session, job_id)
    return JSONResponse(content=geojson, media_type="application/geo+json")


@router.post("/simulate/run/{job_id}", response_model=SimulateRunResponse)
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
