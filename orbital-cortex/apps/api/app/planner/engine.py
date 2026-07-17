"""Orchestrate generate → estimate → constrain → rank → persist.

Idempotency strategy (documented): each POST appends a new plan generation
batch with monotonically increasing MissionPlan.version values. Prior plans
are retained for audit; recommended flags on older plans are cleared so only
the newest batch's winner is recommended.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.missions import geometry_to_geojson
from app.db.mission_orm import (
    Mission,
    MissionDataCandidate,
    MissionPlan,
    MissionPlanStep,
    SourceEvidence,
)
from app.db.orm import Satellite
from app.db.truth import TruthStatus
from app.planner.constraints import apply_constraint_outcome, evaluate_hard_constraints
from app.planner.estimates import apply_estimates, estimates_for_hash
from app.planner.explain import explain_plan
from app.planner.hash import canonical_hash, plan_content_hash
from app.planner.patterns import generate_candidate_plans
from app.planner.preferences import (
    PLANNER_CONFIG_VERSION,
    score_plans,
    select_recommendation,
)
from app.planner.types import (
    DraftPlan,
    FeasibilityStatus,
    MissionPlannerContext,
    PlanStatus,
)
from app.services import contact_windows as cw_service
from app.services import mission_infrastructure as infra_service
from app.services import tle_cache

# AOI coverage uses PostGIS geography-safe area ratio when possible.


def generate_plans_for_mission(
    db: Session,
    mission: Mission,
    *,
    now_utc: Optional[datetime] = None,
) -> List[MissionPlan]:
    """Run the planner and persist MissionPlan / steps / evidence rows."""
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    ctx = build_context(db, mission, now_utc=now)
    drafts = generate_candidate_plans(ctx)

    evaluated: List[DraftPlan] = []
    for draft in drafts:
        apply_estimates(draft, ctx)
        failures = evaluate_hard_constraints(draft, ctx)
        apply_constraint_outcome(draft, failures)
        # Hash after estimates + constraints so content is stable.
        step_payload = [_step_hash_payload(s) for s in draft.steps]
        draft.plan_hash = plan_content_hash(
            pattern=draft.pattern.value,
            steps=step_payload,
            feasibility_status=draft.feasibility_status.value,
            rejection_codes=[r.code for r in draft.rejection_reasons],
            estimates=estimates_for_hash(draft),
            config_version=PLANNER_CONFIG_VERSION,
        )
        evaluated.append(draft)

    ranked = score_plans(evaluated, ctx)
    winner = select_recommendation(ranked)

    for draft in ranked:
        draft.explanation = explain_plan(
            draft,
            ctx,
            recommended=(winner is not None and draft is winner),
            all_plans=ranked,
        )

    # Clear previous recommended flags (new generation wins).
    existing = db.scalars(
        select(MissionPlan).where(MissionPlan.mission_id == mission.id)
    ).all()
    for row in existing:
        row.recommended = False

    start_version = _next_version(db, mission.id)
    persisted: List[MissionPlan] = []
    for offset, draft in enumerate(ranked):
        plan_row = _persist_plan(
            db,
            mission,
            draft,
            version=start_version + offset,
            recommended=(winner is not None and draft is winner),
            ctx=ctx,
        )
        persisted.append(plan_row)

    db.flush()
    return persisted


def build_context(
    db: Session,
    mission: Mission,
    *,
    now_utc: datetime,
) -> MissionPlannerContext:
    candidates = list(
        db.scalars(
            select(MissionDataCandidate)
            .where(MissionDataCandidate.mission_id == mission.id)
            .order_by(
                MissionDataCandidate.acquisition_time.desc(),
                MissionDataCandidate.id.asc(),
            )
        ).all()
    )
    catalog_snapshot = [_candidate_snapshot(db, row) for row in candidates]
    coverage = _coverage_ratios(db, mission, candidates)

    satellites = infra_service.select_satellites_for_mission(db, mission, candidates)
    windows: List[Dict[str, Any]] = []
    for sat in satellites:
        nxt = cw_service.next_window_for_satellite(
            db, sat.id, now_utc=now_utc.isoformat()
        )
        if nxt:
            windows.append(nxt)
    windows.sort(key=lambda w: (w.get("aos_utc") or "", w.get("id") or ""))

    if satellites:
        snap_meta = tle_cache.metadata_from_db_satellites(list(satellites))
    else:
        snap_meta = tle_cache.metadata_from_db_satellites(
            list(db.scalars(select(Satellite)).all())
        )

    max_age, onboard, residency = _prefs_from_customer_systems(
        mission.customer_systems or []
    )

    return MissionPlannerContext(
        mission_id=str(mission.id),
        objective_type=mission.objective_type,
        deadline=mission.deadline,
        max_cost_usd=mission.max_cost_usd,
        max_data_volume_mb=mission.max_data_volume_mb,
        preferred_compute_location=mission.preferred_compute_location,
        allowed_regions=list(mission.allowed_regions or []),
        data_source_preference=list(mission.data_source_preference or []),
        customer_systems=list(mission.customer_systems or []),
        max_age_days=max_age,
        onboard_preference=onboard,
        data_residency=residency,
        now_utc=now_utc,
        tle_snapshot_id=snap_meta.get("snapshot_id"),
        orbital_truth_status=str(
            snap_meta.get("truth_status") or TruthStatus.UNAVAILABLE.value
        ),
        catalog_snapshot=catalog_snapshot,
        contact_windows=windows,
        coverage_by_candidate=coverage,
        planner_config_version=PLANNER_CONFIG_VERSION,
    )


def plan_to_dict(
    db: Session,
    plan: MissionPlan,
    *,
    include_steps: bool = False,
    include_evidence: bool = False,
) -> Dict[str, Any]:
    assumptions = plan.assumptions if isinstance(plan.assumptions, list) else []
    meta = _assumptions_meta(assumptions)
    payload: Dict[str, Any] = {
        "id": str(plan.id),
        "mission_id": str(plan.mission_id),
        "version": plan.version,
        "recommended": bool(plan.recommended),
        "status": plan.status,
        "summary": plan.summary,
        "estimated_total_time_seconds": plan.estimated_total_time_seconds,
        "estimated_total_cost_usd": plan.estimated_total_cost_usd,
        "confidence": plan.confidence,
        "assumptions": assumptions,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "pattern": meta.get("pattern"),
        "plan_hash": meta.get("plan_hash"),
        "feasibility_status": meta.get("feasibility_status") or plan.status,
        "explanation": meta.get("explanation"),
        "estimates": meta.get("estimates"),
        "score": meta.get("score"),
        "planner_config_version": meta.get("planner_config_version"),
        "input_hash": meta.get("input_hash"),
    }
    if include_steps:
        steps = db.scalars(
            select(MissionPlanStep)
            .where(MissionPlanStep.mission_plan_id == plan.id)
            .order_by(MissionPlanStep.sequence.asc())
        ).all()
        payload["steps"] = [_step_to_dict(s) for s in steps]
    if include_evidence:
        evidence = db.scalars(
            select(SourceEvidence)
            .where(SourceEvidence.mission_plan_id == plan.id)
            .order_by(SourceEvidence.retrieved_at.asc(), SourceEvidence.id.asc())
        ).all()
        payload["evidence"] = [_evidence_to_dict(e) for e in evidence]
    return payload


def _persist_plan(
    db: Session,
    mission: Mission,
    draft: DraftPlan,
    *,
    version: int,
    recommended: bool,
    ctx: MissionPlannerContext,
) -> MissionPlan:
    status = _plan_status(draft).value
    input_hash = canonical_hash(ctx.input_bundle())
    assumptions: List[Any] = list(draft.assumptions)
    assumptions.append(
        {
            "kind": "planner_meta",
            "pattern": draft.pattern.value,
            "plan_hash": draft.plan_hash,
            "input_hash": input_hash,
            "feasibility_status": draft.feasibility_status.value,
            "rejection_reasons": [
                {"code": r.code, "message": r.message} for r in draft.rejection_reasons
            ],
            "explanation": draft.explanation,
            "score": draft.score,
            "score_breakdown": draft.score_breakdown,
            "planner_config_version": PLANNER_CONFIG_VERSION,
            "estimates": {
                "duration": {
                    "value": draft.estimated_total_time_seconds,
                    "truth_status": draft.duration_truth_status,
                    "method": draft.duration_method,
                },
                "data_movement_mb": {
                    "value": draft.estimated_data_movement_mb,
                    "truth_status": draft.data_movement_truth_status,
                    "method": draft.data_movement_method,
                },
                "cost_usd": {
                    "value": draft.estimated_total_cost_usd,
                    "truth_status": draft.cost_truth_status,
                    "method": draft.cost_method,
                },
            },
            "tle_snapshot_id": draft.tle_snapshot_id or ctx.tle_snapshot_id,
            "orbital_truth_status": draft.orbital_truth_status or ctx.orbital_truth_status,
            "candidate_id": draft.candidate_id,
            "contact_window_id": draft.contact_window_id,
        }
    )

    plan = MissionPlan(
        id=uuid.uuid4(),
        mission_id=mission.id,
        version=version,
        recommended=recommended,
        status=status,
        summary=draft.summary,
        estimated_total_time_seconds=draft.estimated_total_time_seconds,
        estimated_total_cost_usd=draft.estimated_total_cost_usd,
        confidence=draft.confidence,
        assumptions=assumptions,
    )
    db.add(plan)
    db.flush()

    step_rows: List[MissionPlanStep] = []
    for step in draft.steps:
        # Propagate plan-level rejection onto steps that were still marked feasible
        # when the whole plan is rejected.
        step_feas = step.feasibility_status
        step_reason = step.rejection_reason
        if (
            draft.feasibility_status == FeasibilityStatus.REJECTED
            and step_feas == FeasibilityStatus.FEASIBLE.value
            and draft.rejection_reasons
        ):
            step_feas = FeasibilityStatus.REJECTED.value
            step_reason = step_reason or draft.rejection_reasons[0].message

        row = MissionPlanStep(
            id=uuid.uuid4(),
            mission_plan_id=plan.id,
            sequence=step.sequence,
            step_type=step.step_type,
            provider_name=step.provider_name,
            resource_id=uuid.UUID(step.resource_id) if step.resource_id else None,
            title=step.title,
            description=step.description,
            start_time=step.start_time,
            end_time=step.end_time,
            duration_seconds=step.duration_seconds,
            estimated_cost_usd=step.estimated_cost_usd,
            input_artifact=step.input_artifact,
            output_artifact=step.output_artifact,
            truth_status=TruthStatus(step.truth_status),
            source_metadata=step.source_metadata or {},
            feasibility_status=step_feas,
            rejection_reason=step_reason,
        )
        db.add(row)
        step_rows.append(row)
    db.flush()

    _write_evidence(db, mission, plan, draft, ctx, step_rows)
    return plan


def _write_evidence(
    db: Session,
    mission: Mission,
    plan: MissionPlan,
    draft: DraftPlan,
    ctx: MissionPlannerContext,
    step_rows: Sequence[MissionPlanStep],
) -> None:
    now = ctx.now_utc
    # Catalog evidence
    if draft.candidate_id:
        candidate = next(
            (c for c in ctx.catalog_snapshot if c.get("id") == draft.candidate_id),
            None,
        )
        if candidate:
            evidence = SourceEvidence(
                id=uuid.uuid4(),
                mission_id=mission.id,
                mission_plan_id=plan.id,
                mission_plan_step_id=step_rows[0].id if step_rows else None,
                source_name=f"catalog:{candidate.get('source_provider')}",
                source_type="catalog_snapshot",
                source_url=candidate.get("source_url"),
                retrieved_at=_parse_dt(candidate.get("source_timestamp")) or now,
                effective_at=_parse_dt(candidate.get("acquisition_time")),
                raw_value={
                    "candidate_id": candidate.get("id"),
                    "external_item_id": candidate.get("external_item_id"),
                    "collection": candidate.get("collection"),
                },
                transformed_value={
                    "coverage_fraction": ctx.coverage_by_candidate.get(
                        str(candidate.get("id")), 0.0
                    ),
                    "estimated_size_bytes": candidate.get("estimated_size_bytes"),
                },
                transformation_method="planner.catalog_snapshot",
                truth_status=TruthStatus(
                    candidate.get("truth_status") or TruthStatus.PROVIDER_REPORTED.value
                ),
            )
            db.add(evidence)

    # Orbital / TLE evidence for downlink patterns
    if draft.tle_snapshot_id or ctx.tle_snapshot_id:
        snap = {
            "snapshot_id": draft.tle_snapshot_id or ctx.tle_snapshot_id,
            "truth_status": draft.orbital_truth_status or ctx.orbital_truth_status,
            "retrieved_at": now.isoformat(),
            "source": "planner",
            "source_url": None,
            "epochs": [],
            "used_pinned_fallback": (
                (draft.orbital_truth_status or ctx.orbital_truth_status)
                == TruthStatus.STALE.value
            ),
        }
        infra_service.record_orbital_snapshot_evidence(
            db,
            mission_id=mission.id,
            snapshot_meta=snap,
            mission_plan_id=plan.id,
        )

    # Method evidence for duration estimate
    method_evidence = SourceEvidence(
        id=uuid.uuid4(),
        mission_id=mission.id,
        mission_plan_id=plan.id,
        mission_plan_step_id=None,
        source_name="planner.estimates",
        source_type="estimate_method",
        source_url=None,
        retrieved_at=now,
        effective_at=now,
        raw_value=estimates_for_hash(draft),
        transformed_value={
            "planner_config_version": PLANNER_CONFIG_VERSION,
            "plan_hash": draft.plan_hash,
        },
        transformation_method=draft.duration_method,
        truth_status=TruthStatus(draft.duration_truth_status),
    )
    db.add(method_evidence)


def _plan_status(draft: DraftPlan) -> PlanStatus:
    if draft.feasibility_status == FeasibilityStatus.FEASIBLE:
        return PlanStatus.FEASIBLE
    if draft.feasibility_status == FeasibilityStatus.CONDITIONAL:
        return PlanStatus.CONDITIONAL
    return PlanStatus.REJECTED


def _next_version(db: Session, mission_id: uuid.UUID) -> int:
    current = db.scalar(
        select(func.max(MissionPlan.version)).where(MissionPlan.mission_id == mission_id)
    )
    return int(current or 0) + 1


def _candidate_snapshot(db: Session, row: MissionDataCandidate) -> Dict[str, Any]:
    return {
        "id": str(row.id),
        "source_provider": row.source_provider,
        "collection": row.collection,
        "external_item_id": row.external_item_id,
        "acquisition_time": row.acquisition_time.isoformat() if row.acquisition_time else None,
        "estimated_size_bytes": row.estimated_size_bytes,
        "source_url": row.source_url,
        "source_timestamp": row.source_timestamp.isoformat() if row.source_timestamp else None,
        "truth_status": (
            row.truth_status.value
            if isinstance(row.truth_status, TruthStatus)
            else str(row.truth_status)
        ),
        "footprint": geometry_to_geojson(db, row.footprint),
        "access_level": "public_information",
    }


def _coverage_ratios(
    db: Session,
    mission: Mission,
    candidates: Sequence[MissionDataCandidate],
) -> Dict[str, float]:
    ratios: Dict[str, float] = {}
    if not candidates:
        return ratios
    # ST_Area of intersection / ST_Area of AOI (degree² ratio; good enough for threshold).
    for row in candidates:
        ratio = db.scalar(
            select(
                func.ST_Area(func.ST_Intersection(row.footprint, mission.area_of_interest))
                / func.nullif(func.ST_Area(mission.area_of_interest), 0)
            )
        )
        ratios[str(row.id)] = float(ratio or 0.0)
    return ratios


def _prefs_from_customer_systems(
    systems: Sequence[Any],
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    max_age: Optional[int] = None
    onboard: Optional[str] = None
    residency: Optional[str] = None
    for item in systems:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        if kind == "data_freshness" and item.get("max_age_days") is not None:
            try:
                max_age = int(item["max_age_days"])
            except (TypeError, ValueError):
                pass
        elif kind == "onboard_processing" and item.get("preference"):
            onboard = str(item["preference"])
        elif kind == "data_residency" and item.get("requirement"):
            residency = str(item["requirement"])
    return max_age, onboard, residency


def _step_hash_payload(step: Any) -> Dict[str, Any]:
    return {
        "sequence": step.sequence,
        "step_type": step.step_type,
        "provider_name": step.provider_name,
        "title": step.title,
        "truth_status": step.truth_status,
        "feasibility_status": step.feasibility_status,
        "rejection_reason": step.rejection_reason,
        "duration_seconds": step.duration_seconds,
    }


def _assumptions_meta(assumptions: List[Any]) -> Dict[str, Any]:
    for item in assumptions:
        if isinstance(item, dict) and item.get("kind") == "planner_meta":
            return item
    return {}


def _step_to_dict(step: MissionPlanStep) -> Dict[str, Any]:
    return {
        "id": str(step.id),
        "mission_plan_id": str(step.mission_plan_id),
        "sequence": step.sequence,
        "step_type": step.step_type,
        "provider_name": step.provider_name,
        "resource_id": str(step.resource_id) if step.resource_id else None,
        "title": step.title,
        "description": step.description,
        "start_time": step.start_time.isoformat() if step.start_time else None,
        "end_time": step.end_time.isoformat() if step.end_time else None,
        "duration_seconds": step.duration_seconds,
        "estimated_cost_usd": step.estimated_cost_usd,
        "input_artifact": step.input_artifact,
        "output_artifact": step.output_artifact,
        "truth_status": (
            step.truth_status.value
            if isinstance(step.truth_status, TruthStatus)
            else str(step.truth_status)
        ),
        "source_metadata": step.source_metadata,
        "feasibility_status": step.feasibility_status,
        "rejection_reason": step.rejection_reason,
    }


def _evidence_to_dict(row: SourceEvidence) -> Dict[str, Any]:
    return {
        "id": str(row.id),
        "mission_id": str(row.mission_id),
        "mission_plan_id": str(row.mission_plan_id) if row.mission_plan_id else None,
        "mission_plan_step_id": (
            str(row.mission_plan_step_id) if row.mission_plan_step_id else None
        ),
        "source_name": row.source_name,
        "source_type": row.source_type,
        "source_url": row.source_url,
        "retrieved_at": row.retrieved_at.isoformat() if row.retrieved_at else None,
        "effective_at": row.effective_at.isoformat() if row.effective_at else None,
        "raw_value": row.raw_value,
        "transformed_value": row.transformed_value,
        "transformation_method": row.transformation_method,
        "truth_status": (
            row.truth_status.value
            if isinstance(row.truth_status, TruthStatus)
            else str(row.truth_status)
        ),
    }


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
