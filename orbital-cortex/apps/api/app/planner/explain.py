"""Structured plain-language explanations for plan recommendations.

No LLM required — fields are deterministic strings the UI can render.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.db.truth import TruthStatus
from app.planner.types import (
    DraftPlan,
    FeasibilityStatus,
    MissionPlannerContext,
    PlanPattern,
)


def explain_plan(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
    *,
    recommended: bool,
    all_plans: List[DraftPlan],
) -> Dict[str, Any]:
    """Build structured explanation fields for a plan."""
    why = _why_recommended(plan, ctx, recommended=recommended, all_plans=all_plans)
    executable_now, needs_provider = _executable_split(plan)
    assumptions = _top_assumptions(plan, ctx)
    missing = _missing_integrations(plan, ctx)
    return {
        "why_recommended": why,
        "executable_now": executable_now,
        "needs_provider": needs_provider,
        "top_assumptions": assumptions,
        "missing_integrations": missing,
        "feasibility_status": plan.feasibility_status.value,
        "rejection_reasons": [
            {"code": r.code, "message": r.message} for r in plan.rejection_reasons
        ],
        "score": plan.score,
        "score_breakdown": plan.score_breakdown,
        "pattern": plan.pattern.value,
    }


def _why_recommended(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
    *,
    recommended: bool,
    all_plans: List[DraftPlan],
) -> str:
    if not recommended:
        if plan.feasibility_status == FeasibilityStatus.REJECTED:
            reasons = (
                "; ".join(r.message for r in plan.rejection_reasons[:2])
                or "hard constraints failed"
            )
            return f"Not recommended: {reasons}"
        if plan.feasibility_status == FeasibilityStatus.CONDITIONAL:
            return (
                "Not the primary recommendation — this path is conditional on "
                "missing provider integrations."
            )
        return (
            f"Feasible alternative (score {plan.score:.1f}); "
            "another plan ranked higher."
        )

    if plan.pattern == PlanPattern.EXISTING_IMAGERY_CLOUD:
        base = (
            "Recommended because existing catalog imagery can be retrieved and "
            "processed in cloud without waiting for a new satellite acquisition."
        )
    elif plan.pattern == PlanPattern.EXISTING_IMAGERY_EDGE:
        base = (
            "Recommended because existing catalog imagery can be processed in the "
            "preferred customer environment with less data leaving that boundary."
        )
    elif plan.pattern == PlanPattern.SATELLITE_GROUND_CLOUD:
        base = (
            "Recommended as the best available path, but acquisition remains "
            "conditional until a tasking API is connected."
        )
    else:
        base = "Recommended by structured scoring among available plan shells."

    latency = plan.estimated_total_time_seconds
    latency_txt = (
        f" Estimated duration is about {latency / 60.0:.0f} minutes "
        f"({plan.duration_truth_status})."
        if latency is not None
        else ""
    )
    cost_txt = (
        " Cost is UNAVAILABLE — no real pricing source is connected."
        if plan.cost_truth_status == TruthStatus.UNAVAILABLE.value
        else f" Estimated cost is ${plan.estimated_total_cost_usd:.2f}."
    )
    rivals = [
        p
        for p in all_plans
        if p is not plan and p.feasibility_status != FeasibilityStatus.REJECTED
    ]
    rival_txt = ""
    if rivals:
        other = rivals[0]
        rival_txt = (
            f" It outranked '{other.summary}' on structured preference scoring "
            f"({plan.score:.1f} vs {other.score:.1f})."
        )
    return base + latency_txt + cost_txt + rival_txt


def _executable_split(plan: DraftPlan) -> tuple[List[str], List[str]]:
    executable: List[str] = []
    needs: List[str] = []
    for step in plan.steps:
        label = f"{step.sequence}. {step.title}"
        if (
            step.feasibility_status == FeasibilityStatus.FEASIBLE.value
            and step.truth_status != TruthStatus.UNAVAILABLE.value
        ):
            executable.append(label)
        else:
            needs.append(
                f"{label} — {step.rejection_reason or step.truth_status}"
            )
    if plan.pattern in (
        PlanPattern.EXISTING_IMAGERY_CLOUD,
        PlanPattern.EXISTING_IMAGERY_EDGE,
    ):
        if plan.feasibility_status == FeasibilityStatus.FEASIBLE:
            executable = [f"{s.sequence}. {s.title}" for s in plan.steps]
            needs = []
        elif plan.feasibility_status == FeasibilityStatus.CONDITIONAL:
            needs = [r.message for r in plan.rejection_reasons] or needs
    return executable, needs


def _top_assumptions(plan: DraftPlan, ctx: MissionPlannerContext) -> List[str]:
    out: List[str] = []
    for item in plan.assumptions:
        if isinstance(item, dict):
            detail = item.get("detail") or item.get("key")
            if detail:
                out.append(str(detail))
        else:
            out.append(str(item))
    if plan.duration_method:
        out.append(f"Duration method: {plan.duration_method} ({plan.duration_truth_status}).")
    if plan.cost_truth_status == TruthStatus.UNAVAILABLE.value:
        out.append("Cost is unavailable — pricing providers are not connected.")
    if ctx.orbital_truth_status == TruthStatus.STALE.value and plan.pattern in (
        PlanPattern.SATELLITE_GROUND_CLOUD,
        PlanPattern.ONBOARD_PROCESSING,
    ):
        out.append(
            f"Orbital data snapshot '{ctx.tle_snapshot_id}' is STALE; "
            "contact geometry may be outdated."
        )
    return out[:8]


def _missing_integrations(plan: DraftPlan, ctx: MissionPlannerContext) -> List[str]:
    missing: List[str] = []
    codes = {r.code for r in plan.rejection_reasons}
    if "tasking_api_unavailable" in codes or plan.pattern == PlanPattern.SATELLITE_GROUND_CLOUD:
        missing.append("Satellite tasking / reservation API")
    if "onboard_provider_unavailable" in codes or plan.pattern == PlanPattern.ONBOARD_PROCESSING:
        missing.append("Onboard processing provider")
    if "customer_edge_unspecified" in codes:
        missing.append("Customer edge environment configuration")
    if "cost_unavailable" in codes or plan.cost_truth_status == TruthStatus.UNAVAILABLE.value:
        missing.append("Provider pricing / cost API")
    if not ctx.catalog_snapshot and plan.pattern in (
        PlanPattern.EXISTING_IMAGERY_CLOUD,
        PlanPattern.EXISTING_IMAGERY_EDGE,
    ):
        missing.append("Catalog discovery results for this mission")
    # Deduplicate preserving order
    seen = set()
    ordered: List[str] = []
    for item in missing:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
