"""Deterministic cost estimation for simulated jobs."""

from __future__ import annotations

from typing import Any, Dict


PRIORITY_MULTIPLIERS = {
    "fastest": 1.2,
    "cheapest": 0.85,
    "most_reliable": 1.1,
}

SENSOR_MULTIPLIERS = {
    "SAR": 1.1,
    "optical": 1.0,
    "hyperspectral": 1.25,
    "any": 0.95,
}


def estimate_cost_usd(job: Dict[str, Any], node: Dict[str, Any]) -> float:
    priority_multiplier = PRIORITY_MULTIPLIERS[job["priority"]]
    sensor_multiplier = SENSOR_MULTIPLIERS[job["sensor"]]
    cost = float(node["base_cost_usd"]) * priority_multiplier * sensor_multiplier
    return round(cost, 2)
