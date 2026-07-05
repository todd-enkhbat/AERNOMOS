"""Job API routes."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core import node_registry, storage
from app.core.router import build_routing_decision
from app.core.scheduler import run_job_simulation
from app.db import get_db
from app.models.event import JobEventsResponse
from app.models.job import (
    JobCreate,
    JobCreateResponse,
    JobDetailResponse,
    JobsListResponse,
    SimulateRunResponse,
)


router = APIRouter(prefix="/v1", tags=["jobs"])


@router.post("/jobs", response_model=JobCreateResponse, status_code=201)
def create_job(
    payload: JobCreate,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    try:
        job = storage.create_job(connection, _model_to_dict(payload))
        storage.create_event(
            connection,
            job["id"],
            "job_created",
            (
                f"Accepted {job['sensor']} {job['job_type']} request with "
                f"{job['priority']} priority and ${job['max_cost_usd']:.2f} max budget."
            ),
        )
        compute_nodes = node_registry.list_compute_nodes(connection)
        ground_stations = node_registry.list_ground_stations(connection)
        routing_decision = build_routing_decision(job, compute_nodes, ground_stations)
        eligible_count = sum(
            1 for candidate in routing_decision["candidate_scores"]
            if candidate["eligible"]
        )
        storage.create_event(
            connection,
            job["id"],
            "routing_candidates_scored",
            (
                f"Scored {len(routing_decision['candidate_scores'])} compute nodes; "
                f"{eligible_count} passed model, policy, and preference checks."
            ),
        )
        saved_decision = storage.save_routing_decision(connection, routing_decision)
        job = storage.update_job(
            connection,
            job["id"],
            selected_route_id=saved_decision["id"],
        )
        storage.create_event(
            connection,
            job["id"],
            "route_selected",
            (
                f"Selected {saved_decision['selected_node_id']} at "
                f"{saved_decision['confidence']:.0%} route confidence; "
                f"latency {saved_decision['estimated_latency_minutes']:.0f} minutes, "
                f"cost ${saved_decision['estimated_cost_usd']:.2f}, "
                f"fallback {saved_decision['fallback_node_id'] or 'none'}."
            ),
        )
        connection.commit()
        return {
            "job": job,
            "routing_decision": saved_decision,
        }
    except ValueError as exc:
        connection.rollback()
        raise _api_error(400, "routing_failed", str(exc))


@router.get("/jobs", response_model=JobsListResponse)
def list_jobs(
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    return {"jobs": storage.list_jobs(connection)}


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: str,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    job = _require_job(connection, job_id)
    result = storage.get_result(connection, job_id)
    return {
        "job": job,
        "routing_decision": storage.get_routing_decision(connection, job_id),
        "result_summary": result["summary"] if result else None,
    }


@router.get("/jobs/{job_id}/events", response_model=JobEventsResponse)
def get_job_events(
    job_id: str,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(connection, job_id)
    return {"events": storage.list_events(connection, job_id)}


@router.post("/simulate/run/{job_id}", response_model=SimulateRunResponse)
def simulate_run(
    job_id: str,
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    _require_job(connection, job_id)
    try:
        response = run_job_simulation(connection, job_id)
        connection.commit()
        return response
    except ValueError as exc:
        connection.rollback()
        raise _api_error(400, "simulation_failed", str(exc))


def _require_job(connection: sqlite3.Connection, job_id: str) -> Dict[str, Any]:
    job = storage.get_job(connection, job_id)
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
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
