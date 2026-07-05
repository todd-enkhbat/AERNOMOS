"""Deterministic routing score implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.core.contact_windows import next_contact_minutes, select_ground_station
from app.core.cost_model import estimate_cost_usd
from app.core.policy_engine import node_is_allowed
from app.core.storage import new_id


def build_routing_decision(
    job: Dict[str, Any],
    compute_nodes: List[Dict[str, Any]],
    ground_stations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    raw_candidates = [
        _build_raw_candidate(job, node, ground_stations)
        for node in compute_nodes
    ]
    candidates = _score_candidates(job, raw_candidates)
    eligible_candidates = [candidate for candidate in candidates if candidate["eligible"]]
    if not eligible_candidates:
        raise ValueError("No eligible compute nodes support this job under local demo policy")

    selected = sorted(
        eligible_candidates,
        key=lambda candidate: (
            -candidate["score"],
            candidate["estimated_latency_minutes"],
            candidate["estimated_cost_usd"],
            candidate["node_id"],
        ),
    )[0]
    selected_node = _node_by_id(compute_nodes, selected["node_id"])
    fallback_node_id = _select_fallback_node_id(eligible_candidates, compute_nodes, selected)
    reasons = _selected_reasons(job, selected, selected_node, fallback_node_id)

    return {
        "id": new_id("route"),
        "job_id": job["id"],
        "selected_node_id": selected["node_id"],
        "selected_ground_station_id": selected.get("selected_ground_station_id"),
        "fallback_node_id": fallback_node_id,
        "estimated_latency_minutes": selected["estimated_latency_minutes"],
        "estimated_cost_usd": selected["estimated_cost_usd"],
        "confidence": round(max(0.5, min(0.99, selected["score"] / 100)), 2),
        "reasons": reasons,
        "candidate_scores": candidates,
    }


def _build_raw_candidate(
    job: Dict[str, Any],
    node: Dict[str, Any],
    ground_stations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    station = select_ground_station(ground_stations)
    contact_minutes = next_contact_minutes(node)
    if node["type"] == "orbital":
        station_latency = float(station["latency_minutes"]) if station else 0.0
        estimated_latency = contact_minutes + float(node["latency_minutes"]) + station_latency
        selected_ground_station_id = station["id"] if station else None
    else:
        estimated_latency = float(node["latency_minutes"])
        selected_ground_station_id = None

    return {
        "node": node,
        "node_id": node["id"],
        "selected_ground_station_id": selected_ground_station_id,
        "model_supported": job["job_type"] in node["supported_models"],
        "policy_allowed": node_is_allowed(node),
        "preference_allowed": _preference_allows_node(job, node),
        "estimated_latency_minutes": round(estimated_latency, 2),
        "estimated_cost_usd": estimate_cost_usd(job, node),
        "contact_minutes": contact_minutes,
    }


def _score_candidates(
    job: Dict[str, Any],
    raw_candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    eligible_raw = [
        candidate
        for candidate in raw_candidates
        if candidate["model_supported"]
        and candidate["policy_allowed"]
        and candidate["preference_allowed"]
    ]
    latency_range = _range_for(eligible_raw, "estimated_latency_minutes")
    cost_range = _range_for(eligible_raw, "estimated_cost_usd")
    weights = _weights_for_priority(job["priority"])

    scored = [
        _score_candidate(job, candidate, latency_range, cost_range, weights)
        for candidate in raw_candidates
    ]
    return sorted(scored, key=lambda candidate: candidate["node_id"])


def _score_candidate(
    job: Dict[str, Any],
    candidate: Dict[str, Any],
    latency_range: Tuple[float, float],
    cost_range: Tuple[float, float],
    weights: Dict[str, float],
) -> Dict[str, Any]:
    node = candidate["node"]
    eligible = (
        candidate["model_supported"]
        and candidate["policy_allowed"]
        and candidate["preference_allowed"]
    )

    if eligible:
        model_support_score = weights["model_support"]
        latency_score = _inverse_score(
            candidate["estimated_latency_minutes"],
            latency_range,
            weights["latency"],
        )
        cost_score = _inverse_score(
            candidate["estimated_cost_usd"],
            cost_range,
            weights["cost"],
        )
        availability_score = round(float(node["availability"]) * weights["availability"], 2)
        contact_score = _contact_score(candidate["contact_minutes"], weights["contact"])
        preference_score = _preference_score(job, node, candidate, cost_range, latency_range, weights)
        compliance_score = weights["compliance"]
    else:
        model_support_score = weights["model_support"] if candidate["model_supported"] else 0.0
        latency_score = 0.0
        cost_score = 0.0
        availability_score = 0.0
        contact_score = 0.0
        preference_score = 0.0
        compliance_score = weights["compliance"] if candidate["policy_allowed"] else 0.0

    score = round(
        model_support_score
        + latency_score
        + cost_score
        + availability_score
        + contact_score
        + preference_score
        + compliance_score,
        2,
    )
    if not eligible:
        score = 0.0

    return {
        "node_id": candidate["node_id"],
        "score": score,
        "eligible": eligible,
        "model_support_score": round(model_support_score, 2),
        "latency_score": round(latency_score, 2),
        "cost_score": round(cost_score, 2),
        "availability_score": round(availability_score, 2),
        "contact_score": round(contact_score, 2),
        "preference_score": round(preference_score, 2),
        "compliance_score": round(compliance_score, 2),
        "estimated_latency_minutes": candidate["estimated_latency_minutes"],
        "estimated_cost_usd": candidate["estimated_cost_usd"],
        "available": eligible,
        "selected_ground_station_id": candidate.get("selected_ground_station_id"),
        "reasons": _candidate_reasons(job, candidate, eligible),
    }


def _range_for(candidates: List[Dict[str, Any]], field: str) -> Tuple[float, float]:
    if not candidates:
        return (0.0, 1.0)
    values = [float(candidate[field]) for candidate in candidates]
    return (min(values), max(values))


def _inverse_score(value: float, value_range: Tuple[float, float], max_points: float) -> float:
    minimum, maximum = value_range
    if maximum <= minimum:
        return round(max_points, 2)
    normalized = (maximum - float(value)) / (maximum - minimum)
    return round(max(0.0, min(max_points, normalized * max_points)), 2)


def _contact_score(contact_minutes: float, max_points: float) -> float:
    score = max_points * (1 - min(float(contact_minutes), 60.0) / 60.0)
    return round(max(0.0, min(max_points, score)), 2)


def _preference_score(
    job: Dict[str, Any],
    node: Dict[str, Any],
    candidate: Dict[str, Any],
    cost_range: Tuple[float, float],
    latency_range: Tuple[float, float],
    weights: Dict[str, float],
) -> float:
    preference = job["compute_preference"]
    max_points = weights["preference"]
    if preference == "orbital_if_available":
        return max_points if node["type"] == "orbital" else 0.0
    if preference == "ground_only":
        return max_points if node["type"] == "ground_cloud" else 0.0
    if preference == "cheapest":
        return _inverse_score(candidate["estimated_cost_usd"], cost_range, max_points)
    if preference == "fastest":
        return _inverse_score(candidate["estimated_latency_minutes"], latency_range, max_points)
    return 0.0


def _weights_for_priority(priority: str) -> Dict[str, float]:
    if priority == "fastest":
        return {
            "model_support": 25,
            "latency": 25,
            "cost": 10,
            "availability": 15,
            "contact": 10,
            "preference": 10,
            "compliance": 5,
        }
    if priority == "cheapest":
        return {
            "model_support": 25,
            "latency": 10,
            "cost": 25,
            "availability": 15,
            "contact": 10,
            "preference": 10,
            "compliance": 5,
        }
    return {
        "model_support": 25,
        "latency": 15,
        "cost": 10,
        "availability": 25,
        "contact": 10,
        "preference": 10,
        "compliance": 5,
    }


def _preference_allows_node(job: Dict[str, Any], node: Dict[str, Any]) -> bool:
    if job["compute_preference"] == "ground_only" and node["type"] == "orbital":
        return False
    return True


def _candidate_reasons(
    job: Dict[str, Any],
    candidate: Dict[str, Any],
    eligible: bool,
) -> List[str]:
    node = candidate["node"]
    reasons: List[str] = []
    if candidate["model_supported"]:
        reasons.append("Supports requested job type")
    else:
        reasons.append("Does not support requested job type")
    if candidate["policy_allowed"]:
        reasons.append("Allowed by local non-defense demo policy")
    else:
        reasons.append("Blocked by local demo policy")
    if candidate["preference_allowed"]:
        reasons.append("Allowed by compute preference")
    else:
        reasons.append("Excluded by compute preference")
    if node["type"] == "orbital":
        reasons.append(f"Next contact window in {int(candidate['contact_minutes'])} minutes")
    else:
        reasons.append("Ground cloud contact is immediately available")
    if candidate["estimated_cost_usd"] > float(job["max_cost_usd"]):
        reasons.append("Estimated cost exceeds requested max cost")
    if eligible:
        reasons.append("Eligible candidate")
    return reasons


def _selected_reasons(
    job: Dict[str, Any],
    selected: Dict[str, Any],
    selected_node: Dict[str, Any],
    fallback_node_id: Optional[str],
) -> List[str]:
    reasons = [
        (
            f"Selected {selected_node['id']} because it supports "
            f"{job['sensor']} {job['job_type']}."
        ),
        (
            f"Estimated route latency is "
            f"{selected['estimated_latency_minutes']:.0f} minutes."
        ),
        f"Estimated route cost is ${selected['estimated_cost_usd']:.2f}.",
        f"Matched priority '{job['priority']}' and compute preference '{job['compute_preference']}'.",
    ]
    if selected_node["type"] == "orbital":
        reasons.insert(
            1,
            f"Next orbital contact window is in {int(_selected_contact(selected))} minutes.",
        )
    else:
        reasons.insert(1, "Cloud fallback path is immediately reachable.")
    if fallback_node_id and selected_node["type"] == "orbital":
        reasons.append(f"Fallback node is {fallback_node_id}.")
    return reasons


def _selected_contact(selected: Dict[str, Any]) -> float:
    for reason in selected.get("reasons", []):
        prefix = "Next contact window in "
        if reason.startswith(prefix):
            return float(reason[len(prefix) :].split(" ")[0])
    return 0.0


def _select_fallback_node_id(
    eligible_candidates: List[Dict[str, Any]],
    compute_nodes: List[Dict[str, Any]],
    selected: Dict[str, Any],
) -> Optional[str]:
    cloud_node_ids = {
        node["id"]
        for node in compute_nodes
        if node["type"] == "ground_cloud" and node["id"] != selected["node_id"]
    }
    cloud_candidates = [
        candidate
        for candidate in eligible_candidates
        if candidate["node_id"] in cloud_node_ids
    ]
    if not cloud_candidates:
        return None
    return sorted(
        cloud_candidates,
        key=lambda candidate: (
            -candidate["score"],
            candidate["estimated_latency_minutes"],
            candidate["estimated_cost_usd"],
            candidate["node_id"],
        ),
    )[0]["node_id"]


def _node_by_id(nodes: List[Dict[str, Any]], node_id: str) -> Dict[str, Any]:
    for node in nodes:
        if node["id"] == node_id:
            return node
    raise KeyError(node_id)
