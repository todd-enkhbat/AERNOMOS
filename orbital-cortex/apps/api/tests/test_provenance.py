"""Phase G: provenance envelope serialization and OpenAPI exposure."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.db.truth import TruthStatus
from app.main import app, run_migrations
from app.models.provenance import (
    EXPLANATION_CALCULATED_CONTACT,
    EXPLANATION_SIMULATED,
    freshness_for,
    provenanced,
)
from app.services.contact_windows import window_to_api


def test_provenanced_helper_shape():
    envelope = provenanced(
        42.5,
        TruthStatus.CALCULATED,
        source="CelesTrak TLE snapshot celestrak-test",
        retrieved_at="2026-07-01T12:00:00+00:00",
        method="SGP4 via Skyfield",
        explanation=EXPLANATION_CALCULATED_CONTACT,
    )
    assert envelope["value"] == 42.5
    assert envelope["truth_status"] == "CALCULATED"
    assert envelope["source"].startswith("CelesTrak TLE snapshot")
    assert envelope["freshness"] in {"fresh", "stale", "unknown"}


def test_freshness_for_stale_and_simulated():
    assert freshness_for(TruthStatus.STALE) == "stale"
    assert freshness_for(TruthStatus.SIMULATED) == "unknown"
    assert freshness_for(TruthStatus.UNAVAILABLE) == "stale"


def test_window_to_api_wraps_numeric_fields():
    from types import SimpleNamespace

    window = SimpleNamespace(
        id="cw_test",
        satellite_id="sat_sentinel_1a",
        ground_station_id="gs_ksat_svalbard",
        date="2026-07-16",
        aos_utc="2026-07-16T10:00:00+00:00",
        culminate_utc="2026-07-16T10:05:00+00:00",
        los_utc="2026-07-16T10:10:00+00:00",
        max_elevation_deg=45.2,
        duration_s=600.0,
        est_downlink_mb=39000.0,
        tle_snapshot_id="celestrak-20260716",
    )
    payload = window_to_api(
        window,  # type: ignore[arg-type]
        snapshot_id="celestrak-20260716",
        retrieved_at="2026-07-16T08:00:00+00:00",
    )
    assert payload["aos_utc"]["value"] == "2026-07-16T10:00:00+00:00"
    assert payload["aos_utc"]["truth_status"] == "CALCULATED"
    assert payload["est_downlink_mb"]["truth_status"] == "ESTIMATED"
    assert payload["duration_s"]["method"] == "SGP4 via Skyfield"


def test_openapi_includes_provenanced_value():
    run_migrations()
    schema = app.openapi()
    provenanced_schema = schema["components"]["schemas"]["ProvenancedValue"]
    assert "truth_status" in provenanced_schema["properties"]
    assert "value" in provenanced_schema["properties"]
    contact = schema["components"]["schemas"]["ContactWindow"]
    assert contact["properties"]["aos_utc"]["$ref"].endswith("ProvenancedValue")


@pytest.fixture()
def client():
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def test_catalog_candidate_provenance_in_api(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    from datetime import datetime, timezone

    from app.catalog.types import CatalogItem

    item = CatalogItem(
        source_provider="microsoft-planetary-computer",
        collection="sentinel-1-grd",
        external_item_id="S1A_TEST",
        acquisition_time=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        footprint={
            "type": "Polygon",
            "coordinates": [
                [
                    [-74.1, 40.6],
                    [-73.9, 40.6],
                    [-73.9, 40.8],
                    [-74.1, 40.8],
                    [-74.1, 40.6],
                ]
            ],
        },
        estimated_size_bytes=1_500_000_000,
        source_url="https://example.test/item",
        assets=[],
    )

    class FakeProvider:
        provider_id = "microsoft-planetary-computer"

        def search(self, query):
            return [item]

        def get_item(self, collection, external_item_id):
            return item

        def get_assets(self, collection, external_item_id):
            return []

    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: FakeProvider(),
    )

    assert client.post("/v1/sessions").status_code in (200, 201)
    mission_id = client.post(
        "/v1/missions",
        json={
            "title": "provenance test",
            "objective_type": "analyze_imagery",
            "area_of_interest": {
                "type": "bbox",
                "coordinates": [-74.3, 40.3, -73.5, 41.0],
            },
        },
    ).json()["mission"]["id"]

    discover = client.post(f"/v1/missions/{mission_id}/discover", json={"limit": 5})
    assert discover.status_code == 200
    candidate = discover.json()["candidates"][0]
    assert candidate["acquisition_time"]["truth_status"] == "PROVIDER_REPORTED"
    assert candidate["acquisition_time"]["value"]
    assert candidate["estimated_size_bytes"]["truth_status"] == "ESTIMATED"


def test_simulated_explanation_constant():
    assert "demonstration" in EXPLANATION_SIMULATED.lower()
