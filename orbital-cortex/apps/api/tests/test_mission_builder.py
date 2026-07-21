"""Phase E: guided mission builder validation and ownership."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.core.mission_geo import MAX_AOI_AREA_KM2, aoi_area_km2, validate_area_of_interest
from app.main import app, run_migrations

VALID_AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}


def _payload(**overrides: object) -> dict:
    body: dict = {
        "title": "Harbor awareness plan",
        "objective_type": "analyze_imagery",
        "area_of_interest": VALID_AOI,
        "status": "exploratory",
        "notes": "Builder test",
    }
    body.update(overrides)
    return body


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _validation_text(response) -> str:
    body = response.json()
    detail = body.get("detail")
    if detail is not None:
        return str(detail).lower()
    error = body.get("error") or {}
    parts = [error.get("message"), error.get("details"), error.get("code")]
    return " ".join(str(part) for part in parts if part is not None).lower()


def test_aoi_area_helpers_reject_continent_scale():
    huge = {"type": "bbox", "coordinates": [-120.0, 20.0, -60.0, 50.0]}
    assert aoi_area_km2(huge) > MAX_AOI_AREA_KM2
    with pytest.raises(ValueError, match="too large"):
        validate_area_of_interest(huge)


def test_create_mission_missing_title_422(client: TestClient):
    _ensure_session(client)
    response = client.post("/v1/missions", json=_payload(title="   "))
    assert response.status_code == 422
    assert "title" in _validation_text(response)


def test_create_mission_invalid_geojson_type_422(client: TestClient):
    _ensure_session(client)
    response = client.post(
        "/v1/missions",
        json=_payload(
            area_of_interest={
                "type": "Point",
                "coordinates": [-74.0, 40.7],
            }
        ),
    )
    assert response.status_code == 422
    assert "area" in _validation_text(response) or "polygon" in _validation_text(
        response
    )


def test_create_mission_oversized_aoi_422(client: TestClient):
    _ensure_session(client)
    response = client.post(
        "/v1/missions",
        json=_payload(
            area_of_interest={
                "type": "bbox",
                "coordinates": [-120.0, 20.0, -60.0, 50.0],
            }
        ),
    )
    assert response.status_code == 422
    assert "large" in _validation_text(response) or "area" in _validation_text(
        response
    )


def test_create_mission_invalid_objective_422(client: TestClient):
    _ensure_session(client)
    response = client.post(
        "/v1/missions",
        json=_payload(objective_type="submit_compute_job"),
    )
    assert response.status_code == 422


def test_create_mission_valid_201_owned_by_session(client: TestClient):
    _ensure_session(client)
    response = client.post(
        "/v1/missions",
        json=_payload(
            organization_name="Acme Earth Observation",
            use_case="Port traffic awareness",
            max_age_days=14,
            onboard_processing="preferred",
            data_residency="EU",
            preferred_compute_location="ground",
            max_cost_usd=250,
            data_source_preference=["sentinel-1"],
            allowed_regions=["EU", "US"],
            customer_systems=[{"kind": "cloud_provider", "provider": "aws"}],
        ),
    )
    assert response.status_code == 201, response.text
    mission = response.json()["mission"]
    assert mission["title"] == "Harbor awareness plan"
    assert mission["objective_type"] == "analyze_imagery"
    assert mission["status"] == "exploratory"
    assert mission["anonymous_session_id"]
    assert mission["is_example"] is False
    systems = mission["customer_systems"]
    kinds = {item.get("kind") for item in systems if isinstance(item, dict)}
    assert "organization" in kinds
    assert "data_freshness" in kinds
    assert "onboard_processing" in kinds
    assert "cloud_provider" in kinds

    listed = client.get("/v1/missions")
    assert listed.status_code == 200
    assert any(m["id"] == mission["id"] for m in listed.json()["missions"])


def test_cross_session_cannot_see_builder_mission(client: TestClient):
    client_a = TestClient(app)
    client_b = TestClient(app)
    assert client_a.post("/v1/sessions").status_code == 201
    assert client_b.post("/v1/sessions").status_code == 201

    created = client_a.post("/v1/missions", json=_payload(title="Session A plan"))
    assert created.status_code == 201
    mission_id = created.json()["mission"]["id"]

    listed_b = client_b.get("/v1/missions")
    assert listed_b.status_code == 200
    assert listed_b.json()["missions"] == []

    forbidden = client_b.get(f"/v1/missions/{mission_id}")
    assert forbidden.status_code == 403

    client_a.close()
    client_b.close()
