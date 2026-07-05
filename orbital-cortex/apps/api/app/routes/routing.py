"""Routing API routes."""

from __future__ import annotations

from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import storage
from app.db import get_db
from app.models.errors import ErrorResponse
from app.models.routing import ReplayResponse, RoutingResponse
from app.routing.replay import canonical_hash, replay_from_inputs

router = APIRouter(prefix="/v1", tags=["routing"])

NOT_FOUND: Dict[Union[int, str], Dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Job or routing decision not found"}
}


@router.get(
    "/routing/{job_id}",
    response_model=RoutingResponse,
    summary="Get the routing explanation (legacy path)",
    responses=NOT_FOUND,
)
@router.get(
    "/jobs/{job_id}/routing",
    response_model=RoutingResponse,
    summary="Get the routing explanation for a job",
    description=(
        "Ranked candidates with eligibility, hard-constraint failures, "
        "per-factor sub-scores, weights, and the final score."
    ),
    responses=NOT_FOUND,
)
def get_routing(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.get_job(session, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    decision = storage.get_routing_decision(session, job_id)
    if decision is None:
        raise _api_error(
            404,
            "routing_not_found",
            f"No routing decision exists for job id {job_id}.",
        )
    return {"routing_decision": decision}


@router.post(
    "/jobs/{job_id}/replay",
    response_model=ReplayResponse,
    summary="Deterministically replay a routing decision",
    description=(
        "Recomputes the decision from the persisted inputs bundle and "
        "compares hashes bit-for-bit against the stored decision."
    ),
    responses=NOT_FOUND,
)
def replay_routing(
    job_id: str,
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    job = storage.get_job(session, job_id)
    if job is None:
        raise _api_error(404, "job_not_found", f"No job exists for id {job_id}.")
    audit = storage.get_routing_audit(session, job_id)
    if audit is None or not audit.get("inputs_json"):
        raise _api_error(
            404,
            "routing_not_found",
            f"No replayable routing audit exists for job id {job_id}.",
        )
    recomputed = replay_from_inputs(audit["inputs_json"])
    replay_hash = canonical_hash(recomputed)
    stored_hash = audit["decision_hash"]
    return {
        "match": replay_hash == stored_hash,
        "stored_decision_hash": stored_hash,
        "replay_decision_hash": replay_hash,
        "config_version": audit["config_version"],
        "input_hash": audit["input_hash"],
    }


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
