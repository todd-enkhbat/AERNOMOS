"""Phase P: mission feedback and design-partner capture."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("ANALYTICS_HASH_SALT", "test-analytics-hash-salt")
os.environ["ADMIN_TOKEN"] = "test-admin-token"

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import MissionDataCandidate
from app.db.truth import TruthStatus
from app.leads.orm import DesignPartnerRequestRow, MissionFeedbackRow
from app.leads.schemas import FEEDBACK_COMMENT_MAX_LEN, HONEYPOT_FIELD
from app.main import app, run_migrations

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}
COVERING_WKT = (
    "POLYGON((-74.2 40.4, -73.6 40.4, -73.6 40.9, -74.2 40.9, -74.2 40.4))"
)


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _create_mission(client: TestClient, title: str = "Feedback mission") -> str:
    _ensure_session(client)
    created = client.post(
        "/v1/missions",
        json={
            "title": title,
            "objective_type": "analyze_imagery",
            "area_of_interest": AOI,
            "data_source_preference": ["sentinel-1-grd"],
            "start_time": "2024-01-01T00:00:00+00:00",
            "end_time": "2024-01-31T23:59:59+00:00",
        },
    )
    assert created.status_code == 201, created.text
    return created.json()["mission"]["id"]


def _add_candidate(mission_id: str) -> None:
    db = SessionLocal(bind=get_engine())
    try:
        db.add(
            MissionDataCandidate(
                id=uuid.uuid4(),
                mission_id=uuid.UUID(mission_id),
                source_provider="microsoft-planetary-computer",
                collection="sentinel-1-grd",
                external_item_id=f"S1A_FEEDBACK_{uuid.uuid4().hex[:8]}",
                acquisition_time=_utcnow() - timedelta(days=3),
                footprint=WKTElement(COVERING_WKT, srid=4326),
                asset_metadata={},
                estimated_size_bytes=50_000_000,
                source_url="https://example.test/stac/item",
                source_timestamp=_utcnow(),
                truth_status=TruthStatus.PROVIDER_REPORTED,
            )
        )
        db.commit()
    finally:
        db.close()


def _partner_payload(**overrides: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "name": "Ada Lovelace",
        "work_email": "ada@example.com",
        "organization": "Analytical Engines Ltd",
        "role": "Mission architect",
        "mission_type": "maritime_awareness",
        "requested_integration": "satellite_tasking",
        "permission_to_contact": True,
    }
    payload.update(overrides)
    return payload


def test_non_blocking_plan_generation_without_feedback(client: TestClient):
    """Plan generation completes with zero feedback or design-partner interaction."""
    mission_id = _create_mission(client, title="Non-blocking plan")
    _add_candidate(mission_id)

    plans = client.post(f"/v1/missions/{mission_id}/plans")
    assert plans.status_code == 201, plans.text
    body = plans.json()
    assert body["plans"]
    assert body["recommended_plan_id"]

    detail = client.get(f"/v1/missions/{mission_id}")
    assert detail.status_code == 200
    assert detail.json()["mission"]["id"] == mission_id

    listed = client.get(f"/v1/missions/{mission_id}/plans")
    assert listed.status_code == 200
    assert len(listed.json()["plans"]) >= 1

    plan_id = body["recommended_plan_id"]
    plan_detail = client.get(f"/v1/missions/{mission_id}/plans/{plan_id}")
    assert plan_detail.status_code == 200
    assert plan_detail.json()["plan"]["steps"]

    db = SessionLocal(bind=get_engine())
    try:
        mid = uuid.UUID(mission_id)
        feedback_count = db.scalar(
            select(func.count())
            .select_from(MissionFeedbackRow)
            .where(MissionFeedbackRow.mission_id == mid)
        )
        lead_count = db.scalar(
            select(func.count())
            .select_from(DesignPartnerRequestRow)
            .where(DesignPartnerRequestRow.mission_id == mid)
        )
        assert int(feedback_count or 0) == 0
        assert int(lead_count or 0) == 0
    finally:
        db.close()


def test_design_partner_requires_permission_to_contact(client: TestClient):
    denied = client.post(
        "/v1/design-partner-requests",
        json=_partner_payload(permission_to_contact=False),
    )
    assert denied.status_code == 422
    assert denied.json()["error"]["code"] == "validation_error"

    ok = client.post("/v1/design-partner-requests", json=_partner_payload())
    assert ok.status_code == 201, ok.text
    request = ok.json()["request"]
    assert request["permission_to_contact"] is True
    assert request["organization"] == "Analytical Engines Ltd"


def test_feedback_comment_cap_rejects_not_truncates(client: TestClient):
    mission_id = _create_mission(client, title="Comment cap")
    overlong = "x" * (FEEDBACK_COMMENT_MAX_LEN + 1)
    response = client.post(
        f"/v1/missions/{mission_id}/feedback",
        json={"rating": "yes", "comment": overlong},
    )
    assert response.status_code == 422

    ok = client.post(
        f"/v1/missions/{mission_id}/feedback",
        json={"rating": "partly", "comment": "Useful enough for a design review."},
    )
    assert ok.status_code == 201, ok.text
    assert ok.json()["feedback"]["rating"] == "partly"
    assert "Useful enough" in (ok.json()["feedback"]["comment"] or "")


def test_honeypot_returns_success_but_does_not_persist(client: TestClient):
    db = SessionLocal(bind=get_engine())
    try:
        before = int(
            db.scalar(select(func.count()).select_from(DesignPartnerRequestRow)) or 0
        )
    finally:
        db.close()

    payload = _partner_payload(organization="Bot Corp")
    payload[HONEYPOT_FIELD] = "https://spam.example/trap"
    response = client.post("/v1/design-partner-requests", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["request"]["permission_to_contact"] is True

    db = SessionLocal(bind=get_engine())
    try:
        after = int(
            db.scalar(select(func.count()).select_from(DesignPartnerRequestRow)) or 0
        )
        bot_rows = db.scalars(
            select(DesignPartnerRequestRow).where(
                DesignPartnerRequestRow.organization == "Bot Corp"
            )
        ).all()
        assert after == before
        assert bot_rows == []
    finally:
        db.close()


def test_leads_rate_limit(monkeypatch):
    from app.core import ratelimit

    monkeypatch.setenv("RATE_LIMIT_LEADS", "2/hour")
    get_settings.cache_clear()
    ratelimit.limiter.reset()
    ratelimit.limiter.enabled = True
    try:
        with TestClient(app) as client:
            assert client.post("/v1/sessions").status_code in (200, 201)
            for i in range(2):
                response = client.post(
                    "/v1/design-partner-requests",
                    json=_partner_payload(organization=f"Rate Ltd {i}"),
                )
                assert response.status_code == 201, response.text
            limited = client.post(
                "/v1/design-partner-requests",
                json=_partner_payload(organization="Rate Ltd overflow"),
            )
            assert limited.status_code == 429
            assert limited.json()["error"]["code"] == "rate_limited"
    finally:
        ratelimit.limiter.enabled = False
        monkeypatch.undo()
        get_settings.cache_clear()


def test_leads_export_requires_admin_token(client: TestClient):
    denied = client.get("/v1/admin/leads/export")
    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "admin_unauthorized"

    allowed = client.get(
        "/v1/admin/leads/export",
        headers={"X-Nomos-Admin-Token": "test-admin-token"},
    )
    assert allowed.status_code == 200
    body = allowed.json()
    assert "feedback" in body
    assert "design_partner_requests" in body


def test_no_public_read_routes_for_leads(client: TestClient):
    for path in (
        "/v1/feedback",
        "/v1/mission-feedback",
        "/v1/design-partner-requests",
        "/v1/leads",
        "/v1/admin/leads",
    ):
        response = client.get(path)
        assert response.status_code in {404, 405}, path
