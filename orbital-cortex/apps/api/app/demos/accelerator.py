"""Accelerator-ready curated demos (Phase R).

Three demos that reset from a single command and run offline against pinned
real STAC fixtures by default:

    python -m app.seed --demo=1 --reset
    python -m app.seed --demo=2 --reset
    python -m app.seed --demo=3 --reset

Pass ``--live`` to re-fetch from Planetary Computer instead of fixtures.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from geoalchemy2.elements import WKTElement
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.catalog import service as catalog_service
from app.catalog.fixture_provider import items_from_fixture_name
from app.catalog.planetary_computer import PlanetaryComputerCatalog
from app.core.config import get_settings
from app.core.tokens import hash_token
from app.db.mission_orm import (
    AnonymousSession,
    Mission,
    MissionDataCandidate,
    MissionPlan,
)
from app.db.truth import TruthStatus
from app.planner.engine import generate_plans_for_mission, plan_to_dict

# Stable namespace so demo missions/sessions survive reseeds with the same IDs.
_DEMO_NAMESPACE = uuid.UUID("00000000-0000-4000-8000-0000000000d1")

# Deterministic raw session tokens (only the hash is stored). Tests and the
# seed CLI use these so Demo 3 can execute as the mission owner without manual
# cookie surgery.
DEMO_SESSION_TOKENS: Dict[int, str] = {
    1: "nomos-accelerator-demo-1-session-token-v1",
    2: "nomos-accelerator-demo-2-session-token-v1",
    3: "nomos-accelerator-demo-3-session-token-v1",
}


def demo_mission_id(demo_number: int) -> uuid.UUID:
    return uuid.uuid5(_DEMO_NAMESPACE, f"accelerator-demo-{demo_number}")


def demo_session_id(demo_number: int) -> uuid.UUID:
    return uuid.uuid5(_DEMO_NAMESPACE, f"accelerator-demo-session-{demo_number}")


def demo_candidate_id(demo_number: int, index: int = 0) -> uuid.UUID:
    return uuid.uuid5(
        _DEMO_NAMESPACE, f"accelerator-demo-{demo_number}-candidate-{index}"
    )


ACCELERATOR_DEMOS: Dict[int, Dict[str, Any]] = {
    1: {
        "number": 1,
        "slug": "accelerator-demo-1",
        "title": "Demo 1 — Existing Sentinel imagery (NY Harbor)",
        "objective_type": "analyze_imagery",
        "wkt": "POLYGON((-74.3 40.3,-73.5 40.3,-73.5 41.0,-74.3 41.0,-74.3 40.3))",
        "collection": "sentinel-1-grd",
        "fixture": "demo1_maritime_ny_harbor_s1.json",
        "preferred_compute_location": "cloud",
        "allowed_regions": [],
        "data_residency": "US",
        "start_time": "2024-06-01T00:00:00+00:00",
        "end_time": "2024-06-30T23:59:59+00:00",
        "deadline_days": 14,
        "notes": (
            "Accelerator Demo 1: plan existing Sentinel-1 imagery over New York "
            "Harbor with a U.S. data-residency constraint. Catalog candidates "
            "come from a pinned real Planetary Computer STAC fixture by default."
        ),
        "disclosure": {
            "kind": "accelerator_demo_disclosure",
            "demo_number": 1,
            "catalog_mode_default": "fixture",
            "summary": (
                "Pinned real Sentinel-1 STAC items (PROVIDER_REPORTED) over NY "
                "Harbor. Onboard processing is rejected as unavailable. Cloud "
                "steps use the SIMULATED demo cloud provider."
            ),
            "real_data": [
                "Pinned Planetary Computer Sentinel-1 GRD metadata (real item IDs, "
                "acquisition times, footprints)",
                "Public CelesTrak TLE snapshots (live or pinned)",
            ],
            "real_calculations": [
                "SGP4 contact windows",
                "AOI coverage and planner feasibility",
            ],
            "simulated_steps": [
                "Nomos simulated cloud provider on cloud_process steps",
                "Ground-station operational parameters (latency/availability)",
            ],
            "unavailable_integrations": [
                "Satellite tasking",
                "Onboard execution",
                "Commercial pricing",
            ],
        },
    },
    2: {
        "number": 2,
        "slug": "accelerator-demo-2",
        "title": "Demo 2 — Disaster response (Gulf Coast)",
        "objective_type": "remote_sensing_workflow",
        "wkt": "POLYGON((-90.5 29.5,-89.5 29.5,-89.5 30.5,-90.5 30.5,-90.5 29.5))",
        "collection": "sentinel-1-grd",
        "fixture": "demo2_disaster_gulf_s1.json",
        "preferred_compute_location": "cloud",
        "allowed_regions": [],
        "data_residency": "US",
        "start_time": "2024-09-01T00:00:00+00:00",
        "end_time": "2024-09-20T23:59:59+00:00",
        "deadline_days": 2,
        "notes": (
            "Accelerator Demo 2: urgent disaster framing comparing existing "
            "imagery, new tasking/acquisition (conditional), and cloud "
            "processing. Every number carries a truth status."
        ),
        "disclosure": {
            "kind": "accelerator_demo_disclosure",
            "demo_number": 2,
            "catalog_mode_default": "fixture",
            "summary": (
                "Feasibility comparison under an urgent deadline. Tasking stays "
                "conditional; onboard stays rejected; existing-imagery→cloud can "
                "be feasible from pinned real STAC scenes."
            ),
            "real_data": [
                "Pinned Planetary Computer Sentinel-1 GRD metadata over the Gulf AOI",
            ],
            "real_calculations": [
                "Planner feasibility, rejection reasons, and ranking",
                "SGP4 contact windows when a downlink pattern applies",
            ],
            "simulated_steps": [
                "SIMULATED cloud provider on cloud_process steps",
            ],
            "unavailable_integrations": [
                "Satellite tasking API",
                "Ground-station reservation",
                "Onboard execution",
                "Commercial pricing",
            ],
        },
    },
    3: {
        "number": 3,
        "slug": "accelerator-demo-3",
        "title": "Demo 3 — Customer edge processing + real CPU execution",
        "objective_type": "compare_processing",
        "wkt": "POLYGON((-122.55 37.70,-122.35 37.70,-122.35 37.85,-122.55 37.85,-122.55 37.70))",
        "collection": "sentinel-2-l2a",
        "fixture": "demo3_edge_bayarea_s2.json",
        "preferred_compute_location": "customer_edge",
        "allowed_regions": [],
        "data_residency": "US",
        "start_time": "2024-07-01T00:00:00+00:00",
        "end_time": "2024-07-31T23:59:59+00:00",
        "deadline_days": 10,
        "notes": (
            "Accelerator Demo 3: compare cloud vs customer-edge processing on a "
            "real pinned Sentinel-2 scene, then run one real Phase M CPU "
            "execution (crop → thumbnail) with OBSERVED metrics."
        ),
        "disclosure": {
            "kind": "accelerator_demo_disclosure",
            "demo_number": 3,
            "catalog_mode_default": "fixture",
            "summary": (
                "Cloud vs edge comparison from pinned real Sentinel-2 metadata. "
                "CPU demo executes on Nomos's worker against fixture:sample.tif "
                "(not a STAC download) and records OBSERVED duration."
            ),
            "real_data": [
                "Pinned Planetary Computer Sentinel-2 L2A metadata",
            ],
            "real_calculations": [
                "Planner cloud vs edge comparison",
            ],
            "simulated_steps": [
                "SIMULATED cloud provider; edge providers remain public_data_only / "
                "sandbox_requested until connected",
            ],
            "unavailable_integrations": [
                "Customer edge reservation",
                "Onboard execution",
                "Commercial pricing",
            ],
            "observed_execution": [
                "Phase M crop_geotiff + thumbnail on fixture:sample.tif "
                "(OBSERVED duration and byte counts)",
            ],
        },
    },
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_demo_session(session: Session, demo_number: int) -> AnonymousSession:
    settings = get_settings()
    now = _utc_now()
    sid = demo_session_id(demo_number)
    raw = DEMO_SESSION_TOKENS[demo_number]
    row = session.get(AnonymousSession, sid)
    if row is None:
        row = AnonymousSession(
            id=sid,
            session_token_hash=hash_token(raw),
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(days=settings.session_ttl_days),
        )
        session.add(row)
    else:
        row.session_token_hash = hash_token(raw)
        row.last_seen_at = now
        row.expires_at = now + timedelta(days=settings.session_ttl_days)
    session.flush()
    return row


def _delete_demo_mission(session: Session, demo_number: int) -> None:
    mid = demo_mission_id(demo_number)
    existing = session.get(Mission, mid)
    if existing is not None:
        session.delete(existing)
        session.flush()


def _create_demo_mission(
    session: Session,
    *,
    demo_number: int,
    owner: AnonymousSession,
    now: datetime,
) -> Mission:
    spec = ACCELERATOR_DEMOS[demo_number]
    deadline = now + timedelta(days=int(spec["deadline_days"]))
    systems: List[Any] = [
        dict(spec["disclosure"]),
        {
            "kind": "data_residency",
            "value": spec.get("data_residency"),
        },
    ]
    mission = Mission(
        id=demo_mission_id(demo_number),
        anonymous_session_id=owner.id,
        organization_id=None,
        title=str(spec["title"]),
        objective_type=str(spec["objective_type"]),
        status="active",
        area_of_interest=WKTElement(str(spec["wkt"]), srid=4326),
        start_time=_parse_dt(str(spec["start_time"])),
        end_time=_parse_dt(str(spec["end_time"])),
        deadline=deadline,
        preferred_compute_location=spec.get("preferred_compute_location"),
        allowed_regions=list(spec.get("allowed_regions") or []),
        data_source_preference=[{"collection": spec["collection"]}],
        customer_systems=systems,
        notes=str(spec["notes"]),
        is_example=False,
        created_at=now,
        updated_at=now,
    )
    session.add(mission)
    session.flush()
    return mission


def _seed_candidates_from_fixture(
    session: Session,
    mission: Mission,
    fixture_name: str,
    *,
    demo_number: int,
) -> List[MissionDataCandidate]:
    items = items_from_fixture_name(fixture_name)
    session.execute(
        delete(MissionDataCandidate).where(
            MissionDataCandidate.mission_id == mission.id
        )
    )
    session.flush()
    now = _utc_now()
    rows: List[MissionDataCandidate] = []
    from app.core.missions import geojson_to_wkt

    for index, item in enumerate(items):
        meta = item.asset_metadata_payload()
        meta["nomos_fixture"] = dict(item.properties.get("nomos_fixture") or {})
        meta["nomos_fixture"]["demo_mode"] = "pinned_fixture"
        row = MissionDataCandidate(
            id=demo_candidate_id(demo_number, index),
            mission_id=mission.id,
            source_provider=item.source_provider,
            collection=item.collection,
            external_item_id=item.external_item_id,
            acquisition_time=item.acquisition_time,
            footprint=WKTElement(geojson_to_wkt(item.footprint), srid=4326),
            asset_metadata=meta,
            estimated_size_bytes=item.estimated_size_bytes,
            source_url=item.source_url,
            source_timestamp=now,
            truth_status=TruthStatus.PROVIDER_REPORTED,
            created_at=now,
        )
        session.add(row)
        rows.append(row)
    session.flush()
    return rows


def _seed_candidates_live(
    session: Session, mission: Mission, collection: str
) -> List[MissionDataCandidate]:
    session.execute(
        delete(MissionDataCandidate).where(
            MissionDataCandidate.mission_id == mission.id
        )
    )
    session.flush()
    return catalog_service.discover_for_mission(
        session,
        mission,
        provider=PlanetaryComputerCatalog(use_cache=False),
        collections=[collection],
        limit=5,
    )


def reset_accelerator_demo(
    session: Session,
    demo_number: int,
    *,
    live: bool = False,
) -> Dict[str, Any]:
    """Delete and recreate one accelerator demo. Returns a run summary."""
    if demo_number not in ACCELERATOR_DEMOS:
        raise ValueError(f"Unknown demo number: {demo_number}. Expected 1, 2, or 3.")

    spec = ACCELERATOR_DEMOS[demo_number]
    now = _utc_now()
    _delete_demo_mission(session, demo_number)
    owner = _ensure_demo_session(session, demo_number)
    mission = _create_demo_mission(
        session, demo_number=demo_number, owner=owner, now=now
    )

    catalog_mode = "live" if live else "fixture"
    if live:
        candidates = _seed_candidates_live(
            session, mission, str(spec["collection"])
        )
    else:
        candidates = _seed_candidates_from_fixture(
            session,
            mission,
            str(spec["fixture"]),
            demo_number=demo_number,
        )

    if not candidates:
        raise RuntimeError(
            f"Demo {demo_number} produced zero catalog candidates "
            f"(mode={catalog_mode}). Check the fixture or live STAC query."
        )

    session.execute(
        delete(MissionPlan).where(MissionPlan.mission_id == mission.id)
    )
    session.flush()
    plans = generate_plans_for_mission(session, mission, now_utc=now)
    session.flush()

    plan_summaries = [
        plan_to_dict(session, plan, include_steps=True, include_evidence=False)
        for plan in plans
    ]
    recommended = next((p for p in plan_summaries if p.get("recommended")), None)

    simulated_steps: List[Dict[str, Any]] = []
    for plan in plan_summaries:
        for step in plan.get("steps") or []:
            meta = step.get("source_metadata") or {}
            integration = meta.get("integration_status")
            truth = step.get("truth_status")
            if integration == "simulated" or truth == "SIMULATED":
                simulated_steps.append(
                    {
                        "plan_id": plan["id"],
                        "step_id": step["id"],
                        "title": step.get("title"),
                        "truth_status": truth,
                        "integration_status": integration,
                        "feasibility_status": step.get("feasibility_status"),
                    }
                )

    executable_step = None
    for plan in plan_summaries:
        for step in plan.get("steps") or []:
            if (
                step.get("step_type") in {"cloud_process", "edge_process"}
                and step.get("feasibility_status") == "feasible"
            ):
                executable_step = {
                    "plan_id": plan["id"],
                    "step_id": step["id"],
                    "step_type": step["step_type"],
                    "title": step.get("title"),
                }
                break
        if executable_step is not None:
            break

    return {
        "demo_number": demo_number,
        "slug": spec["slug"],
        "mission_id": str(mission.id),
        "session_id": str(owner.id),
        "session_token": DEMO_SESSION_TOKENS[demo_number],
        "catalog_mode": catalog_mode,
        "candidate_count": len(candidates),
        "candidates": [
            {
                "id": str(row.id),
                "external_item_id": row.external_item_id,
                "collection": row.collection,
                "acquisition_time": row.acquisition_time.isoformat(),
                "truth_status": (
                    row.truth_status.value
                    if hasattr(row.truth_status, "value")
                    else str(row.truth_status)
                ),
                "source_url": row.source_url,
            }
            for row in candidates
        ],
        "plan_count": len(plan_summaries),
        "recommended_plan_id": recommended["id"] if recommended else None,
        "recommended_feasibility": (
            recommended.get("feasibility_status") if recommended else None
        ),
        "plans": [
            {
                "id": p["id"],
                "pattern": p.get("pattern"),
                "feasibility_status": p.get("feasibility_status"),
                "recommended": p.get("recommended"),
                "summary": p.get("summary"),
            }
            for p in plan_summaries
        ],
        "simulated_steps_visible": simulated_steps,
        "executable_step": executable_step,
        "disclosure": spec["disclosure"],
    }


def run_demo_cpu_execution(
    session: Session,
    demo_number: int = 3,
) -> Dict[str, Any]:
    """Trigger the Phase M CPU demo for Demo 3 and return OBSERVED metrics.

    Runs crop_geotiff on fixture:sample.tif synchronously (same path used when
    Redis is unreachable). Must be called after ``reset_accelerator_demo(3)``.
    """
    from app.execution.fixtures import DEMO_CROP_BOUNDS, ensure_execution_fixtures
    from app.execution.provider import (
        ExecutionContext,
        LocalCpuExecutionProvider,
        derive_idempotency_key,
    )
    from app.execution.types import ExecutionTask

    ensure_execution_fixtures()
    summary = None
    # Prefer using already-seeded state; if missing, reset first.
    mission = session.get(Mission, demo_mission_id(demo_number))
    if mission is None:
        summary = reset_accelerator_demo(session, demo_number, live=False)
        mission = session.get(Mission, demo_mission_id(demo_number))
        assert mission is not None

    plans = list(
        session.scalars(
            select(MissionPlan)
            .where(MissionPlan.mission_id == mission.id)
            .order_by(MissionPlan.version.asc())
        ).all()
    )
    recommended = next((p for p in plans if p.recommended), plans[0] if plans else None)
    if recommended is None:
        raise RuntimeError("Demo has no plans; reset the demo first.")

    detail = plan_to_dict(
        session, recommended, include_steps=True, include_evidence=False
    )
    step = None
    chosen_plan = recommended
    for plan in [recommended, *plans]:
        if plan is None:
            continue
        detail = plan_to_dict(
            session, plan, include_steps=True, include_evidence=False
        )
        for candidate in detail.get("steps") or []:
            if (
                candidate.get("step_type") in {"cloud_process", "edge_process"}
                and candidate.get("feasibility_status") == "feasible"
            ):
                step = candidate
                chosen_plan = plan
                break
        if step is not None:
            break
    if step is None or chosen_plan is None:
        raise RuntimeError(
            "No feasible cloud_process/edge_process step for CPU execution."
        )

    from uuid import UUID

    step_id = UUID(step["id"])
    task = ExecutionTask(
        task_type="crop_geotiff",
        input_ref="fixture:sample.tif",
        params={"bounds": list(DEMO_CROP_BOUNDS), "max_size": 256},
    )
    provider = LocalCpuExecutionProvider(
        session,
        ExecutionContext(
            mission_id=mission.id,
            mission_plan_id=chosen_plan.id,
            mission_plan_step_id=step_id,
        ),
    )
    idempotency_key = derive_idempotency_key(
        plan_id=chosen_plan.id, step_id=step_id, task=task
    )
    # Use a unique key each reset so back-to-back runs actually re-execute.
    idempotency_key = f"{idempotency_key}:{_utc_now().isoformat()}"
    estimate = provider.estimate(task)
    job = provider.submit(task, idempotency_key)
    session.flush()

    status = provider.status(job.external_job_id)
    result_payload: Optional[Dict[str, Any]] = None
    observed: Optional[Dict[str, Any]] = None
    if status.status == "succeeded":
        result = provider.result(job.external_job_id)
        result_payload = result.model_dump()
        observed_obj = result_payload.get("observed")
        if isinstance(observed_obj, dict):
            observed = observed_obj
        else:
            observed = result_payload.get("observed_metrics")

    return {
        "demo_number": demo_number,
        "mission_id": str(mission.id),
        "plan_id": str(chosen_plan.id),
        "step_id": step["id"],
        "job": job.model_dump(),
        "estimate": estimate.model_dump(),
        "status": status.model_dump(),
        "result": result_payload,
        "observed_metrics": observed,
        "observed_truth_status": "OBSERVED" if status.status == "succeeded" else None,
        "seed_summary": summary,
    }
