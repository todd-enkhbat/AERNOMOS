"""Deterministic weighted routing scorer with a hard/soft constraint split.

Hard constraints (app/routing/constraints.py) decide *feasibility*: nodes
that fail any are ineligible and never scored. Soft weighted scoring ranks
the survivors. Every candidate carries a structured explanation: recorded
hard-constraint failures with the binding constraint, per-factor sub-scores,
and the weight table used.

compute_routing_decision() is pure and deterministic given its inputs
(job, nodes, stations, next windows, decision time), which is what makes
byte-for-byte replay possible.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.cost_model import estimate_cost_usd
from app.core.storage import new_id, utc_now
from app.routing.constraints import evaluate_hard_constraints

# Bump when scoring weights, constraints, or formulas change: replay compares
# decisions computed under the same config version.
ROUTING_CONFIG_VERSION = "2026.07.05-1"

# Contact wait assumed when a satellite has no cached pass (cold cache or no
# visibility in the horizon): score it like a worst-case one-hour wait.
NO_WINDOW_WAIT_MINUTES = 60.0


def compute_routing_decision(
    job: Dict[str, Any],
    compute_nodes: List[Dict[str, Any]],
    ground_stations: List[Dict[str, Any]],
    next_windows: Optional[Dict[str, Dict[str, Any]]] = None,
    now_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """Pure decision content (no generated id). Deterministic given inputs.

    next_windows maps satellite_id -> next contact window (may be in progress).
    """
    next_windows = next_windows or {}
    now = now_utc or utc_now()
    stations_by_id = {station["id"]: station for station in ground_stations}

    raw_candidates = [
        _build_raw_candidate(job, node, next_windows.get(node.get("satellite_id") or ""), stations_by_id, now)
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
    fallback_candidate = _select_fallback_candidate(eligible_candidates, compute_nodes, selected)
    fallback_node_id = fallback_candidate["node_id"] if fallback_candidate else None
    reasons = _selected_reasons(job, selected, selected_node, fallback_candidate)

    return {
        "job_id": job["id"],
        "selected_node_id": selected["node_id"],
        "selected_ground_station_id": selected.get("selected_ground_station_id"),
        "fallback_node_id": fallback_node_id,
        "estimated_latency_minutes": selected["estimated_latency_minutes"],
        "estimated_cost_usd": selected["estimated_cost_usd"],
        "confidence": round(max(0.5, min(0.99, selected["score"] / 100)), 2),
        "config_version": ROUTING_CONFIG_VERSION,
        "decided_at_utc": now,
        "reasons": reasons,
        "candidate_scores": candidates,
    }


def build_routing_decision(
    job: Dict[str, Any],
    compute_nodes: List[Dict[str, Any]],
    ground_stations: List[Dict[str, Any]],
    next_windows: Optional[Dict[str, Dict[str, Any]]] = None,
    now_utc: Optional[str] = None,
) -> Dict[str, Any]:
    content = compute_routing_decision(
        job, compute_nodes, ground_stations, next_windows, now_utc
    )
    return {"id": new_id("route"), **content}


def _contact_wait_minutes(window: Optional[Dict[str, Any]], now_iso: str) -> Optional[float]:
    """Minutes until AOS; 0 when the pass is already in progress."""
    if window is None:
        return None
    now = datetime.fromisoformat(now_iso)
    aos = datetime.fromisoformat(window["aos_utc"])
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    wait_s = (aos - now).total_seconds()
    return round(max(0.0, wait_s / 60.0), 2)


def _build_raw_candidate(
    job: Dict[str, Any],
    node: Dict[str, Any],
    next_window: Optional[Dict[str, Any]],
    stations_by_id: Dict[str, Dict[str, Any]],
    now_iso: str,
) -> Dict[str, Any]:
    if node["type"] == "orbital":
        wait = _contact_wait_minutes(next_window, now_iso)
        contact_minutes = wait if wait is not None else NO_WINDOW_WAIT_MINUTES
        station = (
            stations_by_id.get(next_window["ground_station_id"]) if next_window else None
        )
        station_latency = float(station["latency_minutes"]) if station else 0.0
        estimated_latency = contact_minutes + float(node["latency_minutes"]) + station_latency
        selected_ground_station_id = station["id"] if station else None
    else:
        contact_minutes = 0.0
        estimated_latency = float(node["latency_minutes"])
        selected_ground_station_id = None
        next_window = None

    estimated_latency = round(estimated_latency, 2)
    failures = evaluate_hard_constraints(job, node, next_window, estimated_latency)
    failed_constraints = {failure["constraint"] for failure in failures}

    return {
        "node": node,
        "node_id": node["id"],
        "selected_ground_station_id": selected_ground_station_id,
        "hard_constraint_failures": failures,
        "model_supported": "model_unsupported" not in failed_constraints,
        "policy_allowed": "compliance_mismatch" not in failed_constraints,
        "preference_allowed": "preference_exclusion" not in failed_constraints,
        "estimated_latency_minutes": estimated_latency,
        "estimated_cost_usd": estimate_cost_usd(job, node),
        "contact_minutes": contact_minutes,
        "next_window": next_window,
    }


def _score_candidates(
    job: Dict[str, Any],
    raw_candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    eligible_raw = [
        candidate
        for candidate in raw_candidates
        if not candidate["hard_constraint_failures"]
    ]
    latency_range = _range_for(eligible_raw, "estimated_latency_minutes")
    cost_range = _range_for(eligible_raw, "estimated_cost_usd")
    weights = _weights_for_priority(job["priority"])

    scored = [
        _score_candidate(job, candidate, latency_range, cost_range, weights)
        for candidate in raw_candidates
    ]
    # Ranked: eligible by score (best first), then eliminated nodes.
    return sorted(
        scored,
        key=lambda candidate: (
            not candidate["eligible"],
            -candidate["score"],
            candidate["node_id"],
        ),
    )


def _score_candidate(
    job: Dict[str, Any],
    candidate: Dict[str, Any],
    latency_range: Tuple[float, float],
    cost_range: Tuple[float, float],
    weights: Dict[str, float],
) -> Dict[str, Any]:
    node = candidate["node"]
    eligible = not candidate["hard_constraint_failures"]

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

    window = candidate.get("next_window")
    failures = candidate["hard_constraint_failures"]
    return {
        "node_id": candidate["node_id"],
        "score": score,
        "eligible": eligible,
        "hard_constraint_failures": failures,
        "binding_constraint": failures[0]["constraint"] if failures else None,
        "weights": weights,
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
        "next_contact_minutes": round(float(candidate["contact_minutes"]), 2),
        "next_aos_utc": window["aos_utc"] if window else None,
        "next_max_elevation_deg": window["max_elevation_deg"] if window else None,
        "est_downlink_mb": window["est_downlink_mb"] if window else None,
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
    for failure in candidate["hard_constraint_failures"]:
        reasons.append(f"Hard constraint [{failure['constraint']}]: {failure['detail']}")
    if candidate["model_supported"]:
        reasons.append(
            f"Supports {_label(job['job_type'])} on {node['gpu_class']} compute."
        )
    else:
        reasons.append(f"Does not support {_label(job['job_type'])}.")
    if candidate["policy_allowed"]:
        reasons.append("Passes non-defense commercial demo policy.")
    else:
        reasons.append("Blocked by local demo policy")
    if candidate["preference_allowed"]:
        reasons.append(f"Compatible with {_label(job['compute_preference'])} preference.")
    else:
        reasons.append(f"Excluded by {_label(job['compute_preference'])} preference.")
    if node["type"] == "orbital":
        window = candidate.get("next_window")
        if window:
            reasons.append(
                f"Next pass over {window['ground_station_id']} at {window['aos_utc']} "
                f"(in {candidate['contact_minutes']:.0f} min, max elevation "
                f"{window['max_elevation_deg']:.0f} deg, ~{window['est_downlink_mb']:.0f} MB downlink); "
                f"total route latency {candidate['estimated_latency_minutes']:.0f} minutes."
            )
        else:
            reasons.append(
                "No cached contact window in the pass horizon; assuming a "
                f"{NO_WINDOW_WAIT_MINUTES:.0f}-minute worst-case wait."
            )
    else:
        reasons.append(
            f"Ground cloud is immediately reachable with "
            f"{candidate['estimated_latency_minutes']:.0f} minute execution latency."
        )
    budget_failed = "budget_exceeded" in {
        failure["constraint"] for failure in candidate["hard_constraint_failures"]
    }
    if budget_failed:
        pass  # hard-constraint detail already recorded above
    elif candidate["estimated_cost_usd"] > float(job["max_cost_usd"]):
        reasons.append(
            f"Estimated cost ${candidate['estimated_cost_usd']:.2f} exceeds "
            f"requested cap ${float(job['max_cost_usd']):.2f}."
        )
    else:
        budget_delta = float(job["max_cost_usd"]) - candidate["estimated_cost_usd"]
        reasons.append(f"Estimated cost is ${budget_delta:.2f} under the job budget.")
    if eligible:
        reasons.append("Eligible candidate after model, policy, and preference checks.")
    return reasons


def _selected_reasons(
    job: Dict[str, Any],
    selected: Dict[str, Any],
    selected_node: Dict[str, Any],
    fallback_candidate: Optional[Dict[str, Any]],
) -> List[str]:
    budget_delta = float(job["max_cost_usd"]) - selected["estimated_cost_usd"]
    locality_reason = (
        "The route keeps first-pass inference close to the simulated orbital data path."
        if selected_node["type"] == "orbital"
        else "The route uses cloud fallback because immediate execution is favored."
    )
    reasons = [
        (
            f"Selected {selected_node['id']} because it supports "
            f"{job['sensor']} {_label(job['job_type'])} on {selected_node['gpu_class']}."
        ),
        locality_reason,
        (
            f"Route score {selected['score']:.1f}/100 balanced "
            f"{_label(job['priority'])} priority against "
            f"{_label(job['compute_preference'])} compute preference."
        ),
        (
            f"Estimated latency is {selected['estimated_latency_minutes']:.0f} minutes "
            f"and estimated cost is ${selected['estimated_cost_usd']:.2f}."
        ),
    ]
    if budget_delta >= 0:
        reasons.append(f"Route is ${budget_delta:.2f} under the max budget.")
    else:
        reasons.append(f"Route is ${abs(budget_delta):.2f} over the requested max budget.")
    if selected_node["type"] == "orbital":
        aos = selected.get("next_aos_utc")
        contact_text = (
            f"Next contact (AOS {aos}) is in {selected['next_contact_minutes']:.0f} minutes"
            if aos
            else "No cached pass; worst-case contact wait assumed"
        )
        reasons.insert(
            1,
            (
                f"{contact_text}; downlink is paired with "
                f"{selected.get('selected_ground_station_id') or 'the best available ground station'}."
            ),
        )
    else:
        reasons.insert(1, "Cloud fallback path is immediately reachable.")
    if fallback_candidate and selected_node["type"] == "orbital":
        cost_delta = fallback_candidate["estimated_cost_usd"] - selected["estimated_cost_usd"]
        latency_delta = selected["estimated_latency_minutes"] - fallback_candidate["estimated_latency_minutes"]
        if cost_delta > 0:
            reasons.append(
                f"Cloud fallback {fallback_candidate['node_id']} remains available, "
                f"but costs ${cost_delta:.2f} more in this simulation."
            )
        elif latency_delta > 0:
            reasons.append(
                f"Cloud fallback {fallback_candidate['node_id']} is "
                f"{latency_delta:.0f} minutes faster, but the orbital route wins on preference and locality."
            )
        else:
            reasons.append(f"Cloud fallback {fallback_candidate['node_id']} remains available.")
    return reasons


def _select_fallback_candidate(
    eligible_candidates: List[Dict[str, Any]],
    compute_nodes: List[Dict[str, Any]],
    selected: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
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
    )[0]


def _node_by_id(nodes: List[Dict[str, Any]], node_id: str) -> Dict[str, Any]:
    for node in nodes:
        if node["id"] == node_id:
            return node
    raise KeyError(node_id)


def _label(value: str) -> str:
    return value.replace("_", " ")
