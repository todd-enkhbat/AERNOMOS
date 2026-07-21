"""Versioned mission brief JSON export."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog import service as catalog_service
from app.core import missions as mission_store
from app.db.mission_orm import Mission, MissionPlan
from app.db.truth import TruthStatus
from app.planner import engine as planner_engine
from app.services import mission_infrastructure as infra_service

JSON_SCHEMA_VERSION = 1

TRUTH_STATUS_LEGEND = [
    {
        "status": TruthStatus.OBSERVED.value,
        "meaning": "Directly measured or observed from a real instrument or system.",
    },
    {
        "status": TruthStatus.CALCULATED.value,
        "meaning": "Derived by Nomos from observed or provider-reported inputs.",
    },
    {
        "status": TruthStatus.PROVIDER_REPORTED.value,
        "meaning": "Reported by an upstream catalog or orbital data provider.",
    },
    {
        "status": TruthStatus.ESTIMATED.value,
        "meaning": "Heuristic estimate; not a guaranteed operational value.",
    },
    {
        "status": TruthStatus.SIMULATED.value,
        "meaning": "Authored or simulated for demonstration — not live capacity.",
    },
    {
        "status": TruthStatus.STALE.value,
        "meaning": "Previously real data that may be outdated.",
    },
    {
        "status": TruthStatus.UNAVAILABLE.value,
        "meaning": "No real source is connected for this value.",
    },
]

MISSING_INTEGRATIONS_DEFAULT = [
    "Satellite tasking / reservation API",
    "Ground-station booking / capacity API",
    "Commercial pricing feeds",
    "Onboard processing provider",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _geo_summary(aoi: Dict[str, Any]) -> Dict[str, Any]:
    """Static geographic summary without requiring a map image."""
    geom_type = aoi.get("type")
    coords = aoi.get("coordinates")
    bbox: Optional[List[float]] = None
    if geom_type == "Polygon" and coords:
        ring = coords[0] if coords else []
        lons = [float(p[0]) for p in ring if isinstance(p, (list, tuple)) and len(p) >= 2]
        lats = [float(p[1]) for p in ring if isinstance(p, (list, tuple)) and len(p) >= 2]
        if lons and lats:
            bbox = [min(lons), min(lats), max(lons), max(lats)]
    elif geom_type == "bbox" and isinstance(coords, (list, tuple)) and len(coords) == 4:
        bbox = [float(c) for c in coords]
    return {
        "geometry_type": geom_type,
        "bbox": bbox,
        "note": (
            "Map imagery is not embedded in this JSON export. "
            "Use the mission result page for interactive geography."
        ),
        "truth_status": TruthStatus.CALCULATED.value,
    }


def _rejection_reasons(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    explanation = plan.get("explanation") or {}
    if isinstance(explanation, dict) and explanation.get("rejection_reasons"):
        return list(explanation["rejection_reasons"])
    for item in plan.get("assumptions") or []:
        if isinstance(item, dict) and item.get("kind") == "planner_meta":
            return list(item.get("rejection_reasons") or [])
    return []


def _missing_integrations(plans: List[Dict[str, Any]]) -> List[str]:
    found: List[str] = []
    for plan in plans:
        explanation = plan.get("explanation") or {}
        if not isinstance(explanation, dict):
            continue
        for item in explanation.get("missing_integrations") or []:
            if item not in found:
                found.append(str(item))
    return found or list(MISSING_INTEGRATIONS_DEFAULT)


def _next_actions(missing: List[str]) -> List[str]:
    actions: List[str] = []
    if any("tasking" in m.lower() or "reservation" in m.lower() for m in missing):
        actions.extend(
            [
                "Connect a satellite tasking provider account",
                "Request ground-station access",
            ]
        )
    else:
        actions.append("Connect the selected data provider account")
    if any("onboard" in m.lower() for m in missing):
        actions.append("Upload payload and onboard compute capabilities")
    actions.extend(
        [
            "Confirm data residency and destination region",
            "Review the plan with the engineering team",
        ]
    )
    return actions


def build_mission_export_json(db: Session, mission: Mission) -> Dict[str, Any]:
    """Build a versioned mission brief document for download."""
    mission_input = mission_store.mission_to_dict(db, mission)
    candidates = [
        catalog_service.candidate_to_dict(db, row)
        for row in catalog_service.list_candidates(db, mission.id)
    ]
    plans_rows = list(
        db.scalars(
            select(MissionPlan)
            .where(MissionPlan.mission_id == mission.id)
            .order_by(MissionPlan.version.desc(), MissionPlan.created_at.desc())
        ).all()
    )
    plans = [
        planner_engine.plan_to_dict(
            db, row, include_steps=True, include_evidence=True
        )
        for row in plans_rows
    ]
    selected = next((p for p in plans if p.get("recommended")), None)
    if selected is None and plans:
        selected = plans[0]

    infra = infra_service.get_mission_infrastructure(db, mission)
    missing = _missing_integrations(plans)
    generated_at = _utc_now_iso()

    source_snapshots: Dict[str, Any] = {
        "catalog_candidates": candidates,
        "orbital_snapshot": (infra or {}).get("orbital_snapshot"),
        "ground_stations_referenced": (infra or {}).get("ground_stations") or [],
        "satellites_referenced": (infra or {}).get("satellites") or [],
    }

    return {
        "schema_version": JSON_SCHEMA_VERSION,
        "document_type": "nomos_mission_brief",
        "generated_at": generated_at,
        "mission_input": mission_input,
        "geographic_summary": _geo_summary(mission_input.get("area_of_interest") or {}),
        "source_snapshots": source_snapshots,
        "candidate_plans": plans,
        "selected_plan": selected,
        "assumptions": (selected or {}).get("assumptions") or [],
        "truth_statuses": {
            "legend": TRUTH_STATUS_LEGEND,
            "plan_feasibility": [
                {
                    "plan_id": p["id"],
                    "status": p.get("status"),
                    "feasibility_status": p.get("feasibility_status"),
                    "rejection_reasons": _rejection_reasons(p),
                }
                for p in plans
            ],
        },
        "rejection_reasons": _rejection_reasons(selected) if selected else [],
        "source_evidence": (selected or {}).get("evidence") or [],
        "missing_integrations": missing,
        "next_actions": _next_actions(missing),
        "disclosures": {
            "simulation_boundary": (
                "This mission plan uses real public orbital and catalog data where "
                "available. Satellite tasking, provider reservation, onboard execution, "
                "and commercial guarantees are not performed unless explicitly marked "
                "as connected."
            ),
            "unavailable_integrations": missing,
            "simulated_fields_policy": (
                "Any SIMULATED or UNAVAILABLE values are labeled in plan assumptions "
                "and source evidence. Do not treat them as live operational capacity."
            ),
        },
    }
