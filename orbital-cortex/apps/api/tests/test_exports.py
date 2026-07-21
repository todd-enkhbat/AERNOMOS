"""Phase K: mission brief JSON/PDF exports and share isolation."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import ShareLink
from app.exports.json_document import JSON_SCHEMA_VERSION
from app.main import app, run_migrations

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}


def _mission_payload(title: str = "Export mission") -> dict:
    return {
        "title": title,
        "objective_type": "analyze_imagery",
        "area_of_interest": AOI,
        "notes": "export test",
    }


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _create_mission(client: TestClient, title: str = "Export mission") -> str:
    _ensure_session(client)
    created = client.post("/v1/missions", json=_mission_payload(title))
    assert created.status_code == 201
    return created.json()["mission"]["id"]


def test_json_export_schema_version_and_auth(client: TestClient):
    mission_id = _create_mission(client)

    ok = client.get(f"/v1/missions/{mission_id}/exports/json")
    assert ok.status_code == 200
    body = ok.json()
    assert body["schema_version"] == JSON_SCHEMA_VERSION
    assert body["document_type"] == "nomos_mission_brief"
    assert body["mission_input"]["id"] == mission_id
    assert "truth_statuses" in body
    assert body["truth_statuses"]["legend"]
    assert "disclosures" in body
    assert "simulation_boundary" in body["disclosures"]

    stranger = TestClient(app)
    denied = stranger.get(f"/v1/missions/{mission_id}/exports/json")
    assert denied.status_code == 401

    other = TestClient(app)
    assert other.post("/v1/sessions").status_code == 201
    forbidden = other.get(f"/v1/missions/{mission_id}/exports/json")
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "mission_forbidden"
    other.close()
    stranger.close()


def test_json_export_via_share_and_isolation(client: TestClient):
    mission_a = _create_mission(client, "Share export A")
    share = client.post(
        f"/v1/missions/{mission_a}/share-links",
        json={"permissions": ["read"]},
    )
    assert share.status_code == 201
    token = share.json()["share_link"]["token"]

    client_b = TestClient(app)
    assert client_b.post("/v1/sessions").status_code == 201
    mission_b = client_b.post(
        "/v1/missions", json=_mission_payload("Share export B")
    ).json()["mission"]["id"]

    stranger = TestClient(app)
    ok = stranger.get(
        f"/v1/missions/{mission_a}/exports/json",
        headers={"X-Nomos-Share-Token": token},
    )
    assert ok.status_code == 200
    assert ok.json()["mission_input"]["id"] == mission_a

    # Share for A must not open B.
    leak = stranger.get(
        f"/v1/missions/{mission_b}/exports/json",
        headers={"X-Nomos-Share-Token": token},
    )
    assert leak.status_code == 403
    assert leak.json()["error"]["code"] == "share_token_invalid"

    # Resolve endpoint returns only mission_id.
    resolved = stranger.get(f"/v1/share/{token}")
    assert resolved.status_code == 200
    assert resolved.json()["mission_id"] == mission_a
    assert "mission_input" not in resolved.json()

    client_b.close()
    stranger.close()


def test_share_resolve_revoked_and_expired(client: TestClient):
    mission_id = _create_mission(client, "Revoke share")
    share = client.post(
        f"/v1/missions/{mission_id}/share-links",
        json={"permissions": ["read"]},
    )
    token = share.json()["share_link"]["token"]
    share_id = share.json()["share_link"]["id"]

    stranger = TestClient(app)
    assert stranger.get(f"/v1/share/{token}").status_code == 200

    revoked = client.post(f"/v1/missions/{mission_id}/share-links/{share_id}/revoke")
    assert revoked.status_code == 200
    denied = stranger.get(f"/v1/share/{token}")
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "share_token_invalid"

    # Fresh link then force-expire in DB (keep expires_at >= created_at for CHECK).
    share2 = client.post(
        f"/v1/missions/{mission_id}/share-links",
        json={"permissions": ["read"]},
    )
    token2 = share2.json()["share_link"]["token"]
    share2_id = share2.json()["share_link"]["id"]

    session = SessionLocal(bind=get_engine())
    try:
        link = session.get(ShareLink, __import__("uuid").UUID(share2_id))
        assert link is not None
        past = datetime.now(timezone.utc) - timedelta(days=2)
        link.created_at = past
        link.expires_at = past + timedelta(hours=1)
        session.commit()
    finally:
        session.close()

    expired = stranger.get(f"/v1/share/{token2}")
    assert expired.status_code == 403
    assert expired.json()["error"]["code"] == "share_token_invalid"
    stranger.close()


def test_pdf_export_owner_only_mocked(client: TestClient):
    mission_id = _create_mission(client, "PDF mission")

    fake_pdf = b"%PDF-1.4 fake mission brief"

    with patch(
        "app.exports.service.render_mission_brief_pdf",
        return_value=fake_pdf,
    ):
        created = client.post(f"/v1/missions/{mission_id}/exports/pdf")
    assert created.status_code == 201
    export = created.json()["export"]
    assert export["status"] == "ready"
    assert export["export_type"] == "pdf"
    assert export["download_url"]
    assert export["artifact_key"]
    assert export["artifact_key"].endswith(".pdf")

    status = client.get(f"/v1/missions/{mission_id}/exports/pdf")
    assert status.status_code == 200
    assert status.json()["export"]["id"] == export["id"]

    by_id = client.get(f"/v1/missions/{mission_id}/exports/pdf/{export['id']}")
    assert by_id.status_code == 200

    other = TestClient(app)
    assert other.post("/v1/sessions").status_code == 201
    forbidden = other.post(f"/v1/missions/{mission_id}/exports/pdf")
    assert forbidden.status_code == 403
    other.close()


def test_pdf_html_template_smoke():
    from app.exports.json_document import TRUTH_STATUS_LEGEND
    from app.exports.pdf import render_mission_brief_html

    doc = {
        "schema_version": JSON_SCHEMA_VERSION,
        "document_type": "nomos_mission_brief",
        "generated_at": "2026-07-17T00:00:00+00:00",
        "mission_input": {
            "id": "00000000-0000-4000-8000-000000000001",
            "title": "Smoke brief",
            "objective_type": "analyze_imagery",
            "status": "exploratory",
            "start_time": None,
            "end_time": None,
            "deadline": None,
            "notes": "template smoke",
        },
        "geographic_summary": {
            "geometry_type": "bbox",
            "bbox": [-74.3, 40.3, -73.5, 41.0],
            "note": "static",
        },
        "selected_plan": {
            "status": "conditional",
            "recommended": True,
            "summary": "Use existing imagery",
            "estimated_total_time_seconds": 120,
            "estimated_total_cost_usd": None,
            "explanation": {"why_recommended": "Best available path"},
            "steps": [
                {
                    "sequence": 1,
                    "title": "Select scene",
                    "description": "Catalog candidate",
                    "provider_name": "microsoft-planetary-computer",
                    "feasibility_status": "feasible",
                    "truth_status": "PROVIDER_REPORTED",
                    "rejection_reason": None,
                }
            ],
        },
        "candidate_plans": [
            {
                "version": 1,
                "summary": "Use existing imagery",
                "status": "conditional",
                "recommended": True,
            }
        ],
        "assumptions": [{"kind": "planner_meta", "pattern": "existing_imagery_cloud"}],
        "source_evidence": [
            {
                "source_name": "Planetary Computer",
                "source_type": "catalog",
                "truth_status": "PROVIDER_REPORTED",
                "retrieved_at": "2026-07-17T00:00:00+00:00",
            }
        ],
        "truth_statuses": {"legend": TRUTH_STATUS_LEGEND},
        "missing_integrations": ["Satellite tasking / reservation API"],
        "next_actions": ["Connect a satellite tasking provider account"],
        "disclosures": {
            "simulation_boundary": "Demo disclosure text.",
        },
    }
    html = render_mission_brief_html(doc)
    assert "Smoke brief" in html
    assert "Executive summary" in html
    assert "Appendix A" in html
    assert "Planning only" in html


def test_pdf_weasyprint_integration_optional():
    """Real WeasyPrint smoke when system libs are present; otherwise skip."""
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError) as exc:
        pytest.skip(f"WeasyPrint unavailable: {exc}")

    from app.exports.pdf import render_mission_brief_pdf

    html = (
        "<html><body><h1>Nomos PDF smoke</h1>"
        "<p>SIMULATED disclosure present.</p></body></html>"
    )
    try:
        pdf = render_mission_brief_pdf({}, html_override=html)
    except Exception as exc:  # pragma: no cover - OS lib gaps in some CI images
        pytest.skip(f"WeasyPrint runtime unavailable: {exc}")
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 100
