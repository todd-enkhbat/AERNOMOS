"""Job execution pipeline: routing + simulated execution stages.

Used by both the ARQ worker and the manual /v1/simulate/run endpoint.
Each stage reads the persisted job status and advances it one step, so the
pipeline is resumable: if a worker dies mid-flight, re-running it continues
from the last persisted state instead of starting over.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import node_registry, storage
from app.core.mock_inference import generate_mock_result
from app.core.object_store import get_object_store
from app.core.state import TERMINAL_STATES
from app.db.orm import Satellite
from app.routing.replay import (
    DEFAULT_SEED,
    build_inputs_bundle,
    canonical_hash,
)
from app.routing.scorer import ROUTING_CONFIG_VERSION, compute_routing_decision
from app.services.contact_windows import next_window_for_satellite
from app.services.scenes import ingest_canned_scene


def _transition(
    session: Session,
    job_id: str,
    to_status: str,
    event_type: str,
    message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    job = storage.get_job(session, job_id)
    event_payload = {
        "status_from": job["status"] if job else None,
        "status_to": to_status,
        **(payload or {}),
    }
    updated = storage.update_job(session, job_id, status=to_status)
    storage.create_event(session, job_id, event_type, message, payload=event_payload)
    return updated


def route_job(session: Session, job_id: str) -> Dict[str, Any]:
    """queued -> routing: score candidates and persist the routing decision."""
    job = storage.get_job(session, job_id)
    if job is None:
        raise KeyError(job_id)

    compute_nodes = node_registry.list_compute_nodes(session)
    ground_stations = node_registry.list_ground_stations(session)

    # Real SGP4 pass times from the precomputed cache, one per satellite.
    now = storage.utc_now()
    next_windows = {}
    for node in compute_nodes:
        satellite_id = node.get("satellite_id")
        if satellite_id and satellite_id not in next_windows:
            window = next_window_for_satellite(session, satellite_id, now)
            if window is not None:
                next_windows[satellite_id] = window

    routing_content = compute_routing_decision(
        job, compute_nodes, ground_stations, next_windows=next_windows, now_utc=now
    )
    inputs = build_inputs_bundle(
        job, compute_nodes, ground_stations, next_windows, now
    )
    input_hash = canonical_hash(inputs)
    decision_hash = canonical_hash(routing_content)
    tle_snapshot_id = session.scalars(select(Satellite.snapshot_id).limit(1)).first() or ""
    routing_decision = {"id": storage.new_id("route"), **routing_content}
    eligible_count = sum(
        1 for candidate in routing_decision["candidate_scores"] if candidate["eligible"]
    )
    storage.create_event(
        session,
        job_id,
        "routing_candidates_scored",
        (
            f"Scored {len(routing_decision['candidate_scores'])} compute nodes; "
            f"{eligible_count} passed model, policy, and preference checks."
        ),
        payload={
            "candidates": len(routing_decision["candidate_scores"]),
            "eligible": eligible_count,
        },
    )
    saved_decision = storage.save_routing_decision(
        session,
        routing_decision,
        audit={
            "config_version": ROUTING_CONFIG_VERSION,
            "input_hash": input_hash,
            "decision_hash": decision_hash,
            "tle_snapshot_id": tle_snapshot_id,
            "seed": DEFAULT_SEED,
            "inputs_json": inputs,
        },
    )
    _transition(
        session,
        job_id,
        "routing",
        "route_selected",
        (
            f"Selected {saved_decision['selected_node_id']} at "
            f"{saved_decision['confidence']:.0%} route confidence; "
            f"latency {saved_decision['estimated_latency_minutes']:.0f} minutes, "
            f"cost ${saved_decision['estimated_cost_usd']:.2f}, "
            f"fallback {saved_decision['fallback_node_id'] or 'none'}."
        ),
        payload={
            "routing_decision_id": saved_decision["id"],
            "selected_node_id": saved_decision["selected_node_id"],
            "confidence": saved_decision["confidence"],
        },
    )
    storage.update_job(session, job_id, selected_route_id=saved_decision["id"])
    return saved_decision


def run_pipeline(
    session: Session,
    job_id: str,
    *,
    stage_delay_s: float = 0.0,
) -> Dict[str, Any]:
    """Drive a job from its current state to a terminal state.

    Returns {"job", "events_created", "result"}.
    """
    job = storage.get_job(session, job_id)
    if job is None:
        raise KeyError(job_id)

    existing_result = storage.get_result(session, job_id)
    if job["status"] in TERMINAL_STATES:
        return {
            "job": job,
            "events_created": 0,
            "result": existing_result,
        }

    events_created = 0

    def _pause() -> None:
        if stage_delay_s > 0:
            session.commit()  # make progress visible to readers mid-flight
            time.sleep(stage_delay_s)

    if job["status"] == "queued":
        route_job(session, job_id)
        events_created += 2
        job = storage.get_job(session, job_id)
        assert job is not None
        _pause()

    routing_decision = storage.get_routing_decision(session, job_id)
    if routing_decision is None:
        raise ValueError("Job has no routing decision")

    if job["status"] == "routing":
        contact_message = (
            f"Confirmed next contact through {routing_decision['selected_ground_station_id']}."
            if routing_decision["selected_ground_station_id"]
            else "Confirmed direct cloud execution path; no ground station required."
        )
        job = _transition(
            session,
            job_id,
            "executing",
            "execution_scheduled",
            (
                f"Reserved simulated compute slot on {routing_decision['selected_node_id']} "
                f"for route {routing_decision['id']}."
            ),
            payload={"node_id": routing_decision["selected_node_id"]},
        )
        storage.create_event(
            session,
            job_id,
            "contact_window_confirmed",
            contact_message,
            payload={
                "ground_station_id": routing_decision["selected_ground_station_id"],
            },
        )
        storage.create_event(
            session,
            job_id,
            "execution_started",
            "Loaded mocked SAR scene and started deterministic inference pass.",
        )
        storage.create_event(
            session,
            job_id,
            "inference_completed",
            "Inference pass completed; detections and confidence scores generated.",
        )
        events_created += 4
        _pause()

    if job["status"] == "executing":
        job = _transition(
            session,
            job_id,
            "downlinking",
            "downlink_complete",
            "Packaged GeoJSON result and simulated downlink handoff completed.",
        )
        events_created += 1
        _pause()

    saved_result: Optional[Dict[str, Any]]
    if job["status"] == "downlinking":
        result = generate_mock_result(job)
        # F1: bytes go to object storage; the DB row keeps only the keys.
        result["output_files"] = _upload_result_artifacts(session, job_id, result)
        saved_result = storage.save_result(session, result)
        job = storage.get_job(session, job_id)
        assert job is not None
        ingest_canned_scene(session, job)
        job = _transition(
            session,
            job_id,
            "complete",
            "result_ready",
            "Result manifest, summary, and detection features are ready for retrieval.",
            payload={"result_id": saved_result["id"]},
        )
        events_created += 1
    else:
        saved_result = storage.get_result(session, job_id)

    return {
        "job": job,
        "events_created": events_created,
        "result": saved_result,
    }


def _upload_result_artifacts(
    session: Session,
    job_id: str,
    result: Dict[str, Any],
) -> List[str]:
    """Upload result artifacts; on failure the result stays inline-only."""
    detections_key = f"results/{job_id}/detections.geojson"
    summary_key = f"results/{job_id}/summary.json"
    summary_doc = {
        "job_id": job_id,
        "summary": result["summary"],
        "confidence": result["confidence"],
    }
    try:
        store = get_object_store()
        store.put_bytes(
            detections_key,
            json.dumps(result["geojson"]).encode("utf-8"),
            "application/geo+json",
        )
        store.put_bytes(
            summary_key,
            json.dumps(summary_doc).encode("utf-8"),
            "application/json",
        )
    except Exception as exc:
        storage.create_event(
            session,
            job_id,
            "artifact_upload_failed",
            f"Object-store upload failed; result remains inline: {exc}",
            payload={"error": str(exc)},
        )
        return []
    storage.create_event(
        session,
        job_id,
        "artifacts_uploaded",
        "Uploaded result artifacts to object storage.",
        payload={"keys": [detections_key, summary_key]},
    )
    return [detections_key, summary_key]


def fail_job(session: Session, job_id: str, error: str) -> None:
    """Mark a job failed (from any non-terminal state) with an event."""
    job = storage.get_job(session, job_id)
    if job is None or job["status"] in TERMINAL_STATES:
        return
    _transition(
        session,
        job_id,
        "failed",
        "job_failed",
        f"Job execution failed: {error}",
        payload={"error": error},
    )
