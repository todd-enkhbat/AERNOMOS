"""Registry reads for simulated compute nodes and ground stations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.orm import ComputeNode, GroundStation, Satellite


def _node_to_dict(node: ComputeNode) -> Dict[str, Any]:
    return {
        "id": node.id,
        "name": node.name,
        "type": node.type,
        "location": node.location,
        "orbit": node.orbit,
        "gpu_class": node.gpu_class,
        "supported_models": node.supported_models_json,
        "storage_gb": int(node.storage_gb),
        "downlink_mbps": int(node.downlink_mbps),
        "power_state": node.power_state,
        "availability": float(node.availability),
        "compliance_tags": node.compliance_tags_json,
        "base_cost_usd": float(node.base_cost_usd),
        "latency_minutes": float(node.latency_minutes),
        "satellite_id": node.satellite_id,
    }


def _station_to_dict(station: GroundStation) -> Dict[str, Any]:
    return {
        "id": station.id,
        "name": station.name,
        "location": station.location,
        "provider": station.provider,
        "latitude": float(station.latitude),
        "longitude": float(station.longitude),
        "altitude_m": float(station.altitude_m),
        "min_elevation_deg": float(station.min_elevation_deg),
        "latency_minutes": float(station.latency_minutes),
        "downlink_mbps": int(station.downlink_mbps),
        "availability": float(station.availability),
    }


def _satellite_to_dict(satellite: Satellite) -> Dict[str, Any]:
    return {
        "id": satellite.id,
        "name": satellite.name,
        "norad_id": int(satellite.norad_id),
        "tle_line1": satellite.tle_line1,
        "tle_line2": satellite.tle_line2,
        "tle_epoch": satellite.tle_epoch,
        "source": satellite.source,
        "snapshot_id": satellite.snapshot_id,
        "downlink_rate_mbps": float(satellite.downlink_rate_mbps),
    }


def list_satellites(session: Session) -> List[Dict[str, Any]]:
    satellites = session.scalars(select(Satellite).order_by(Satellite.id.asc())).all()
    return [_satellite_to_dict(satellite) for satellite in satellites]


def list_compute_nodes(session: Session) -> List[Dict[str, Any]]:
    nodes = session.scalars(select(ComputeNode).order_by(ComputeNode.id.asc())).all()
    return [_node_to_dict(node) for node in nodes]


def list_ground_stations(session: Session) -> List[Dict[str, Any]]:
    stations = session.scalars(
        select(GroundStation).order_by(GroundStation.id.asc())
    ).all()
    return [_station_to_dict(station) for station in stations]


def get_compute_node(
    session: Session,
    node_id: str,
) -> Optional[Dict[str, Any]]:
    node = session.get(ComputeNode, node_id)
    if node is None:
        return None
    return _node_to_dict(node)
