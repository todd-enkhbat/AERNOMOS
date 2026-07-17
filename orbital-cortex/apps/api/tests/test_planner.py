"""Phase I: source-backed mission feasibility planner."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import Mission, MissionDataCandidate, MissionPlan
from app.db.truth import TruthStatus
from app.main import app, run_migrations
from app.planner import engine as planner_engine
from app.planner.preferences import PLANNER_CONFIG_VERSION

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}
# Footprint covering NY harbor AOI.
COVERING_WKT = (
    "POLYGON((-74.2 40.4, -73.6 40.4, -73.6 40.9, -74.2 40.9, -74.2 40.4))"
)
# Footprint in the Pacific — no AOI overlap.
MISS_WKT = (
    "POLYGON((-160.0 10.0, -150.0 10.0, -150.0 20.0, -160.0 20.0, -160.0 10.0))"
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _create_mission(
    client: TestClient,
    *,
    title: str = "Planner mission",
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    _ensure_session(client)
    payload: Dict[str, Any] = {
        "title": title,
        "objective_type": "analyze_imagery",
        "area_of_interest": AOI,
        "data_source_preference": ["sentinel-1-grd"],
        "start_time": "2024-01-01T00:00:00+00:00",
        "end_time": "2024-01-31T23:59:59+00:00",
    }
    if extra:
        payload.update(extra)
    created = client.post("/v1/missions", json=payload)
    assert created.status_code == 201, created.text
    return created.json()["mission"]["id"]


def _add_candidate(
    mission_id: str,
    *,
    footprint_wkt: str = COVERING_WKT,
    acquisition_time: Optional[datetime] = None,
    size_bytes: int = 50_000_000,
    external_item_id: str = "S1A_TEST_ITEM",
) -> str:
    db = SessionLocal(bind=get_engine())
    try:
        mid = uuid.UUID(mission_id)
        acquired = acquisition_time or (_utcnow() - timedelta(days=3))
        row = MissionDataCandidate(
            id=uuid.uuid4(),
            mission_id=mid,
            source_provider="microsoft-planetary-computer",
            collection="sentinel-1-grd",
            external_item_id=external_item_id,
            acquisition_time=acquired,
            footprint=WKTElement(footprint_wkt, srid=4326),
            asset_metadata={},
            estimated_size_bytes=size_bytes,
            source_url="https://example.test/stac/item",
            source_timestamp=_utcnow(),
            truth_status=TruthStatus.PROVIDER_REPORTED,
        )
        db.add(row)
        db.commit()
        return str(row.id)
    finally:
        db.close()


def _rejection_codes(plan: Dict[str, Any]) -> List[str]:
    expl = plan.get("explanation") or {}
    reasons = expl.get("rejection_reasons") or []
    codes = [r.get("code") for r in reasons if isinstance(r, dict)]
    # Also dig assumptions planner_meta
    for item in plan.get("assumptions") or []:
        if isinstance(item, dict) and item.get("kind") == "planner_meta":
            for r in item.get("rejection_reasons") or []:
                if isinstance(r, dict) and r.get("code"):
                    codes.append(r["code"])
    return codes


def _plans_by_pattern(plans: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for plan in plans:
        pattern = plan.get("pattern")
        if not pattern:
            for item in plan.get("assumptions") or []:
                if isinstance(item, dict) and item.get("kind") == "planner_meta":
                    pattern = item.get("pattern")
        if pattern:
            out[str(pattern)] = plan
    return out


def test_generate_plans_at_least_three_with_catalog(client: TestClient):
    mission_id = _create_mission(client)
    _add_candidate(mission_id)

    response = client.post(f"/v1/missions/{mission_id}/plans")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["planner_config_version"] == PLANNER_CONFIG_VERSION
    assert len(body["plans"]) >= 3
    assert body["recommended_plan_id"]
    recommended = next(p for p in body["plans"] if p["recommended"])
    assert recommended["status"] in {"feasible", "conditional"}
    assert recommended["explanation"]["why_recommended"]
    estimates = recommended.get("estimates") or {}
    assert estimates["duration"]["truth_status"] in {
        "ESTIMATED",
        "CALCULATED",
        "UNAVAILABLE",
    }
    assert estimates["cost_usd"]["truth_status"] == "UNAVAILABLE"
    assert estimates["cost_usd"]["value"] is None

    listed = client.get(f"/v1/missions/{mission_id}/plans")
    assert listed.status_code == 200
    assert len(listed.json()["plans"]) >= 3

    detail = client.get(
        f"/v1/missions/{mission_id}/plans/{recommended['id']}"
    )
    assert detail.status_code == 200
    plan = detail.json()["plan"]
    assert plan["steps"]
    assert plan["evidence"]
    assert all(s.get("truth_status") for s in plan["steps"])


def test_deadline_miss_rejects(client: TestClient):
    soon = (_utcnow() + timedelta(minutes=1)).isoformat()
    mission_id = _create_mission(
        client,
        title="Deadline miss",
        extra={"deadline": soon},
    )
    _add_candidate(mission_id)

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    by_pattern = _plans_by_pattern(body["plans"])
    cloud = by_pattern["existing_imagery_cloud"]
    assert cloud["status"] == "rejected"
    assert "deadline_infeasible" in _rejection_codes(cloud)


def test_cost_cap_with_unavailable_pricing(client: TestClient):
    mission_id = _create_mission(
        client,
        title="Cost cap",
        extra={"max_cost_usd": 10.0},
    )
    _add_candidate(mission_id)

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    assert body["plans"]
    for plan in body["plans"]:
        assert "cost_unavailable" in _rejection_codes(plan)
        assert plan["status"] == "rejected"
        estimates = plan.get("estimates") or {}
        assert estimates["cost_usd"]["truth_status"] == "UNAVAILABLE"
        assert plan["estimated_total_cost_usd"] is None
    assert body["recommended_plan_id"] is None


def test_geography_no_aoi_coverage_rejects(client: TestClient):
    mission_id = _create_mission(client, title="No coverage")
    _add_candidate(mission_id, footprint_wkt=MISS_WKT, external_item_id="MISS_ITEM")

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    by_pattern = _plans_by_pattern(body["plans"])
    cloud = by_pattern["existing_imagery_cloud"]
    edge = by_pattern["existing_imagery_edge"]
    assert cloud["status"] == "rejected"
    assert edge["status"] in {"rejected", "conditional"}
    assert "aoi_uncovered" in _rejection_codes(cloud)


def test_onboard_path_rejected(client: TestClient):
    mission_id = _create_mission(client, title="Onboard check")
    _add_candidate(mission_id)

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    by_pattern = _plans_by_pattern(body["plans"])
    onboard = by_pattern["onboard_processing"]
    assert onboard["status"] == "rejected"
    assert "onboard_provider_unavailable" in _rejection_codes(onboard)

    sat = by_pattern["satellite_ground_cloud"]
    assert sat["status"] in {"conditional", "rejected"}
    if sat["status"] == "conditional":
        assert "tasking_api_unavailable" in _rejection_codes(sat)


def test_stale_orbital_data_labeled(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    mission_id = _create_mission(client, title="Stale orbital")
    _add_candidate(mission_id)

    def _stale_meta(satellites):  # noqa: ANN001
        return {
            "snapshot_id": "pinned-test-stale",
            "source": "pinned-snapshot",
            "source_url": None,
            "epochs": ["2020-01-01T00:00:00+00:00"],
            "truth_status": TruthStatus.STALE.value,
            "retrieved_at": _utcnow().isoformat(),
            "stale_epoch_days": 7,
            "used_pinned_fallback": True,
        }

    monkeypatch.setattr(
        "app.planner.engine.tle_cache.metadata_from_db_satellites",
        _stale_meta,
    )

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    by_pattern = _plans_by_pattern(body["plans"])
    sat = by_pattern["satellite_ground_cloud"]
    assumptions = sat.get("assumptions") or []
    blob = str(assumptions).lower()
    assert "stale" in blob
    meta = next(
        (a for a in assumptions if isinstance(a, dict) and a.get("kind") == "planner_meta"),
        {},
    )
    assert meta.get("orbital_truth_status") == TruthStatus.STALE.value


def test_missing_catalog_no_fake_feasible_imagery(client: TestClient):
    mission_id = _create_mission(client, title="No catalog")

    body = client.post(f"/v1/missions/{mission_id}/plans").json()
    by_pattern = _plans_by_pattern(body["plans"])
    cloud = by_pattern["existing_imagery_cloud"]
    edge = by_pattern["existing_imagery_edge"]
    assert cloud["status"] == "rejected"
    assert "data_missing" in _rejection_codes(cloud)
    assert edge["status"] == "rejected"
    assert "data_missing" in _rejection_codes(edge)
    # Must not invent a feasible imagery plan.
    assert cloud.get("recommended") is False
    assert edge.get("recommended") is False


def test_determinism_same_snapshot_same_recommendation(client: TestClient):
    mission_id = _create_mission(client, title="Determinism")
    _add_candidate(mission_id)
    now = _utcnow()

    db = SessionLocal(bind=get_engine())
    try:
        mission = db.get(Mission, uuid.UUID(mission_id))
        assert mission is not None
        first = planner_engine.generate_plans_for_mission(db, mission, now_utc=now)
        db.commit()
        first_payload = [
            planner_engine.plan_to_dict(db, row) for row in first
        ]

        second = planner_engine.generate_plans_for_mission(db, mission, now_utc=now)
        db.commit()
        second_payload = [
            planner_engine.plan_to_dict(db, row) for row in second
        ]
    finally:
        db.close()

    first_by = _plans_by_pattern(first_payload)
    second_by = _plans_by_pattern(second_payload)
    assert set(first_by) == set(second_by)
    for pattern in first_by:
        assert first_by[pattern]["plan_hash"] == second_by[pattern]["plan_hash"]
        assert first_by[pattern]["status"] == second_by[pattern]["status"]
        assert first_by[pattern].get("score") == second_by[pattern].get("score")

    first_rec = next(p for p in first_payload if p["recommended"])
    second_rec = next(p for p in second_payload if p["recommended"])
    assert first_rec["pattern"] == second_rec["pattern"]
    assert first_rec["plan_hash"] == second_rec["plan_hash"]
    assert first_rec["input_hash"] == second_rec["input_hash"]

    # Only the newest batch should remain recommended.
    db = SessionLocal(bind=get_engine())
    try:
        recommended = db.scalars(
            select(MissionPlan).where(
                MissionPlan.mission_id == uuid.UUID(mission_id),
                MissionPlan.recommended.is_(True),
            )
        ).all()
        assert len(recommended) == 1
    finally:
        db.close()
