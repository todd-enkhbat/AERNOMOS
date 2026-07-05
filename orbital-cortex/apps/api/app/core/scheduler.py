"""Manual simulation scheduler."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List

from app.core.mock_inference import generate_mock_result
from app.core import storage


def run_job_simulation(
    connection: sqlite3.Connection,
    job_id: str,
) -> Dict[str, Any]:
    job = storage.get_job(connection, job_id)
    if job is None:
        raise KeyError(job_id)

    existing_result = storage.get_result(connection, job_id)
    if job["status"] == "completed" and existing_result is not None:
        return {
            "job": job,
            "events_created": 0,
            "result": existing_result,
        }

    routing_decision = storage.get_routing_decision(connection, job_id)
    if routing_decision is None:
        raise ValueError("Job has no routing decision")

    created_events: List[Dict[str, Any]] = []
    transitions = [
        (
            "scheduled",
            "execution_scheduled",
            (
                "Job scheduled on "
                f"{routing_decision['selected_node_id']} via route "
                f"{routing_decision['id']}."
            ),
        ),
        (
            "running",
            "execution_started",
            "Mock inference started on selected simulated compute node.",
        ),
        (
            "running",
            "downlink_complete",
            "Simulated downlink and result packaging completed.",
        ),
    ]
    for status, event_type, message in transitions:
        job = storage.update_job(connection, job_id, status=status)
        created_events.append(storage.create_event(connection, job_id, event_type, message))

    result = generate_mock_result(job)
    saved_result = storage.save_result(connection, result)
    job = storage.update_job(connection, job_id, status="completed")
    created_events.append(
        storage.create_event(
            connection,
            job_id,
            "result_ready",
            "Mock result is ready for retrieval.",
        )
    )

    return {
        "job": job,
        "events_created": len(created_events),
        "result": saved_result,
    }
