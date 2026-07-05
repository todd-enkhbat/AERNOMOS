"""Seed local SQLite data from simulator JSON files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List

from app.db import REPO_ROOT


SIMULATOR_DIR = REPO_ROOT / "simulator"


def _read_json_file(name: str) -> List[Dict[str, Any]]:
    path = SIMULATOR_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def _dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def seed_database(connection: sqlite3.Connection) -> Dict[str, int]:
    compute_nodes = _read_json_file("sample_nodes.json")
    ground_stations = _read_json_file("sample_ground_stations.json")
    _seed_compute_nodes(connection, compute_nodes)
    _seed_ground_stations(connection, ground_stations)
    connection.commit()
    return {
        "compute_nodes": len(compute_nodes),
        "ground_stations": len(ground_stations),
    }


def _seed_compute_nodes(
    connection: sqlite3.Connection,
    nodes: Iterable[Dict[str, Any]],
) -> None:
    for node in nodes:
        connection.execute(
            """
            INSERT INTO compute_nodes (
                id,
                name,
                type,
                location,
                orbit,
                gpu_class,
                supported_models_json,
                storage_gb,
                downlink_mbps,
                power_state,
                availability,
                compliance_tags_json,
                base_cost_usd,
                latency_minutes,
                next_contact_minutes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                type = excluded.type,
                location = excluded.location,
                orbit = excluded.orbit,
                gpu_class = excluded.gpu_class,
                supported_models_json = excluded.supported_models_json,
                storage_gb = excluded.storage_gb,
                downlink_mbps = excluded.downlink_mbps,
                power_state = excluded.power_state,
                availability = excluded.availability,
                compliance_tags_json = excluded.compliance_tags_json,
                base_cost_usd = excluded.base_cost_usd,
                latency_minutes = excluded.latency_minutes,
                next_contact_minutes = excluded.next_contact_minutes
            """,
            (
                node["id"],
                node["name"],
                node["type"],
                node["location"],
                node.get("orbit"),
                node["gpu_class"],
                _dumps(node["supported_models"]),
                int(node["storage_gb"]),
                int(node["downlink_mbps"]),
                node["power_state"],
                float(node["availability"]),
                _dumps(node["compliance_tags"]),
                float(node["base_cost_usd"]),
                float(node["latency_minutes"]),
                float(node.get("next_contact_minutes", 0)),
            ),
        )


def _seed_ground_stations(
    connection: sqlite3.Connection,
    ground_stations: Iterable[Dict[str, Any]],
) -> None:
    for station in ground_stations:
        connection.execute(
            """
            INSERT INTO ground_stations (
                id,
                name,
                location,
                latitude,
                longitude,
                latency_minutes,
                downlink_mbps,
                availability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                location = excluded.location,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                latency_minutes = excluded.latency_minutes,
                downlink_mbps = excluded.downlink_mbps,
                availability = excluded.availability
            """,
            (
                station["id"],
                station["name"],
                station["location"],
                float(station["latitude"]),
                float(station["longitude"]),
                float(station["latency_minutes"]),
                int(station["downlink_mbps"]),
                float(station["availability"]),
            ),
        )
