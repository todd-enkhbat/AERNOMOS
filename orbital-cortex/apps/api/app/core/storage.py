"""SQLite persistence helpers for jobs, routing, events, and results."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def loads(value: Optional[str], default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


def row_to_job(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "job_type": row["job_type"],
        "area_of_interest": loads(row["area_of_interest_json"], {}),
        "sensor": row["sensor"],
        "priority": row["priority"],
        "compute_preference": row["compute_preference"],
        "max_cost_usd": float(row["max_cost_usd"]),
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "selected_route_id": row["selected_route_id"],
    }


def create_job(connection: sqlite3.Connection, payload: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = utc_now()
    job_id = new_id("job")
    connection.execute(
        """
        INSERT INTO jobs (
            id,
            job_type,
            area_of_interest_json,
            sensor,
            priority,
            compute_preference,
            max_cost_usd,
            status,
            created_at,
            updated_at,
            selected_route_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            payload["job_type"],
            dumps(payload["area_of_interest"]),
            payload["sensor"],
            payload["priority"],
            payload["compute_preference"],
            float(payload["max_cost_usd"]),
            "queued",
            timestamp,
            timestamp,
            None,
        ),
    )
    job = get_job(connection, job_id)
    if job is None:
        raise RuntimeError("Job insert did not return a row")
    return job


def get_job(connection: sqlite3.Connection, job_id: str) -> Optional[Dict[str, Any]]:
    row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    return row_to_job(row)


def list_jobs(connection: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM jobs ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return [row_to_job(row) for row in rows]


def update_job(
    connection: sqlite3.Connection,
    job_id: str,
    *,
    status: Optional[str] = None,
    selected_route_id: Optional[str] = None,
) -> Dict[str, Any]:
    job = get_job(connection, job_id)
    if job is None:
        raise KeyError(job_id)
    new_status = status if status is not None else job["status"]
    new_route_id = (
        selected_route_id
        if selected_route_id is not None
        else job["selected_route_id"]
    )
    connection.execute(
        """
        UPDATE jobs
        SET status = ?, selected_route_id = ?, updated_at = ?
        WHERE id = ?
        """,
        (new_status, new_route_id, utc_now(), job_id),
    )
    updated = get_job(connection, job_id)
    if updated is None:
        raise KeyError(job_id)
    return updated


def row_to_routing_decision(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "job_id": row["job_id"],
        "selected_node_id": row["selected_node_id"],
        "selected_ground_station_id": row["selected_ground_station_id"],
        "fallback_node_id": row["fallback_node_id"],
        "estimated_latency_minutes": float(row["estimated_latency_minutes"]),
        "estimated_cost_usd": float(row["estimated_cost_usd"]),
        "confidence": float(row["confidence"]),
        "reasons": loads(row["reasons_json"], []),
        "candidate_scores": loads(row["candidate_scores_json"], []),
    }


def save_routing_decision(
    connection: sqlite3.Connection,
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    connection.execute(
        """
        INSERT INTO routing_decisions (
            id,
            job_id,
            selected_node_id,
            selected_ground_station_id,
            fallback_node_id,
            estimated_latency_minutes,
            estimated_cost_usd,
            confidence,
            reasons_json,
            candidate_scores_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            selected_node_id = excluded.selected_node_id,
            selected_ground_station_id = excluded.selected_ground_station_id,
            fallback_node_id = excluded.fallback_node_id,
            estimated_latency_minutes = excluded.estimated_latency_minutes,
            estimated_cost_usd = excluded.estimated_cost_usd,
            confidence = excluded.confidence,
            reasons_json = excluded.reasons_json,
            candidate_scores_json = excluded.candidate_scores_json
        """,
        (
            decision["id"],
            decision["job_id"],
            decision["selected_node_id"],
            decision.get("selected_ground_station_id"),
            decision.get("fallback_node_id"),
            float(decision["estimated_latency_minutes"]),
            float(decision["estimated_cost_usd"]),
            float(decision["confidence"]),
            dumps(decision["reasons"]),
            dumps(decision["candidate_scores"]),
            utc_now(),
        ),
    )
    saved = get_routing_decision(connection, decision["job_id"])
    if saved is None:
        raise RuntimeError("Routing decision insert did not return a row")
    return saved


def get_routing_decision(
    connection: sqlite3.Connection,
    job_id: str,
) -> Optional[Dict[str, Any]]:
    row = connection.execute(
        "SELECT * FROM routing_decisions WHERE job_id = ?",
        (job_id,),
    ).fetchone()
    if row is None:
        return None
    return row_to_routing_decision(row)


def row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "job_id": row["job_id"],
        "event_type": row["event_type"],
        "message": row["message"],
        "timestamp": row["timestamp"],
    }


def create_event(
    connection: sqlite3.Connection,
    job_id: str,
    event_type: str,
    message: str,
) -> Dict[str, Any]:
    event_id = new_id("evt")
    timestamp = utc_now()
    connection.execute(
        """
        INSERT INTO job_events (id, job_id, event_type, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_id, job_id, event_type, message, timestamp),
    )
    row = connection.execute(
        "SELECT * FROM job_events WHERE id = ?",
        (event_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Event insert did not return a row")
    return row_to_event(row)


def list_events(connection: sqlite3.Connection, job_id: str) -> List[Dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM job_events
        WHERE job_id = ?
        ORDER BY rowid ASC
        """,
        (job_id,),
    ).fetchall()
    return [row_to_event(row) for row in rows]


def row_to_result(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "job_id": row["job_id"],
        "summary": row["summary"],
        "confidence": float(row["confidence"]),
        "geojson": loads(row["geojson_json"], {}),
        "output_files": loads(row["output_files_json"], []),
    }


def save_result(
    connection: sqlite3.Connection,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    connection.execute(
        """
        INSERT INTO results (
            id,
            job_id,
            summary,
            confidence,
            geojson_json,
            output_files_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            summary = excluded.summary,
            confidence = excluded.confidence,
            geojson_json = excluded.geojson_json,
            output_files_json = excluded.output_files_json
        """,
        (
            result["id"],
            result["job_id"],
            result["summary"],
            float(result["confidence"]),
            dumps(result["geojson"]),
            dumps(result["output_files"]),
            utc_now(),
        ),
    )
    saved = get_result(connection, result["job_id"])
    if saved is None:
        raise RuntimeError("Result insert did not return a row")
    return saved


def get_result(connection: sqlite3.Connection, job_id: str) -> Optional[Dict[str, Any]]:
    row = connection.execute(
        "SELECT * FROM results WHERE job_id = ?",
        (job_id,),
    ).fetchone()
    if row is None:
        return None
    return row_to_result(row)
