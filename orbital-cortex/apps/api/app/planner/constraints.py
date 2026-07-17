"""Hard constraints for mission plan feasibility.

Each check returns machine-readable reason codes plus human messages.
Failures reject the plan (or make it conditional when noted by the pattern).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from app.db.truth import AccessLevel, TruthStatus
from app.planner.types import (
    ConstraintFailure,
    DraftPlan,
    FeasibilityStatus,
    MissionPlannerContext,
    PlanPattern,
)

# Minimum fraction of AOI area covered by a candidate footprint.
AOI_COVERAGE_THRESHOLD = 0.05

# Access levels that allow catalog retrieval / public planning today.
USABLE_ACCESS = frozenset(
    {
        AccessLevel.PUBLIC_INFORMATION.value,
        AccessLevel.SANDBOX_AVAILABLE.value,
    }
)

# Patterns that require at least one catalog candidate.
IMAGERY_PATTERNS = frozenset(
    {
        PlanPattern.EXISTING_IMAGERY_CLOUD,
        PlanPattern.EXISTING_IMAGERY_EDGE,
    }
)

# Patterns that require a downlink contact window.
DOWNLINK_PATTERNS = frozenset(
    {
        PlanPattern.SATELLITE_GROUND_CLOUD,
        PlanPattern.ONBOARD_PROCESSING,
    }
)


def evaluate_hard_constraints(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    """Return all hard-constraint failures for a draft plan."""
    failures: List[ConstraintFailure] = []

    if plan.pattern in IMAGERY_PATTERNS:
        failures.extend(_check_data_exists(ctx))
        if ctx.catalog_snapshot:
            failures.extend(_check_footprint_coverage(plan, ctx))
            failures.extend(_check_data_freshness(plan, ctx))
            failures.extend(_check_data_volume(plan, ctx))
            failures.extend(_check_provider_access_catalog(ctx))

    failures.extend(_check_region_residency(ctx))
    failures.extend(_check_cost_cap(plan, ctx))
    failures.extend(_check_deadline(plan, ctx))

    if plan.pattern in DOWNLINK_PATTERNS:
        failures.extend(_check_contact_window(plan, ctx))

    if plan.pattern == PlanPattern.ONBOARD_PROCESSING:
        failures.append(
            ConstraintFailure(
                code="onboard_provider_unavailable",
                message=(
                    "No real onboard processing provider is connected. "
                    "This path is not executable today."
                ),
            )
        )

    if plan.pattern == PlanPattern.SATELLITE_GROUND_CLOUD:
        # Tasking / reservation APIs are not connected — handled as conditional
        # in the engine when this is the only structural gap.
        failures.append(
            ConstraintFailure(
                code="tasking_api_unavailable",
                message=(
                    "No satellite tasking or contact-reservation API is connected. "
                    "Acquisition and downlink remain conditional."
                ),
            )
        )

    if plan.pattern == PlanPattern.EXISTING_IMAGERY_EDGE:
        failures.extend(_check_edge_location(ctx))

    return failures


def apply_constraint_outcome(
    plan: DraftPlan,
    failures: List[ConstraintFailure],
) -> DraftPlan:
    """Mutate plan feasibility from hard-constraint results."""
    plan.rejection_reasons = list(failures)
    if not failures:
        plan.feasibility_status = FeasibilityStatus.FEASIBLE
        return plan

    codes = {f.code for f in failures}

    # Conditional: only missing provider integrations / environment gaps.
    conditional_codes = {"tasking_api_unavailable", "customer_edge_unspecified"}
    if codes and codes <= conditional_codes:
        if plan.pattern in (
            PlanPattern.SATELLITE_GROUND_CLOUD,
            PlanPattern.EXISTING_IMAGERY_EDGE,
        ):
            plan.feasibility_status = FeasibilityStatus.CONDITIONAL
            return plan

    # Onboard is always rejected today (no provider).
    if plan.pattern == PlanPattern.ONBOARD_PROCESSING:
        plan.feasibility_status = FeasibilityStatus.REJECTED
        return plan

    plan.feasibility_status = FeasibilityStatus.REJECTED
    return plan


def _check_data_exists(ctx: MissionPlannerContext) -> List[ConstraintFailure]:
    if ctx.catalog_snapshot:
        return []
    return [
        ConstraintFailure(
            code="data_missing",
            message=(
                "No catalog candidates are available for this mission. "
                "Run catalog discovery before planning existing-imagery paths."
            ),
        )
    ]


def _check_footprint_coverage(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    candidate_id = plan.candidate_id
    if not candidate_id:
        return [
            ConstraintFailure(
                code="aoi_uncovered",
                message="No catalog candidate was selected for AOI coverage checks.",
            )
        ]
    coverage = float(ctx.coverage_by_candidate.get(candidate_id, 0.0))
    if coverage < AOI_COVERAGE_THRESHOLD:
        return [
            ConstraintFailure(
                code="aoi_uncovered",
                message=(
                    f"Selected scene covers {coverage:.1%} of the AOI "
                    f"(minimum {AOI_COVERAGE_THRESHOLD:.0%} required)."
                ),
            )
        ]
    return []


def _check_data_freshness(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    if ctx.max_age_days is None:
        return []
    candidate = _candidate(ctx, plan.candidate_id)
    if candidate is None:
        return []
    acquired = _parse_dt(candidate.get("acquisition_time"))
    if acquired is None:
        return [
            ConstraintFailure(
                code="data_stale",
                message=(
                    "Catalog candidate acquisition time is missing; "
                    "freshness cannot be verified."
                ),
            )
        ]
    age_days = (ctx.now_utc - acquired.astimezone(timezone.utc)).total_seconds() / 86400.0
    if age_days > float(ctx.max_age_days):
        return [
            ConstraintFailure(
                code="data_stale",
                message=(
                    f"Scene age is {age_days:.1f} days, exceeding the "
                    f"{ctx.max_age_days}-day freshness preference."
                ),
            )
        ]
    return []


def _check_data_volume(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    if ctx.max_data_volume_mb is None:
        return []
    candidate = _candidate(ctx, plan.candidate_id)
    if candidate is None:
        return []
    size_bytes = candidate.get("estimated_size_bytes")
    if size_bytes is None:
        return []
    size_mb = float(size_bytes) / (1024.0 * 1024.0)
    if size_mb > float(ctx.max_data_volume_mb):
        return [
            ConstraintFailure(
                code="data_volume_exceeded",
                message=(
                    f"Estimated scene size {size_mb:.0f} MB exceeds the "
                    f"{ctx.max_data_volume_mb:.0f} MB mission limit."
                ),
            )
        ]
    return []


def _check_provider_access_catalog(
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    # Planetary Computer STAC is public; treat catalog provider as usable.
    # If a candidate carries an explicit blocked access_level, fail.
    for item in ctx.catalog_snapshot:
        access = item.get("access_level")
        if access and access not in USABLE_ACCESS:
            return [
                ConstraintFailure(
                    code="provider_access_denied",
                    message=(
                        f"Catalog provider access_level '{access}' is not usable "
                        "for automated retrieval today."
                    ),
                )
            ]
    return []


def _check_region_residency(ctx: MissionPlannerContext) -> List[ConstraintFailure]:
    if not ctx.data_residency:
        return []
    # Without a real residency-aware provider registry, only flag when the
    # preferred compute location explicitly conflicts with the requirement.
    preferred = (ctx.preferred_compute_location or "").strip().lower()
    residency = ctx.data_residency.strip().lower()
    if preferred and preferred not in residency and residency not in preferred:
        # Soft conflict only when both are set and look incompatible
        # (e.g. preferred "us-east" vs residency "EU").
        region_tokens = {"eu", "europe", "us", "usa", "apac", "asia"}
        pref_tokens = {t for t in region_tokens if t in preferred}
        res_tokens = {t for t in region_tokens if t in residency}
        if pref_tokens and res_tokens and pref_tokens.isdisjoint(res_tokens):
            return [
                ConstraintFailure(
                    code="region_not_allowed",
                    message=(
                        f"Preferred compute location '{ctx.preferred_compute_location}' "
                        f"conflicts with data residency requirement '{ctx.data_residency}'."
                    ),
                )
            ]
    if ctx.allowed_regions:
        # When allowed_regions is non-empty, preferred location (if set) must
        # match one entry; otherwise residency string must appear.
        allowed_norm = [str(r).strip().lower() for r in ctx.allowed_regions]
        check_value = preferred or residency
        if check_value and not any(
            check_value in allowed or allowed in check_value for allowed in allowed_norm
        ):
            return [
                ConstraintFailure(
                    code="region_not_allowed",
                    message=(
                        f"Location '{check_value}' is outside allowed_regions "
                        f"{ctx.allowed_regions}."
                    ),
                )
            ]
    return []


def _check_cost_cap(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    if ctx.max_cost_usd is None:
        return []
    if (
        plan.cost_truth_status == TruthStatus.UNAVAILABLE.value
        or plan.estimated_total_cost_usd is None
    ):
        return [
            ConstraintFailure(
                code="cost_unavailable",
                message=(
                    "Mission sets a max cost, but no real pricing source is connected. "
                    "Cost cannot be verified — refusing to invent provider prices."
                ),
            )
        ]
    if float(plan.estimated_total_cost_usd) > float(ctx.max_cost_usd):
        return [
            ConstraintFailure(
                code="cost_exceeded",
                message=(
                    f"Estimated cost ${plan.estimated_total_cost_usd:.2f} exceeds "
                    f"the ${ctx.max_cost_usd:.2f} mission cap."
                ),
            )
        ]
    return []


def _check_deadline(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    if ctx.deadline is None:
        return []
    if plan.estimated_total_time_seconds is None:
        return [
            ConstraintFailure(
                code="deadline_infeasible",
                message="Plan duration could not be estimated against the mission deadline.",
            )
        ]
    finish = ctx.now_utc.timestamp() + float(plan.estimated_total_time_seconds)
    deadline_ts = ctx.deadline.astimezone(timezone.utc).timestamp()
    if finish > deadline_ts:
        return [
            ConstraintFailure(
                code="deadline_infeasible",
                message=(
                    f"Estimated completion in {plan.estimated_total_time_seconds / 60.0:.0f} min "
                    f"misses the deadline at {ctx.deadline.isoformat()}."
                ),
            )
        ]
    return []


def _check_contact_window(
    plan: DraftPlan,
    ctx: MissionPlannerContext,
) -> List[ConstraintFailure]:
    if plan.contact_window_id or ctx.contact_windows:
        if plan.contact_window_id or any(ctx.contact_windows):
            # Pattern generators attach the next window when available.
            if plan.contact_window_id:
                return []
            # Window list exists but this plan did not bind one.
            return [
                ConstraintFailure(
                    code="no_contact_window",
                    message="No eligible contact window was bound for this downlink path.",
                )
            ]
    return [
        ConstraintFailure(
            code="no_contact_window",
            message=(
                "No contact windows are available for mission satellites within "
                "the planning horizon."
            ),
        )
    ]


def _check_edge_location(ctx: MissionPlannerContext) -> List[ConstraintFailure]:
    preferred = (ctx.preferred_compute_location or "").strip().lower()
    edge_hints = ("edge", "onprem", "on-prem", "customer", "local")
    if preferred and any(h in preferred for h in edge_hints):
        return []
    # Edge plan is still generated as a candidate shell; without an explicit
    # customer edge preference it is conditional on customer environment access.
    return [
        ConstraintFailure(
            code="customer_edge_unspecified",
            message=(
                "No customer edge / preferred location is configured for "
                "local processing. Set preferred_compute_location to an edge "
                "environment to make this path executable."
            ),
        )
    ]


def _candidate(
    ctx: MissionPlannerContext, candidate_id: Optional[str]
) -> Optional[dict]:
    if not candidate_id:
        return None
    for item in ctx.catalog_snapshot:
        if item.get("id") == candidate_id:
            return item
    return None


def _parse_dt(value: object) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    return None
