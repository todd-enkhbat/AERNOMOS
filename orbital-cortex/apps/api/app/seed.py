"""Seed Postgres reference data: compute nodes, ground stations, satellites."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import REPO_ROOT
from app.db.orm import ComputeNode, GroundStation, Satellite
from app.services import tle_cache

SIMULATOR_DIR = REPO_ROOT / "simulator"


def _read_json_file(name: str) -> List[Dict[str, Any]]:
    path = SIMULATOR_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def seed_database(session: Session) -> Dict[str, int]:
    ground_stations = _read_json_file("ground_stations.json")
    compute_nodes = _read_json_file("sample_nodes.json")
    snapshot = tle_cache.get_snapshot(live=get_settings().live_tle)

    _seed_ground_stations(session, ground_stations)
    _seed_satellites(session, snapshot)
    # Satellites must exist before compute-node rows reference them (FK).
    session.flush()
    _seed_compute_nodes(session, compute_nodes)
    session.commit()
    return {
        "compute_nodes": len(compute_nodes),
        "ground_stations": len(ground_stations),
        "satellites": len(snapshot["satellites"]),
    }


def _seed_satellites(session: Session, snapshot: Dict[str, Any]) -> None:
    for sat in snapshot["satellites"]:
        record = session.get(Satellite, sat["id"])
        if record is None:
            record = Satellite(id=sat["id"])
            session.add(record)
        record.name = sat["name"]
        record.norad_id = int(sat["norad_id"])
        record.tle_line1 = sat["tle_line1"]
        record.tle_line2 = sat["tle_line2"]
        record.tle_epoch = sat["tle_epoch"]
        record.source = snapshot["source"]
        record.snapshot_id = snapshot["snapshot_id"]
        record.downlink_rate_mbps = float(sat["downlink_rate_mbps"])


def _seed_compute_nodes(
    session: Session,
    nodes: Iterable[Dict[str, Any]],
) -> None:
    for node in nodes:
        record = session.get(ComputeNode, node["id"])
        if record is None:
            record = ComputeNode(id=node["id"])
            session.add(record)
        record.name = node["name"]
        record.type = node["type"]
        record.location = node["location"]
        record.orbit = node.get("orbit")
        record.gpu_class = node["gpu_class"]
        record.supported_models_json = node["supported_models"]
        record.storage_gb = int(node["storage_gb"])
        record.downlink_mbps = int(node["downlink_mbps"])
        record.power_state = node["power_state"]
        record.availability = float(node["availability"])
        record.compliance_tags_json = node["compliance_tags"]
        record.base_cost_usd = float(node["base_cost_usd"])
        record.latency_minutes = float(node["latency_minutes"])
        record.satellite_id = node.get("satellite_id")


def _seed_ground_stations(
    session: Session,
    ground_stations: Iterable[Dict[str, Any]],
) -> None:
    for station in ground_stations:
        record = session.get(GroundStation, station["id"])
        if record is None:
            record = GroundStation(id=station["id"])
            session.add(record)
        record.name = station["name"]
        record.location = station["location"]
        record.provider = station.get("provider", "")
        record.latitude = float(station["latitude"])
        record.longitude = float(station["longitude"])
        record.altitude_m = float(station.get("altitude_m", 0))
        record.min_elevation_deg = float(station.get("min_elevation_deg", 10.0))
        record.latency_minutes = float(station["latency_minutes"])
        record.downlink_mbps = int(station["downlink_mbps"])
        record.availability = float(station["availability"])
