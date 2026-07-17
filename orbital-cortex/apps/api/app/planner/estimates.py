"""Duration / data-movement / cost estimates with truth-status provenance.

Cost is UNAVAILABLE unless a real pricing source exists — never invent
fictional cloud/GPU prices.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from app.db.truth import TruthStatus
from app.planner.types import DraftPlan, MissionPlannerContext, PlanPattern, ProvenancedEstimate

# Heuristic transfer rate for ESTIMATED data movement latency (Mbps).
ASSUMED_TRANSFER_MBPS = 100.0
# Heuristic cloud/edge processing duration for ESTIMATED compute steps.
ASSUMED_PROCESS_SECONDS = 900.0
# Retrieval / staging overhead before transfer.
ASSUMED_RETRIEVE_SECONDS = 120.0


def apply_estimates(plan: DraftPlan, ctx: MissionPlannerContext) -> DraftPlan:
    """Fill duration, data movement, and cost on a draft plan."""
    size_bytes = _candidate_size_bytes(plan, ctx)
    size_mb = (float(size_bytes) / (1024.0 * 1024.0)) if size_bytes is not None else None

    data_est = estimate_data_movement_mb(size_mb)
    plan.estimated_data_movement_mb = data_est.value
    plan.data_movement_truth_status = data_est.truth_status
    plan.data_movement_method = data_est.method

    cost_est = estimate_cost_usd()
    plan.estimated_total_cost_usd = cost_est.value
    plan.cost_truth_status = cost_est.truth_status
    plan.cost_method = cost_est.method

    duration_s, duration_truth, duration_method, contact_wait_s = estimate_duration_seconds(
        plan, ctx, size_mb
    )
    plan.estimated_total_time_seconds = duration_s
    plan.duration_truth_status = duration_truth
    plan.duration_method = duration_method

    # Annotate steps with durations where applicable.
    _annotate_step_durations(plan, size_mb, contact_wait_s)
    return plan


def estimate_data_movement_mb(size_mb: Optional[float]) -> ProvenancedEstimate:
    if size_mb is None:
        return ProvenancedEstimate(
            value=None,
            truth_status=TruthStatus.UNAVAILABLE.value,
            method="catalog_size_missing",
            unit="MB",
        )
    return ProvenancedEstimate(
        value=round(size_mb, 2),
        truth_status=TruthStatus.ESTIMATED.value,
        method="candidate.estimated_size_bytes / 1MiB",
        source="mission_data_candidates.estimated_size_bytes",
        unit="MB",
    )


def estimate_cost_usd() -> ProvenancedEstimate:
    """No real pricing source is connected in Phase I."""
    return ProvenancedEstimate(
        value=None,
        truth_status=TruthStatus.UNAVAILABLE.value,
        method=None,
        source=None,
        unit="USD",
    )


def estimate_duration_seconds(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
    size_mb: Optional[float],
) -> Tuple[Optional[float], str, str, Optional[float]]:
    """Return (total_seconds, truth_status, method, contact_wait_seconds)."""
    transfer_s = _transfer_seconds(size_mb)
    process_s = ASSUMED_PROCESS_SECONDS
    retrieve_s = ASSUMED_RETRIEVE_SECONDS

    if plan.pattern in (
        PlanPattern.EXISTING_IMAGERY_CLOUD,
        PlanPattern.EXISTING_IMAGERY_EDGE,
    ):
        total = retrieve_s + (transfer_s or 0.0) + process_s
        method = (
            f"retrieve({retrieve_s:.0f}s) + transfer@"
            f"{ASSUMED_TRANSFER_MBPS:.0f}Mbps + process({process_s:.0f}s)"
        )
        return round(total, 1), TruthStatus.ESTIMATED.value, method, None

    contact_wait_s = _contact_wait_seconds(plan, ctx)
    if plan.pattern == PlanPattern.SATELLITE_GROUND_CLOUD:
        parts = []
        total = 0.0
        # Acquisition assumed near-term; contact wait is CALCULATED when known.
        acq_s = 600.0
        total += acq_s
        parts.append(f"acquisition_buffer({acq_s:.0f}s)")
        if contact_wait_s is not None:
            total += contact_wait_s
            parts.append(f"contact_wait_calculated({contact_wait_s:.0f}s)")
            truth = TruthStatus.CALCULATED.value
            method_prefix = "SGP4 contact wait + "
        else:
            truth = TruthStatus.ESTIMATED.value
            method_prefix = ""
        total += (transfer_s or 0.0) + process_s
        parts.append(
            f"transfer@{ASSUMED_TRANSFER_MBPS:.0f}Mbps + process({process_s:.0f}s)"
        )
        return (
            round(total, 1),
            truth if contact_wait_s is not None else TruthStatus.ESTIMATED.value,
            method_prefix + " + ".join(parts),
            contact_wait_s,
        )

    # Onboard: acquisition + onboard process + prioritized downlink wait.
    onboard_s = 300.0
    total = 600.0 + onboard_s
    if contact_wait_s is not None:
        total += contact_wait_s
        method = (
            f"acquisition_buffer(600s) + onboard({onboard_s:.0f}s) + "
            f"contact_wait_calculated({contact_wait_s:.0f}s)"
        )
        truth = TruthStatus.CALCULATED.value
    else:
        method = f"acquisition_buffer(600s) + onboard({onboard_s:.0f}s); contact wait unknown"
        truth = TruthStatus.ESTIMATED.value
    total += 120.0  # delivery
    return round(total, 1), truth, method, contact_wait_s


def estimates_for_hash(plan: DraftPlan) -> Dict[str, Any]:
    return {
        "duration_seconds": plan.estimated_total_time_seconds,
        "duration_truth_status": plan.duration_truth_status,
        "duration_method": plan.duration_method,
        "data_movement_mb": plan.estimated_data_movement_mb,
        "data_movement_truth_status": plan.data_movement_truth_status,
        "cost_usd": plan.estimated_total_cost_usd,
        "cost_truth_status": plan.cost_truth_status,
    }


def _candidate_size_bytes(plan: DraftPlan, ctx: MissionPlannerContext) -> Optional[int]:
    if not plan.candidate_id:
        return None
    for item in ctx.catalog_snapshot:
        if item.get("id") == plan.candidate_id:
            raw = item.get("estimated_size_bytes")
            return int(raw) if raw is not None else None
    return None


def _transfer_seconds(size_mb: Optional[float]) -> Optional[float]:
    if size_mb is None:
        return None
    return round((size_mb * 8.0) / ASSUMED_TRANSFER_MBPS, 1)


def _contact_wait_seconds(
    plan: DraftPlan, ctx: MissionPlannerContext
) -> Optional[float]:
    window = None
    if plan.contact_window_id:
        for w in ctx.contact_windows:
            if w.get("id") == plan.contact_window_id:
                window = w
                break
    elif ctx.contact_windows:
        window = ctx.contact_windows[0]
    if window is None:
        return None
    aos = window.get("aos_utc")
    if not aos:
        return None
    if isinstance(aos, str):
        try:
            aos_dt = datetime.fromisoformat(aos.replace("Z", "+00:00"))
        except ValueError:
            return None
    elif isinstance(aos, datetime):
        aos_dt = aos
    else:
        return None
    if aos_dt.tzinfo is None:
        aos_dt = aos_dt.replace(tzinfo=timezone.utc)
    wait = (aos_dt.astimezone(timezone.utc) - ctx.now_utc).total_seconds()
    return round(max(0.0, wait), 1)


def _annotate_step_durations(
    plan: DraftPlan,
    size_mb: Optional[float],
    contact_wait_s: Optional[float],
) -> None:
    transfer_s = _transfer_seconds(size_mb)
    for step in plan.steps:
        meta = dict(step.source_metadata or {})
        if step.step_type in ("retrieve_asset", "stage_asset"):
            step.duration_seconds = ASSUMED_RETRIEVE_SECONDS
            meta["duration_truth_status"] = TruthStatus.ESTIMATED.value
            meta["duration_method"] = "assumed_catalog_retrieve_overhead"
        elif step.step_type in ("transfer", "downlink", "delivery"):
            step.duration_seconds = transfer_s
            meta["duration_truth_status"] = (
                TruthStatus.ESTIMATED.value
                if transfer_s is not None
                else TruthStatus.UNAVAILABLE.value
            )
            meta["duration_method"] = f"size_mb * 8 / {ASSUMED_TRANSFER_MBPS} Mbps"
        elif step.step_type in ("process", "onboard_process", "cloud_process", "edge_process"):
            step.duration_seconds = ASSUMED_PROCESS_SECONDS
            meta["duration_truth_status"] = TruthStatus.ESTIMATED.value
            meta["duration_method"] = "assumed_inference_duration"
        elif step.step_type in ("wait_contact", "contact_window"):
            step.duration_seconds = contact_wait_s
            meta["duration_truth_status"] = (
                TruthStatus.CALCULATED.value
                if contact_wait_s is not None
                else TruthStatus.UNAVAILABLE.value
            )
            meta["duration_method"] = "SGP4/Skyfield contact window AOS − now"
            meta["tle_snapshot_id"] = plan.tle_snapshot_id
        elif step.step_type == "acquire":
            step.duration_seconds = 600.0
            meta["duration_truth_status"] = TruthStatus.ESTIMATED.value
            meta["duration_method"] = "acquisition_buffer_estimate"
        step.estimated_cost_usd = None
        meta["cost_truth_status"] = TruthStatus.UNAVAILABLE.value
        step.source_metadata = meta
