"""Group E/F platform tests: health probes, pagination, artifacts,
rate limiting, and the demo-reset guard."""

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import time
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.main import app, run_migrations

PAYLOAD = {
    "job_type": "ship_detection",
    "area_of_interest": {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
    "sensor": "SAR",
    "priority": "fastest",
    "compute_preference": "orbital_if_available",
    "max_cost_usd": 500,
}


def _reset_job_data() -> None:
    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        session.execute(text("DELETE FROM jobs"))
        session.commit()
    finally:
        session.close()


def test_health_probes():
    with TestClient(app) as client:
        healthz = client.get("/healthz")
        assert healthz.status_code == 200
        assert healthz.json()["status"] == "ok"

        readyz = client.get("/readyz")
        assert readyz.status_code == 200
        body = readyz.json()
        assert body["status"] == "ready"
        assert body["checks"]["database"] is True
        # Redis is intentionally unreachable in tests and must not gate
        # readiness (jobs fall back to the manual execution path).
        assert body["checks"]["redis"] is False

        # Responses carry the request-ID header from the logging middleware.
        assert healthz.headers["x-request-id"]


def test_jobs_cursor_pagination():
    _reset_job_data()

    with TestClient(app) as client:
        created_ids = [
            client.post("/v1/jobs", json=PAYLOAD).json()["job"]["id"] for _ in range(3)
        ]

        first = client.get("/v1/jobs", params={"limit": 2})
        assert first.status_code == 200
        page1 = first.json()
        assert len(page1["jobs"]) == 2
        assert page1["next_cursor"]

        second = client.get(
            "/v1/jobs", params={"limit": 2, "cursor": page1["next_cursor"]}
        )
        assert second.status_code == 200
        page2 = second.json()
        assert len(page2["jobs"]) == 1

        ids1 = {job["id"] for job in page1["jobs"]}
        ids2 = {job["id"] for job in page2["jobs"]}
        assert ids1.isdisjoint(ids2)
        assert ids1 | ids2 == set(created_ids)

        bad = client.get("/v1/jobs", params={"cursor": "%%%not-base64"})
        assert bad.status_code == 400
        assert bad.json()["error"]["code"] == "invalid_cursor"


def test_contact_windows_cursor_pagination():
    with TestClient(app) as client:
        first = client.get("/v1/contact-windows", params={"limit": 5})
        assert first.status_code == 200
        page1 = first.json()
        assert len(page1["contact_windows"]) == 5
        assert page1["next_cursor"]

        second = client.get(
            "/v1/contact-windows",
            params={"limit": 5, "cursor": page1["next_cursor"]},
        )
        assert second.status_code == 200
        page2 = second.json()
        assert page2["contact_windows"]

        ids1 = {w["id"] for w in page1["contact_windows"]}
        ids2 = {w["id"] for w in page2["contact_windows"]}
        assert ids1.isdisjoint(ids2)
        # Keyset ordering continues across the page boundary.
        assert page2["contact_windows"][0]["aos_utc"] >= page1["contact_windows"][-1]["aos_utc"]


def test_result_artifacts_served_via_signed_urls():
    _reset_job_data()

    with TestClient(app) as client:
        job_id = client.post("/v1/jobs", json=PAYLOAD).json()["job"]["id"]
        assert client.post(f"/v1/simulate/run/{job_id}").status_code == 200

        response = client.get(f"/v1/jobs/{job_id}/result")
        assert response.status_code == 200
        body = response.json()

        # F1 DoD: the DB row holds object keys, not URLs or inline blobs.
        assert body["result"]["output_files"]
        assert all("://" not in key for key in body["result"]["output_files"])
        assert {a["key"] for a in body["artifacts"]} == set(
            body["result"]["output_files"]
        )

        detections = next(
            a for a in body["artifacts"] if a["key"].endswith("detections.geojson")
        )
        parsed = urlparse(detections["url"])
        fetched = client.get(f"{parsed.path}?{parsed.query}")
        assert fetched.status_code == 200
        assert fetched.headers["content-type"].startswith("application/geo+json")
        assert fetched.json()["type"] == "FeatureCollection"

        tampered = client.get(
            f"{parsed.path}?{parsed.query.replace('signature=', 'signature=00')}"
        )
        assert tampered.status_code == 403
        assert tampered.json()["error"]["code"] == "invalid_signature"


def test_expired_artifact_signature_is_rejected():
    from app.core.object_store import _local_signature

    settings = get_settings()
    key = "results/anything/detections.geojson"
    expired = int(time.time()) - 10
    signature = _local_signature(settings.artifact_signing_secret, key, expired)

    with TestClient(app) as client:
        response = client.get(
            f"/v1/artifacts/{key}",
            params={"expires": expired, "signature": signature},
        )
        assert response.status_code == 403


def test_rate_limit_on_job_creation(monkeypatch):
    _reset_job_data()
    from app.core import ratelimit

    monkeypatch.setenv("RATE_LIMIT_JOBS", "2/minute")
    get_settings.cache_clear()
    ratelimit.limiter.reset()
    ratelimit.limiter.enabled = True
    try:
        with TestClient(app) as client:
            assert client.post("/v1/jobs", json=PAYLOAD).status_code == 201
            assert client.post("/v1/jobs", json=PAYLOAD).status_code == 201
            limited = client.post("/v1/jobs", json=PAYLOAD)
            assert limited.status_code == 429
            assert limited.json()["error"]["code"] == "rate_limited"
    finally:
        ratelimit.limiter.enabled = False
        monkeypatch.undo()
        get_settings.cache_clear()


def test_seed_reset_refuses_production_without_force(monkeypatch):
    from app import seed
    from app.core.config import Settings

    monkeypatch.setattr(
        seed, "get_settings", lambda: Settings(app_env="production")
    )
    with pytest.raises(SystemExit) as ctx:
        seed.main(["--reset"])
    assert "Refusing" in str(ctx.value)


def test_seed_reset_wipes_jobs_and_reseeds():
    from app import seed

    _reset_job_data()
    with TestClient(app) as client:
        client.post("/v1/jobs", json=PAYLOAD)

    # Development environment: --reset needs no --force.
    seed.main(["--reset"])

    session = SessionLocal(bind=get_engine())
    try:
        remaining = session.execute(text("SELECT count(*) FROM jobs")).scalar()
        stations = session.execute(
            text("SELECT count(*) FROM ground_stations")
        ).scalar()
    finally:
        session.close()
    assert remaining == 0
    assert stations == 6
