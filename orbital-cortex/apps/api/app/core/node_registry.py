"""Registry reads for simulated compute nodes and ground stations."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional


def _loads(value: str) -> Any:
    return json.loads(value)


def _row_to_compute_node(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "type": row["type"],
        "location": row["location"],
        "orbit": row["orbit"],
        "gpu_class": row["gpu_class"],
        "supported_models": _loads(row["supported_models_json"]),
        "storage_gb": int(row["storage_gb"]),
        "downlink_mbps": int(row["downlink_mbps"]),
        "power_state": row["power_state"],
        "availability": float(row["availability"]),
        "compliance_tags": _loads(row["compliance_tags_json"]),
        "base_cost_usd": float(row["base_cost_usd"]),
        "latency_minutes": float(row["latency_minutes"]),
        "next_contact_minutes": float(row["next_contact_minutes"]),
    }


def _row_to_ground_station(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "location": row["location"],
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "latency_minutes": float(row["latency_minutes"]),
        "downlink_mbps": int(row["downlink_mbps"]),
        "availability": float(row["availability"]),
    }


def list_compute_nodes(connection: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM compute_nodes ORDER BY id ASC"
    ).fetchall()
    return [_row_to_compute_node(row) for row in rows]


def list_ground_stations(connection: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM ground_stations ORDER BY id ASC"
    ).fetchall()
    return [_row_to_ground_station(row) for row in rows]


def get_compute_node(
    connection: sqlite3.Connection,
    node_id: str,
) -> Optional[Dict[str, Any]]:
    row = connection.execute(
        "SELECT * FROM compute_nodes WHERE id = ?",
        (node_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_compute_node(row)
