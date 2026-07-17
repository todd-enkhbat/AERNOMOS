"""Postgres persistence helpers for jobs, routing, events, and results."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.orm import Session

from app.core.pagination import decode_cursor
from app.core.state import validate_transition
from app.db.orm import Job, JobEvent, Result, RoutingCandidate, RoutingDecision


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _job_to_dict(job: Job) -> Dict[str, Any]:
    return {
        "id": job.id,
        "schema_version": int(job.schema_version),
        "job_type": job.job_type,
        "area_of_interest": job.area_of_interest_json,
        "sensor": job.sensor,
        "priority": job.priority,
        "compute_preference": job.compute_preference,
        "max_cost_usd": float(job.max_cost_usd),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "selected_route_id": job.selected_route_id,
        "is_example": bool(getattr(job, "is_example", False)),
    }


def create_job(session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = utc_now()
    job = Job(
        id=new_id("job"),
        schema_version=int(payload.get("schema_version", 1)),
        job_type=payload["job_type"],
        area_of_interest_json=payload["area_of_interest"],
        sensor=payload["sensor"],
        priority=payload["priority"],
        compute_preference=payload["compute_preference"],
        max_cost_usd=float(payload["max_cost_usd"]),
        status="queued",
        created_at=timestamp,
        updated_at=timestamp,
        selected_route_id=None,
        # Public create path never marks examples; seed/ops set this explicitly.
        is_example=False,
    )
    session.add(job)
    session.flush()
    return _job_to_dict(job)


def get_job(session: Session, job_id: str) -> Optional[Dict[str, Any]]:
    job = session.get(Job, job_id)
    if job is None:
        return None
    return _job_to_dict(job)


def list_jobs(
    session: Session,
    *,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List curated public example jobs only (not visitor demo submissions)."""
    query = (
        select(Job)
        .where(Job.is_example.is_(True))
        .order_by(Job.created_at.desc(), Job.id.desc())
    )
    if cursor:
        created_at, job_id = decode_cursor(cursor, 2)
        query = query.where(tuple_(Job.created_at, Job.id) < (created_at, job_id))
    if limit is not None:
        query = query.limit(limit)
    jobs = session.scalars(query).all()
    return [_job_to_dict(job) for job in jobs]


def mark_jobs_as_examples(session: Session, job_ids: List[str]) -> int:
    """Mark the given job IDs as curated public examples. Returns count updated."""
    if not job_ids:
        return 0
    jobs = session.scalars(select(Job).where(Job.id.in_(job_ids))).all()
    for job in jobs:
        job.is_example = True
    session.flush()
    return len(jobs)


def ensure_curated_job_examples(session: Session, *, limit: int = 3) -> int:
    """Promote up to ``limit`` complete jobs as public examples when none exist.

    Prefers ship_detection (richest demo). Does not create synthetic jobs and
    does not delete non-example history — those rows stay reachable by direct
    ID only.
    """
    existing = session.scalar(
        select(func.count()).select_from(Job).where(Job.is_example.is_(True))
    )
    if existing:
        return int(existing)

    preferred = list(
        session.scalars(
            select(Job)
            .where(Job.status == "complete", Job.job_type == "ship_detection")
            .order_by(Job.created_at.desc())
            .limit(limit)
        ).all()
    )
    if len(preferred) < limit:
        seen = {job.id for job in preferred}
        extras = session.scalars(
            select(Job)
            .where(Job.status == "complete")
            .order_by(Job.created_at.desc())
            .limit(limit)
        ).all()
        for job in extras:
            if job.id not in seen:
                preferred.append(job)
                seen.add(job.id)
            if len(preferred) >= limit:
                break

    for job in preferred[:limit]:
        job.is_example = True
    session.flush()
    return len(preferred[:limit])


def update_job(
    session: Session,
    job_id: str,
    *,
    status: Optional[str] = None,
    selected_route_id: Optional[str] = None,
) -> Dict[str, Any]:
    job = session.get(Job, job_id)
    if job is None:
        raise KeyError(job_id)
    if status is not None and status != job.status:
        validate_transition(job.status, status)
        job.status = status
    if selected_route_id is not None:
        job.selected_route_id = selected_route_id
    job.updated_at = utc_now()
    session.flush()
    return _job_to_dict(job)


def _decision_to_dict(decision: RoutingDecision) -> Dict[str, Any]:
    payload = {
        "id": decision.id,
        "job_id": decision.job_id,
        "selected_node_id": decision.selected_node_id,
        "selected_ground_station_id": decision.selected_ground_station_id,
        "fallback_node_id": decision.fallback_node_id,
        "estimated_latency_minutes": float(decision.estimated_latency_minutes),
        "estimated_cost_usd": float(decision.estimated_cost_usd),
        "confidence": float(decision.confidence),
        "reasons": decision.reasons_json,
        "candidate_scores": decision.candidate_scores_json,
        "config_version": decision.config_version or None,
        "input_hash": decision.input_hash or None,
        "decision_hash": decision.decision_hash or None,
        "tle_snapshot_id": decision.tle_snapshot_id or None,
        "seed": int(decision.seed),
    }
    if isinstance(decision.inputs_json, dict):
        payload["decided_at_utc"] = decision.inputs_json.get("now_utc")
    return payload


