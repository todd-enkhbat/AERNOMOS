"""Deterministic contact-window helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def next_contact_minutes(node: Dict[str, Any]) -> float:
    if node["type"] == "ground_cloud":
        return 0.0
    return float(node.get("next_contact_minutes", 0))


def select_ground_station(
    ground_stations: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if not ground_stations:
        return None
    return sorted(
        ground_stations,
        key=lambda station: (
            -float(station["availability"]),
            float(station["latency_minutes"]),
            station["id"],
        ),
    )[0]
