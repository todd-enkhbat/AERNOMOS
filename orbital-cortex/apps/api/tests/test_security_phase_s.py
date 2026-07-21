"""Phase S security tests: access isolation, enumeration, SSRF, redaction."""

from __future__ import annotations

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from fastapi.testclient import TestClient

from app.main import app
from app.security.redaction import redact_request_path
from app.security.remote_urls import RemoteUrlError, assert_remote_url_allowed
from tests.job_auth import create_private_job

AOI = {
    "type": "Polygon",
    "coordinates": [
        [
            [-74.05, 40.68],
            [-73.95, 40.68],
            [-73.95, 40.75],
            [-74.05, 40.75],
            [-74.05, 40.68],
        ]
    ],
}

MISSION_PAYLOAD = {
    "title": "Security review mission",
    "objective_type": "analyze_imagery",
    "area_of_interest": AOI,
}


def _session_client() -> TestClient:
    return TestClient(app)


def test_cross_session_mission_access_denied():
    owner = _session_client()
    stranger = _session_client()
    assert owner.post("/v1/sessions").status_code == 201
    assert stranger.post("/v1/sessions").status_code == 201

    created = owner.post("/v1/missions", json=MISSION_PAYLOAD)
    assert created.status_code == 201
    mission_id = created.json()["mission"]["id"]

    listed = stranger.get("/v1/missions")
    assert listed.status_code == 200
    assert mission_id not in {m["id"] for m in listed.json()["missions"]}

    denied = stranger.get(f"/v1/missions/{mission_id}")
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "mission_forbidden"


def test_missions_not_publicly_enumerable_without_session():
    with _session_client() as client:
        listed = client.get("/v1/missions")
        assert listed.status_code == 401
        assert listed.json()["error"]["code"] == "session_required"


def test_share_revoke_blocks_further_access():
    owner = _session_client()
    assert owner.post("/v1/sessions").status_code == 201
    created = owner.post("/v1/missions", json=MISSION_PAYLOAD)
    mission_id = created.json()["mission"]["id"]

    share = owner.post(f"/v1/missions/{mission_id}/share-links", json={})
    assert share.status_code == 201
    raw = share.json()["share_link"]["token"]
    link_id = share.json()["share_link"]["id"]

    reader = _session_client()
    ok = reader.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": raw},
    )
    assert ok.status_code == 200

    revoked = owner.post(f"/v1/missions/{mission_id}/share-links/{link_id}/revoke")
    assert revoked.status_code == 200

    blocked = reader.get(
        f"/v1/missions/{mission_id}",
        headers={"X-Nomos-Share-Token": raw},
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "share_token_invalid"


def test_private_job_requires_access_token_enumeration_resistance():
    with _session_client() as client:
        job_id, headers = create_private_job(
            client,
            {
                "job_type": "ship_detection",
                "area_of_interest": {
                    "type": "bbox",
                    "coordinates": [-74.3, 40.3, -73.5, 41.0],
                },
                "sensor": "SAR",
                "priority": "fastest",
                "compute_preference": "orbital_if_available",
                "max_cost_usd": 100,
            },
        )

        listed = client.get("/v1/jobs")
        assert job_id not in {j["id"] for j in listed.json()["jobs"]}

        assert client.get(f"/v1/jobs/{job_id}").status_code == 401
        assert client.get(f"/v1/jobs/{job_id}", headers=headers).status_code == 200
        assert (
            client.get(
                f"/v1/jobs/{job_id}",
                headers={"X-Nomos-Job-Token": "not-the-real-token"},
            ).status_code
            == 403
        )


def test_ssrf_blocked_hosts():
    blocked = [
        "http://planetarycomputer.microsoft.com/api/stac/v1",
        "https://evil.example.com/steal",
        "https://127.0.0.1/admin",
        "https://169.254.169.254/latest/meta-data/",
        "https://localhost/secret",
        "ftp://planetarycomputer.microsoft.com/x",
    ]
    for url in blocked:
        try:
            assert_remote_url_allowed(url)
            raise AssertionError(f"expected block for {url}")
        except RemoteUrlError:
            pass

    # Allowlisted Planetary Computer host (may still fail DNS in offline CI —
    # accept either allow or resolve failure that is not an allowlist miss).
    try:
        assert_remote_url_allowed(
            "https://planetarycomputer.microsoft.com/api/stac/v1/collections"
        )
    except RemoteUrlError as exc:
        assert "not on the remote fetch allowlist" not in str(exc)


def test_share_token_redacted_from_request_path():
    raw = "super-secret-share-token-value"
    path = f"/v1/share/{raw}"
    redacted = redact_request_path(path)
    assert raw not in redacted
    assert "[redacted]" in redacted
    assert redact_request_path("/v1/missions") == "/v1/missions"


def test_share_permissions_write_rejected():
    owner = _session_client()
    assert owner.post("/v1/sessions").status_code == 201
    mission_id = owner.post("/v1/missions", json=MISSION_PAYLOAD).json()["mission"]["id"]
    bad = owner.post(
        f"/v1/missions/{mission_id}/share-links",
        json={"permissions": ["write"]},
    )
    assert bad.status_code == 422