def _soft_scores_from_candidate(candidate: Dict[str, Any]) -> Dict[str, float]:
    return {
        "model_support_score": float(candidate["model_support_score"]),
        "latency_score": float(candidate["latency_score"]),
        "cost_score": float(candidate["cost_score"]),
        "availability_score": float(candidate["availability_score"]),
        "contact_score": float(candidate["contact_score"]),
        "preference_score": float(candidate["preference_score"]),
        "compliance_score": float(candidate["compliance_score"]),
    }


def save_routing_decision(
    session: Session,
    decision: Dict[str, Any],
    *,
    audit: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    existing = session.scalars(
        select(RoutingDecision).where(RoutingDecision.job_id == decision["job_id"])
    ).one_or_none()
    if existing is None:
        existing = RoutingDecision(
            id=decision["id"],
            job_id=decision["job_id"],
            created_at=utc_now(),
        )
        session.add(existing)
    existing.selected_node_id = decision["selected_node_id"]
    existing.selected_ground_station_id = decision.get("selected_ground_station_id")
    existing.fallback_node_id = decision.get("fallback_node_id")
    existing.estimated_latency_minutes = float(decision["estimated_latency_minutes"])
    existing.estimated_cost_usd = float(decision["estimated_cost_usd"])
    existing.confidence = float(decision["confidence"])
    existing.reasons_json = decision["reasons"]
    existing.candidate_scores_json = decision["candidate_scores"]
    if audit is not None:
        existing.config_version = audit.get("config_version", "")
        existing.input_hash = audit.get("input_hash", "")
        existing.decision_hash = audit.get("decision_hash", "")
        existing.tle_snapshot_id = audit.get("tle_snapshot_id", "")
        existing.seed = int(audit.get("seed", 0))
        existing.inputs_json = audit.get("inputs_json", {})
    session.flush()

    session.execute(
        delete(RoutingCandidate).where(
            RoutingCandidate.routing_decision_id == existing.id
        )
    )
    for candidate in decision["candidate_scores"]:
        session.add(
            RoutingCandidate(
                id=new_id("rcand"),
                routing_decision_id=existing.id,
                node_id=candidate["node_id"],
                eligible=bool(candidate["eligible"]),
                hard_constraint_failures=candidate.get("hard_constraint_failures", []),
                soft_scores=_soft_scores_from_candidate(candidate),
                weights=candidate.get("weights", {}),
                final_score=float(candidate["score"]),
            )
        )
    session.flush()
    return _decision_to_dict(existing)


def get_routing_audit(session: Session, job_id: str) -> Optional[Dict[str, Any]]:
    decision = session.scalars(
        select(RoutingDecision).where(RoutingDecision.job_id == job_id)
    ).one_or_none()
    if decision is None:
        return None
    return {
        "id": decision.id,
        "job_id": decision.job_id,
        "config_version": decision.config_version,
        "input_hash": decision.input_hash,
        "decision_hash": decision.decision_hash,
        "tle_snapshot_id": decision.tle_snapshot_id,
        "seed": int(decision.seed),
        "inputs_json": decision.inputs_json,
    }


def get_routing_decision(
    session: Session,
    job_id: str,
) -> Optional[Dict[str, Any]]:
    decision = session.scalars(
        select(RoutingDecision).where(RoutingDecision.job_id == job_id)
    ).one_or_none()
    if decision is None:
        return None
    return _decision_to_dict(decision)


def _event_to_dict(event: JobEvent) -> Dict[str, Any]:
    return {
        "id": event.id,
        "job_id": event.job_id,
        "event_type": event.event_type,
        "message": event.message,
        "payload": event.payload,
        "ts_utc": event.ts_utc,
    }


def create_event(
    session: Session,
    job_id: str,
    event_type: str,
    message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = JobEvent(
        id=new_id("evt"),
        job_id=job_id,
        event_type=event_type,
        message=message,
        payload=payload or {},
        ts_utc=utc_now(),
    )
    session.add(event)
    session.flush()
    return _event_to_dict(event)


def list_events(session: Session, job_id: str) -> List[Dict[str, Any]]:
    events = session.scalars(
        select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.seq.asc())
    ).all()
    return [_event_to_dict(event) for event in events]


def _result_to_dict(result: Result) -> Dict[str, Any]:
    return {
        "id": result.id,
        "job_id": result.job_id,
        "summary": result.summary,
        "confidence": float(result.confidence),
        "geojson": result.geojson_json,
        "output_files": result.output_files_json,
    }


def save_result(
    session: Session,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    existing = session.scalars(
        select(Result).where(Result.job_id == result["job_id"])
    ).one_or_none()
    if existing is None:
        existing = Result(
            id=result["id"],
            job_id=result["job_id"],
            created_at=utc_now(),
        )
        session.add(existing)
    existing.summary = result["summary"]
    existing.confidence = float(result["confidence"])
    existing.geojson_json = result["geojson"]
    existing.output_files_json = result["output_files"]
    session.flush()
    return _result_to_dict(existing)


def get_result(session: Session, job_id: str) -> Optional[Dict[str, Any]]:
    result = session.scalars(
        select(Result).where(Result.job_id == job_id)
    ).one_or_none()
    if result is None:
        return None
    return _result_to_dict(result)
