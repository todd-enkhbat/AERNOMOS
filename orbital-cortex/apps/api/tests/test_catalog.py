"""Phase F: STAC catalog discovery (mocked Planetary Computer)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.catalog.errors import CatalogUnavailableError
from app.catalog.planetary_computer import (
    PROVIDER_ID,
    PlanetaryComputerCatalog,
    stac_item_to_catalog_item,
)
from app.catalog.types import CatalogItem, CatalogSearchQuery
from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import MissionDataCandidate
from app.main import app, run_migrations

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "stac_ny_harbor_sentinel1.json"
AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}


def _load_fixture() -> Dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _feature_to_stac_item(feature: Dict[str, Any]) -> Any:
    """Minimal duck-typed pystac Item from fixture GeoJSON Feature."""
    assets = {}
    for key, raw in (feature.get("assets") or {}).items():
        assets[key] = SimpleNamespace(
            href=raw.get("href"),
            media_type=raw.get("type"),
            roles=raw.get("roles") or [],
            title=raw.get("title"),
            extra_fields={
                k: v
                for k, v in raw.items()
                if k not in {"href", "type", "roles", "title"}
            },
            to_dict=lambda raw=raw: dict(raw),
        )
    links = [
        SimpleNamespace(rel=link.get("rel"), href=link.get("href"))
        for link in feature.get("links") or []
    ]
    return SimpleNamespace(
        id=feature["id"],
        collection=feature.get("collection"),
        geometry=feature["geometry"],
        properties=feature.get("properties") or {},
        assets=assets,
        links=links,
    )


class FakePlanetaryComputer:
    provider_id = PROVIDER_ID

    def __init__(self, items: List[CatalogItem] | None = None, *, fail: bool = False):
        self._items = items or []
        self.fail = fail
        self.search_calls = 0

    def search(self, query: CatalogSearchQuery) -> List[CatalogItem]:
        self.search_calls += 1
        if self.fail:
            raise CatalogUnavailableError("Planetary Computer STAC timed out.")
        return list(self._items)[: query.limit]

    def get_item(self, collection: str, external_item_id: str) -> CatalogItem:
        for item in self._items:
            if item.collection == collection and item.external_item_id == external_item_id:
                return item
        raise CatalogUnavailableError("not found")

    def get_assets(self, collection: str, external_item_id: str) -> list:
        return self.get_item(collection, external_item_id).assets


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _create_mission(client: TestClient, title: str = "NY Harbor discover") -> str:
    _ensure_session(client)
    created = client.post(
        "/v1/missions",
        json={
            "title": title,
            "objective_type": "ship_detection",
            "area_of_interest": AOI,
            "start_time": "2024-01-01T00:00:00+00:00",
            "end_time": "2024-01-31T23:59:59+00:00",
        },
    )
    assert created.status_code == 201
    return created.json()["mission"]["id"]


def _fixture_catalog_items() -> List[CatalogItem]:
    features = _load_fixture()["features"]
    return [stac_item_to_catalog_item(_feature_to_stac_item(f)) for f in features]


def test_stac_fixture_maps_to_catalog_item():
    items = _fixture_catalog_items()
    assert len(items) == 2
    first = items[0]
    assert first.source_provider == PROVIDER_ID
    assert first.collection == "sentinel-1-grd"
    assert first.external_item_id.startswith("S1A_IW_GRDH")
    assert first.acquisition_time == datetime(2024, 1, 15, 22, 46, 5, tzinfo=timezone.utc)
    assert first.footprint["type"] == "Polygon"
    assert first.source_url and "planetarycomputer.microsoft.com" in first.source_url
    assert first.estimated_size_bytes == 3_000_000_000
    roles = {tuple(a.roles) for a in first.assets}
    assert ("data",) in roles or any("data" in a.roles for a in first.assets)


def test_discover_persists_and_dedupes(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    items = _fixture_catalog_items()
    fake = FakePlanetaryComputer(items)
    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: fake,
    )

    mission_id = _create_mission(client)
    first = client.post(f"/v1/missions/{mission_id}/discover", json={"limit": 20})
    assert first.status_code == 200
    body = first.json()
    assert len(body["candidates"]) == 2
    for candidate in body["candidates"]:
        assert candidate["truth_status"] == "PROVIDER_REPORTED"
        assert candidate["source_provider"] == PROVIDER_ID
        assert candidate["source_url"]
        assert candidate["source_timestamp"]
        assert candidate["footprint"]["type"] == "Polygon"
        assert candidate["available_assets"]
        assert candidate["acquisition_time"]["truth_status"] == "PROVIDER_REPORTED"
        assert candidate["acquisition_time"]["value"]
        assert candidate["estimated_size_bytes"]["truth_status"] == "ESTIMATED"
        assert candidate["estimated_size_bytes"]["value"] > 0

    second = client.post(f"/v1/missions/{mission_id}/discover", json={})
    assert second.status_code == 200
    assert len(second.json()["candidates"]) == 2

    listed = client.get(f"/v1/missions/{mission_id}/candidates")
    assert listed.status_code == 200
    assert len(listed.json()["candidates"]) == 2

    session = SessionLocal(bind=get_engine())
    try:
        count = session.scalar(
            select(func.count())
            .select_from(MissionDataCandidate)
            .where(MissionDataCandidate.mission_id == mission_id)
        )
        assert count == 2
    finally:
        session.close()

    assert fake.search_calls == 2


def test_discover_upstream_failure_no_fake_rows(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    fake = FakePlanetaryComputer(fail=True)
    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: fake,
    )
    mission_id = _create_mission(client, title="fail discover")
    response = client.post(f"/v1/missions/{mission_id}/discover", json={})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"

    listed = client.get(f"/v1/missions/{mission_id}/candidates")
    assert listed.status_code == 200
    assert listed.json()["candidates"] == []


def test_unauthorized_cannot_discover_other_session(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    items = _fixture_catalog_items()
    monkeypatch.setattr(
        "app.catalog.service.default_catalog_provider",
        lambda: FakePlanetaryComputer(items),
    )

    owner = TestClient(app)
    stranger = TestClient(app)
    assert owner.post("/v1/sessions").status_code == 201
    assert stranger.post("/v1/sessions").status_code == 201

    created = owner.post(
        "/v1/missions",
        json={
            "title": "owner only",
            "objective_type": "ship_detection",
            "area_of_interest": AOI,
        },
    )
    mission_id = created.json()["mission"]["id"]

    forbidden = stranger.post(f"/v1/missions/{mission_id}/discover", json={})
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "mission_forbidden"

    owner.close()
    stranger.close()


def test_planetary_computer_search_uses_client(monkeypatch: pytest.MonkeyPatch):
    """Unit: PlanetaryComputerCatalog.search maps Client results."""
    features = _load_fixture()["features"]
    raw_items = [_feature_to_stac_item(f) for f in features]

    class FakeSearch:
        def items(self):
            return iter(raw_items)

    class FakeClient:
        def search(self, **kwargs):
            assert "sentinel-1-grd" in kwargs["collections"]
            assert kwargs.get("max_items") == 10
            return FakeSearch()

    monkeypatch.setattr(
        PlanetaryComputerCatalog,
        "_open_client",
        lambda self: FakeClient(),
    )
    catalog = PlanetaryComputerCatalog(use_cache=False)
    results = catalog.search(
        CatalogSearchQuery(
            collections=["sentinel-1-grd"],
            bbox=(-74.3, 40.3, -73.5, 41.0),
            start=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end=datetime(2024, 1, 31, tzinfo=timezone.utc),
            limit=10,
        )
    )
    assert len(results) == 2
    assert results[0].external_item_id == features[0]["id"]
