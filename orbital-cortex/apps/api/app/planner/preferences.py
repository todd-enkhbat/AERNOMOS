"""Soft preference scoring for feasible / conditional mission plans."""

from __future__ import annotations

from typing import Dict, List, Tuple

from app.db.truth import TruthStatus
from app.planner.types import DraftPlan, FeasibilityStatus, MissionPlannerContext, PlanPattern

# Bump when weights, constraints, or estimate formulas change.
PLANNER_CONFIG_VERSION = "2026.07.17-1"

# Fixed weights (sum ≈ 100). Versioned with PLANNER_CONFIG_VERSION.
WEIGHTS: Dict[str, float] = {
    "latency": 22.0,
    "cost": 12.0,
    "data_movement": 14.0,
    "recency": 12.0,
    "onboard": 8.0,
    "customer_environment": 12.0,
    "confidence": 10.0,
    "simplicity": 10.0,
}

PATTERN_STEP_COUNTS = {
    PlanPattern.EXISTING_IMAGERY_CLOUD: 4,
    PlanPattern.EXISTING_IMAGERY_EDGE: 4,
    PlanPattern.SATELLITE_GROUND_CLOUD: 5,
    PlanPattern.ONBOARD_PROCESSING: 4,
}


def score_plans(
    plans: List[DraftPlan],
    ctx: MissionPlannerContext,
) -> List[DraftPlan]:
    """Score all plans; ineligible plans get score 0 but keep breakdown zeros."""
    rankable = [
        p
        for p in plans
        if p.feasibility_status
        in (FeasibilityStatus.FEASIBLE, FeasibilityStatus.CONDITIONAL)
    ]
    latency_range = _range_for(
        [
            p.estimated_total_time_seconds
            for p in rankable
            if p.estimated_total_time_seconds is not None
        ]
    )
    cost_range = _range_for(
        [
            p.estimated_total_cost_usd
            for p in rankable
            if p.estimated_total_cost_usd is not None
            and p.cost_truth_status != TruthStatus.UNAVAILABLE.value
        ]
    )
    movement_range = _range_for(
        [
            p.estimated_data_movement_mb
            for p in rankable
            if p.estimated_data_movement_mb is not None
        ]
    )
    recency_ages = [_candidate_age_days(p, ctx) for p in rankable]
    recency_ages_known = [a for a in recency_ages if a is not None]
    recency_range = _range_for(recency_ages_known)

    for plan in plans:
        if plan.feasibility_status == FeasibilityStatus.REJECTED:
            plan.score = 0.0
            plan.score_breakdown = {k: 0.0 for k in WEIGHTS}
            plan.confidence = None
            continue

        breakdown: Dict[str, float] = {}
        breakdown["latency"] = _inverse_score(
            plan.estimated_total_time_seconds, latency_range, WEIGHTS["latency"]
        )
        if (
            plan.estimated_total_cost_usd is not None
            and plan.cost_truth_status != TruthStatus.UNAVAILABLE.value
        ):
            breakdown["cost"] = _inverse_score(
                plan.estimated_total_cost_usd, cost_range, WEIGHTS["cost"]
            )
        else:
            breakdown["cost"] = 0.0  # unknown cost contributes nothing

        breakdown["data_movement"] = _inverse_score(
            plan.estimated_data_movement_mb, movement_range, WEIGHTS["data_movement"]
        )
        age = _candidate_age_days(plan, ctx)
        breakdown["recency"] = _inverse_score(age, recency_range, WEIGHTS["recency"])

        breakdown["onboard"] = (
            WEIGHTS["onboard"]
            if plan.pattern == PlanPattern.ONBOARD_PROCESSING
            else 0.0
        )
        prefer_edge = _prefers_customer_env(ctx)
        if prefer_edge and plan.pattern == PlanPattern.EXISTING_IMAGERY_EDGE:
            breakdown["customer_environment"] = WEIGHTS["customer_environment"]
        elif (not prefer_edge) and plan.pattern == PlanPattern.EXISTING_IMAGERY_CLOUD:
            breakdown["customer_environment"] = WEIGHTS["customer_environment"] * 0.5
        else:
            breakdown["customer_environment"] = 0.0

        # Confidence proxy: feasible > conditional; fresher orbital/catalog better.
        confidence_pts = WEIGHTS["confidence"]
        if plan.feasibility_status == FeasibilityStatus.CONDITIONAL:
            confidence_pts *= 0.45
        if ctx.orbital_truth_status == TruthStatus.STALE.value:
            confidence_pts *= 0.85
        breakdown["confidence"] = round(confidence_pts, 2)

        expected_steps = PATTERN_STEP_COUNTS.get(plan.pattern, len(plan.steps))
        simplicity = WEIGHTS["simplicity"] * (
            expected_steps / max(len(plan.steps), expected_steps, 1)
        )
        # Prefer existing imagery over acquisition when both are feasible.
        if plan.pattern in (
            PlanPattern.EXISTING_IMAGERY_CLOUD,
            PlanPattern.EXISTING_IMAGERY_EDGE,
        ):
            simplicity = min(WEIGHTS["simplicity"], simplicity + 2.0)
        breakdown["simplicity"] = round(simplicity, 2)

        plan.score_breakdown = {k: round(v, 2) for k, v in breakdown.items()}
        plan.score = round(sum(breakdown.values()), 2)
        # Confidence stored on MissionPlan is 0..1; derive from score.
        plan.confidence = round(max(0.05, min(0.95, plan.score / 100.0)), 3)

    return sorted(
        plans,
        key=lambda p: (
            p.feasibility_status == FeasibilityStatus.REJECTED,
            p.feasibility_status == FeasibilityStatus.CONDITIONAL,
            -p.score,
            p.pattern.value,
            p.plan_hash,
        ),
    )


def select_recommendation(ranked: List[DraftPlan]) -> DraftPlan | None:
    """Pick the best feasible plan; fall back to best conditional."""
    feasible = [p for p in ranked if p.feasibility_status == FeasibilityStatus.FEASIBLE]
    if feasible:
        return feasible[0]
    conditional = [
        p for p in ranked if p.feasibility_status == FeasibilityStatus.CONDITIONAL
    ]
    if conditional:
        return conditional[0]
    return None


def _prefers_customer_env(ctx: MissionPlannerContext) -> bool:
    preferred = (ctx.preferred_compute_location or "").strip().lower()
    return any(h in preferred for h in ("edge", "onprem", "on-prem", "customer", "local"))


def _candidate_age_days(plan: DraftPlan, ctx: MissionPlannerContext) -> float | None:
    if not plan.candidate_id:
        return None
    for item in ctx.catalog_snapshot:
        if item.get("id") != plan.candidate_id:
            continue
        acquired = item.get("acquisition_time")
        if not acquired:
            return None
        from datetime import datetime, timezone

        if isinstance(acquired, str):
            try:
                dt = datetime.fromisoformat(acquired.replace("Z", "+00:00"))
            except ValueError:
                return None
        elif isinstance(acquired, datetime):
            dt = acquired
        else:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (ctx.now_utc - dt.astimezone(timezone.utc)).total_seconds() / 86400.0)
    return None


def _range_for(values: List[float]) -> Tuple[float, float]:
    if not values:
        return (0.0, 1.0)
    return (min(values), max(values))


def _inverse_score(
    value: float | None,
    value_range: Tuple[float, float],
    max_points: float,
) -> float:
    if value is None:
        return 0.0
    minimum, maximum = value_range
    if maximum <= minimum:
        return round(max_points, 2)
    normalized = (maximum - float(value)) / (maximum - minimum)
    return round(max(0.0, min(max_points, normalized * max_points)), 2)
