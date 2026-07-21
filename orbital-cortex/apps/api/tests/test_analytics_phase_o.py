"""Phase O: privacy-safe product and planning analytics."""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from pydantic import ValidationError
from sqlalchemy import func, select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("ANALYTICS_HASH_SALT", "test-analytics-hash-salt")
os.environ["ADMIN_TOKEN"] = "test-admin-token"

from app.analytics.emitter import AnalyticsPayloadError, emit_event
from app.analytics.hashing import hash_session_id
from app.analytics.orm import AnalyticsEvent
from app.analytics.schemas import (
    DataCandidatesFoundPayload,
    EventName,
    ExampleViewedPayload,
    MissionCompletedPayload,
    MissionStartedPayload,
    PlanExportedPayload,
    PlanGeneratedPayload,
    PlanningFailurePayload,
    PlanningFailureReason,
    PlanSharedPayload,
    ProviderConnectionRequestedPayload,
    UserReturnedPayload,
)
from app.catalog.errors import CatalogUnavailableError
from app.catalog.planetary_computer import PROVIDER_ID
from app.catalog.types import CatalogItem
from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import AnonymousSession, MissionDataCandidate
from app.db.truth import TruthStatus
from app.deps.admin import verify_admin_token
from app.main import app, run_migrations

LEAK_MARKER = "LEAK_MARKER_PHASE_O_XYZZY_42"
LEAK_LON = -73.991234567
LEAK_LAT = 40.712345678
LEAK_AOI = {
    "type": "Polygon",
    "coordinates": [
        [
            [LEAK_LON, LEAK_LAT],
            [LEAK_LON + 0.5, LEAK_LAT],
            [LEAK_LON + 0.5, LEAK_LAT + 0.5],
            [LEAK_LON, LEAK_LAT + 0.5],
            [LEAK_LON, LEAK_LAT],
        ]
    ],
}
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


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _analytics_blob(db) -> str:
    rows = db.scalars(select(AnalyticsEvent)).all()
    return json.dumps([{"event": r.event_name, "payload": r.payload} for r in rows])


def _add_candidate(mission_id: str) -> None:
    db = SessionLocal(bind=get_engine())
    try:
        db.add(
            MissionDataCandidate(
                id=uuid.uuid4(),
                mission_id=uuid.UUID(mission_id),
                source_provider="microsoft-planetary-computer",
                collection="sentinel-1-grd",
                external_item_id="S1A_ANALYTICS_TEST",
                acquisition_time=datetime.now(timezone.utc),
                footprint=WKTElement(COVERING_WKT, srid=4326),
                asset_metadata={},
                estimated_size_bytes=50_000_000,
                source_url="https://example.test/stac/item",
                source_timestamp=datetime.now(timezone.utc),
                truth_status=TruthStatus.PROVIDER_REPORTED,
            )
        )
        db.commit()
    finally:
        db.close()


class FakeCatalog:
    provider_id = PROVIDER_ID

    def search(self, query):  # noqa: ANN001
        return [
            CatalogItem(
                source_provider=PROVIDER_ID,
                collection="sentinel-1-grd",
                external_item_id="S1A_ANALYTICS_DISCOVER",
                acquisition_time=datetime(2024, 1, 15, tzinfo=timezone.utc),
                footprint={
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-74.0, 40.5],
                            [-73.8, 40.5],
                            [-73.8, 40.7],
                            [-74.0, 40.7],
                            [-74.0, 40.5],
                        ]
                    ],
                },
                source_url="https://example.test/item",
                estimated_size_bytes=1_000_000,
                assets=[],
            )
        ]


class FailingCatalog:
    def search(self, query):  # noqa: ANN001
        raise CatalogUnavailableError("upstream timeout")


