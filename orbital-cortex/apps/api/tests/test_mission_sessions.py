"""Phase C: anonymous sessions, mission isolation, and share-link access."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.core.tokens import hash_token
from app.db import SessionLocal, get_engine
from app.db.mission_orm import ShareLink
from app.main import app, run_migrations

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}


def _mission_payload(title: str = "Private mission") -> dict:
    return {
        "title": title,
        "objective_type": "ship_detection",
        "area_of_interest": AOI,
        "notes": "test",
    }


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ensure_session(client: TestClient) -> TestClient:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)
    assert get_settings().session_cookie_name in client.cookies
    cookie = response.cookies.get(get_settings().session_cookie_name)
    assert cookie
    # Cookie must never echo the raw token in JSON.
    assert "token" not in response.json().get("session", {})
    return client


def test_session_cookie_flags_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SESSION_COOKIE_DOMAIN", ".nomosorbital.com")
    get_settings.cache_clear()
    run_migrations()

    with TestClient(app) as client:
        response = client.post("/v1/sessions")
        assert response.status_code == 201
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie or "httponly" in set_cookie.lower()
        assert "Secure" in set_cookie or "secure" in set_cookie.lower()
        assert "SameSite=lax" in set_cookie or "samesite=lax" in set_cookie.lower()
        assert "Domain=.nomosorbital.com" in set_cookie

    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("SESSION_COOKIE_DOMAIN", raising=False)
    get_settings.cache_clear()


def test_two_sessions_cannot_see_each_others_missions(client: TestClient):
    client_a = TestClient(app)
    client_b = TestClient(app)

    assert client_a.post("/v1/sessions").status_code == 201
    assert client_b.post("/v1/sessions").status_code == 201

    created = client_a.post("/v1/missions", json=_mission_payload("A only"))
    assert created.status_code == 201
    mission_id = created.json()["mission"]["id"]

    listed_a = client_a.get("/v1/missions")
    assert listed_a.status_code == 200
    assert {m["id"] for m in listed_a.json()["missions"]} == {mission_id}

    listed_b = client_b.get("/v1/missions")
    assert listed_b.status_code == 200
    assert listed_b.json()["missions"] == []

    forbidden = client_b.get(f"/v1/missions/{mission_id}")
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "mission_forbidden"

    client_a.close()
    client_b.close()


def test_missions_not_publicly_enumerable(client: TestClient):
    _ensure_session(client)
    created = client.post("/v1/missions", json=_mission_payload("hidden"))
    assert created.status_code == 201
    mission_id = created.json()["mission"]["id"]

    # Fresh client with no cookie cannot list or read.
    stranger = TestClient(app)
    assert stranger.get("/v1/missions").status_code == 401
    missing = stranger.get(f"/v1/missions/{mission_id}")
    assert missing.status_code == 401
    stranger.close()


def test_share_link_access_revoke_and_expiry(client: TestClient):
    _ensure_session(client)
    created = client.post("/v1/missions", json=_mission_payload("share me"))
    mission_id = created.json()["mission"]["id"]

    share = client.post(
        f"/v1/missions/{mission_id}/share-links",
        json={"permissions": ["read"]},
    )
    assert share.status_code == 201
    body = share.json()["share_link"]
    token = body["token"]
    share_id = body["id"]
    assert token
    assert "token_hash" not in body

    stranger = TestClient(app)
    ok = stranger.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": token},
    )
    assert ok.status_code == 200
    assert ok.json()["mission"]["id"] == mission_id

    # Query param also works.
    ok_q = stranger.get(f"/v1/missions/{mission_id}", params={"share_token": token})
    assert ok_q.status_code == 200

    revoked = client.post(
        f"/v1/missions/{mission_id}/share-links/{share_id}/revoke"
    )
    assert revoked.status_code == 200
    assert revoked.json()["share_link"]["revoked_at"] is not None

    denied = stranger.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": token},
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "share_token_invalid"

    # Expired link fails.
    share2 = client.post(
        f"/v1/missions/{mission_id}/share-links",
        json={"permissions": ["read"]},
    )
    token2 = share2.json()["share_link"]["token"]
    session = SessionLocal(bind=get_engine())
    try:
        from sqlalchemy import select

        link = session.scalars(
            select(ShareLink).where(ShareLink.token_hash == hash_token(token2))
        ).one()
        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        link.created_at = past
        link.expires_at = past + timedelta(minutes=1)
        session.commit()
    finally:
        session.close()

    expired = stranger.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": token2},
    )
    assert expired.status_code == 403
    stranger.close()


def test_example_missions_are_public_and_marked(client: TestClient):
    examples = client.get("/v1/missions/examples")
    assert examples.status_code == 200
    missions = examples.json()["missions"]
    assert missions
    assert len(missions) >= 4
    assert all(m["is_example"] is True for m in missions)

    # Examples must not appear in a private session list.
    _ensure_session(client)
    private = client.get("/v1/missions")
    assert private.status_code == 200
    assert all(m["is_example"] is False for m in private.json()["missions"])


def test_invalid_share_token_rejected(client: TestClient):
    _ensure_session(client)
    created = client.post("/v1/missions", json=_mission_payload())
    mission_id = created.json()["mission"]["id"]

    stranger = TestClient(app)
    bad = stranger.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": "not-a-real-token"},
    )
    assert bad.status_code == 403
    stranger.close()


def test_legacy_jobs_still_work_alongside_missions(client: TestClient):
    """Demo job path remains available; missions do not break it."""
    payload = {
        "job_type": "ship_detection",
        "area_of_interest": AOI,
        "sensor": "SAR",
        "priority": "fastest",
        "compute_preference": "orbital_if_available",
        "max_cost_usd": 100,
    }
    response = client.post("/v1/jobs", json=payload)
    assert response.status_code == 201
    job_id = response.json()["job"]["id"]

    session = SessionLocal(bind=get_engine())
    try:
        session.execute(text("DELETE FROM jobs WHERE id = :id"), {"id": job_id})
        session.commit()
    finally:
        session.close()
