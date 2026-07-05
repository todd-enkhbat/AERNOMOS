"""Hard-constraint filter: feasibility checks that run before soft scoring.

A node that fails any hard constraint is ineligible and excluded from
scoring entirely; each failure is recorded as a structured reason so the
API can show why a node was eliminated (the "binding constraint").
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.cost_model import estimate_cost_usd
from app.core.policy_engine import BLOCKED_TAGS, REQUIRED_TAG

# Estimated data volume a job must downlink, by job type (MB). Used to check
# whether the payload fits in the next contact window's downlink budget.
JOB_DATA_VOLUME_MB: Dict[str, float] = {
    "ship_detection": 850.0,
    "crop_health": 600.0,
    "disaster_response": 1200.0,
}


def _failure(constraint: str, detail: str) -> Dict[str, str]:
    return {"constraint": constraint, "detail": detail}


def evaluate_hard_constraints(
    job: Dict[str, Any],
    node: Dict[str, Any],
    next_window: Optional[Dict[str, Any]],
    estimated_latency_minutes: float,
) -> List[Dict[str, str]]:
    """Return structured failures; an empty list means the node is eligible."""
    failures: List[Dict[str, str]] = []

    if job["job_type"] not in node["supported_models"]:
        failures.append(
            _failure(
                "model_unsupported",
                f"Node does not support model '{job['job_type']}' "
                f"(supports: {', '.join(node['supported_models'])}).",
            )
        )

    tags = set(node.get("compliance_tags", []))
    if REQUIRED_TAG not in tags:
        failures.append(
            _failure(
                "compliance_mismatch",
                f"Missing required '{REQUIRED_TAG}' compliance tag.",
            )
        )
    blocked = sorted(tags.intersection(BLOCKED_TAGS))
    if blocked:
        failures.append(
            _failure(
                "compliance_mismatch",
                f"Blocked compliance tags present: {', '.join(blocked)}.",
            )
        )

    if job["compute_preference"] == "ground_only" and node["type"] == "orbital":
        failures.append(
            _failure(
                "preference_exclusion",
                "Job requires ground-only compute; orbital node excluded.",
            )
        )

    estimated_cost = estimate_cost_usd(job, node)
    if estimated_cost > float(job["max_cost_usd"]):
        failures.append(
            _failure(
                "budget_exceeded",
                f"Estimated cost ${estimated_cost:.2f} exceeds the "
                f"${float(job['max_cost_usd']):.2f} job budget.",
            )
        )

    if node["type"] == "orbital":
        if next_window is None:
            failures.append(
                _failure(
                    "no_contact_window",
                    "No contact window cached within the pass horizon; "
                    "downlink cannot be scheduled.",
                )
            )
        else:
            required_mb = JOB_DATA_VOLUME_MB.get(job["job_type"], 1000.0)
            available_mb = float(next_window["est_downlink_mb"])
            if required_mb > available_mb:
                failures.append(
                    _failure(
                        "downlink_infeasible",
                        f"Job needs ~{required_mb:.0f} MB but the next pass "
                        f"only supports ~{available_mb:.0f} MB.",
                    )
                )

    deadline = job.get("deadline_minutes")
    if deadline is not None and estimated_latency_minutes > float(deadline):
        failures.append(
            _failure(
                "deadline_infeasible",
                f"Estimated latency {estimated_latency_minutes:.0f} min exceeds "
                f"the {float(deadline):.0f} min deadline.",
            )
        )

    return failures