def test_emit_each_event_type_stored(client: TestClient):
    db = SessionLocal(bind=get_engine())
    try:
        now = datetime.now(timezone.utc)
        mid = uuid.uuid4()
        sid = uuid.uuid4()
        plan_id = uuid.uuid4()
        share_id = uuid.uuid4()
        session_hash = hash_session_id(sid)

        emit_event(
            db,
            EventName.MISSION_STARTED,
            MissionStartedPayload(
                mission_id=mid,
                session_id_hash=session_hash,
                resource_types_requested=["sentinel-1-grd"],
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.PLAN_GENERATED,
            PlanGeneratedPayload(
                mission_id=mid,
                plan_id=plan_id,
                step_count=4,
                candidate_count=2,
                generation_seconds=1.23,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.MISSION_COMPLETED,
            MissionCompletedPayload(
                mission_id=mid,
                plan_id=plan_id,
                session_id_hash=session_hash,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.DATA_CANDIDATES_FOUND,
            DataCandidatesFoundPayload(
                mission_id=mid,
                candidate_count=2,
                provider_id=PROVIDER_ID,
                search_duration_seconds=0.42,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.PLAN_EXPORTED,
            PlanExportedPayload(
                mission_id=mid,
                export_type="pdf",
                success=True,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.PLAN_SHARED,
            PlanSharedPayload(
                mission_id=mid,
                share_link_id=share_id,
                session_id_hash=session_hash,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.EXAMPLE_VIEWED,
            ExampleViewedPayload(mission_id=mid, timestamp=now),
        )
        emit_event(
            db,
            EventName.USER_RETURNED,
            UserReturnedPayload(
                session_id_hash=session_hash,
                days_since_last_seen=1.5,
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.PROVIDER_CONNECTION_REQUESTED,
            ProviderConnectionRequestedPayload(
                mission_id=mid,
                provider_name="KP Labs",
                integration_status="sandbox_requested",
                timestamp=now,
            ),
        )
        emit_event(
            db,
            EventName.PLANNING_FAILURE,
            PlanningFailurePayload(
                mission_id=mid,
                reason=PlanningFailureReason.NO_CANDIDATES_FOUND,
                timestamp=now,
            ),
        )
        db.commit()

        for event in EventName:
            count = db.scalar(
                select(func.count())
                .select_from(AnalyticsEvent)
                .where(AnalyticsEvent.event_name == event.value)
            )
            assert int(count or 0) >= 1, event.value
    finally:
        db.close()


def test_leak_test_no_sensitive_mission_content_in_analytics(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    """LEAK TEST: AOI coordinates and notes must not appear in analytics payloads."""
    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: FakeCatalog(),
    )
    _ensure_session(client)
    created = client.post(
        "/v1/missions",
        json={
            "title": "Leak probe mission",
            "objective_type": "analyze_imagery",
            "area_of_interest": LEAK_AOI,
            "notes": f"Proprietary mission notes {LEAK_MARKER}",
            "data_source_preference": ["sentinel-1-grd"],
            "start_time": "2024-01-01T00:00:00+00:00",
            "end_time": "2024-01-31T23:59:59+00:00",
        },
    )
    assert created.status_code == 201
    mission_id = created.json()["mission"]["id"]

    discover = client.post(f"/v1/missions/{mission_id}/discover", json={"limit": 5})
    assert discover.status_code == 200

    plans = client.post(f"/v1/missions/{mission_id}/plans")
    assert plans.status_code == 201

    db = SessionLocal(bind=get_engine())
    try:
        blob = _analytics_blob(db)
        assert LEAK_MARKER not in blob
        assert str(LEAK_LON) not in blob
        assert str(LEAK_LAT) not in blob
        assert "Proprietary mission notes" not in blob
        assert "area_of_interest" not in blob
        assert "notes" not in blob

        events = {
            row.event_name
            for row in db.scalars(
                select(AnalyticsEvent).where(
                    AnalyticsEvent.payload["mission_id"].as_string() == mission_id
                )
            ).all()
        }
        assert EventName.MISSION_STARTED.value in events
        assert EventName.DATA_CANDIDATES_FOUND.value in events
        assert EventName.PLAN_GENERATED.value in events
        assert EventName.MISSION_COMPLETED.value in events
    finally:
        db.close()


def test_rejection_test_extra_field_raises():
    db = SessionLocal(bind=get_engine())
    try:
        with pytest.raises((AnalyticsPayloadError, ValidationError)):
            emit_event(
                db,
                EventName.MISSION_STARTED,
                {
                    "mission_id": str(uuid.uuid4()),
                    "session_id_hash": "abc",
                    "resource_types_requested": ["sentinel-1-grd"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "aoi_geometry": {"type": "Polygon", "coordinates": []},
                },
            )
    finally:
        db.close()


def test_session_id_hash_is_stable_and_not_raw_session_id():
    session_id = uuid.uuid4()
    first = hash_session_id(session_id)
    second = hash_session_id(session_id)
    assert first == second
    assert str(session_id) not in first
    assert len(first) == 64


def test_planning_failure_enum_rejects_raw_exception_message():
    with pytest.raises(ValidationError):
        PlanningFailurePayload(
            mission_id=uuid.uuid4(),
            reason="Connection refused: upstream STAC host",  # type: ignore[arg-type]
            timestamp=datetime.now(timezone.utc),
        )


def test_admin_endpoint_requires_token(client: TestClient):
    denied = client.get("/v1/admin/analytics/summary")
    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "admin_unauthorized"

    allowed = client.get(
        "/v1/admin/analytics/summary",
        headers={"X-Nomos-Admin-Token": "test-admin-token"},
    )
    assert allowed.status_code == 200
    assert "traction" in allowed.json()


def test_admin_token_uses_constant_time_comparison():
    settings = get_settings()
    token = settings.admin_token
    assert token
    wrong_samples = [
        "",
        "x" * len(token),
        token[:-1] + ("x" if token[-1] != "x" else "y"),
        "wrong-" + token,
    ]
    timings_wrong = []
    for sample in wrong_samples:
        start = time.perf_counter()
        for _ in range(500):
            assert verify_admin_token(sample) is False
        timings_wrong.append(time.perf_counter() - start)

    start = time.perf_counter()
    for _ in range(500):
        assert verify_admin_token(token) is True
    timing_right = time.perf_counter() - start

    avg_wrong = sum(timings_wrong) / len(timings_wrong)
    # compare_digest should not be orders of magnitude slower for correct token.
    assert timing_right < avg_wrong * 5 + 0.05


def test_integration_flow_emits_expected_events(client: TestClient):
    _ensure_session(client)
    mission_id = client.post(
        "/v1/missions",
        json={
            "title": "Analytics integration",
            "objective_type": "analyze_imagery",
            "area_of_interest": {
                "type": "bbox",
                "coordinates": [-74.3, 40.3, -73.5, 41.0],
            },
            "data_source_preference": ["sentinel-1-grd"],
        },
    ).json()["mission"]["id"]
    _add_candidate(mission_id)
    assert client.post(f"/v1/missions/{mission_id}/plans").status_code == 201
    assert (
        client.post(
            f"/v1/missions/{mission_id}/share-links",
            json={"permissions": ["read"]},
        ).status_code
        == 201
    )

    db = SessionLocal(bind=get_engine())
    try:
        names = {
            row.event_name
            for row in db.scalars(
                select(AnalyticsEvent).where(
                    AnalyticsEvent.payload["mission_id"].as_string() == mission_id
                )
            ).all()
        }
        assert EventName.MISSION_STARTED.value in names
        assert EventName.PLAN_GENERATED.value in names
        assert EventName.MISSION_COMPLETED.value in names
        assert EventName.PLAN_SHARED.value in names
    finally:
        db.close()


def test_catalog_failure_emits_planning_failure_enum(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: FailingCatalog(),
    )
    _ensure_session(client)
    mission_id = client.post(
        "/v1/missions",
        json={
            "title": "Catalog fail",
            "objective_type": "analyze_imagery",
            "area_of_interest": {
                "type": "bbox",
                "coordinates": [-74.3, 40.3, -73.5, 41.0],
            },
        },
    ).json()["mission"]["id"]
    response = client.post(f"/v1/missions/{mission_id}/discover", json={})
    assert response.status_code == 503

    db = SessionLocal(bind=get_engine())
    try:
        row = db.scalars(
            select(AnalyticsEvent)
            .where(AnalyticsEvent.event_name == EventName.PLANNING_FAILURE.value)
            .order_by(AnalyticsEvent.created_at.desc())
        ).first()
        assert row is not None
        assert row.payload["reason"] == PlanningFailureReason.PROVIDER_TIMEOUT.value
        assert "timed out" not in json.dumps(row.payload).lower()
    finally:
        db.close()


def test_raw_session_id_not_in_stored_events(client: TestClient):
    _ensure_session(client)
    db = SessionLocal(bind=get_engine())
    try:
        session_row = db.scalars(select(AnonymousSession)).first()
        assert session_row is not None
        raw_id = str(session_row.id)
        client.post(
            "/v1/missions",
            json={
                "title": "Hash probe",
                "objective_type": "analyze_imagery",
                "area_of_interest": {
                    "type": "bbox",
                    "coordinates": [-74.3, 40.3, -73.5, 41.0],
                },
            },
        )
        blob = _analytics_blob(db)
        assert raw_id not in blob
    finally:
        db.close()
