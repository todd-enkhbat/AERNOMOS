"""Phase N: infrastructure provider registry ingest + planner integration."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.infrastructure_types import PROVIDER_REGISTRY_KIND, IntegrationStatus
from app.db.mission_orm import InfrastructureResource, MissionDataCandidate
from app.db.session import REPO_ROOT
from app.db.truth import AccessLevel, TruthStatus
from app.main import app, run_migrations
from app.seed import seed_database
from app.services.provider_registry import (
    CONNECTED_STATUSES,
    count_registry_rows,
    ingest_providers_from_config,
    load_registry_for_planner,
)

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}
COVERING_WKT = (
    "POLYGON((-74.2 40.4, -73.6 40.4, -73.6 40.9, -74.2 40.9, -74.2 40.4))"
)
PROVIDERS_DIR = REPO_ROOT / "config" / "providers"


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def _ingest_seed_providers() -> None:
    session = SessionLocal(bind=get_engine())
    try:
        ingest_providers_from_config(session, config_dir=PROVIDERS_DIR)
        session.commit()
    finally:
        session.close()


def _registry_row(session, provider_name: str) -> InfrastructureResource | None:
    return session.scalars(
        select(InfrastructureResource).where(
            InfrastructureResource.provider_name == provider_name,
            InfrastructureResource.source_metadata["kind"].astext
            == PROVIDER_REGISTRY_KIND,
        )
    ).one_or_none()


def test_ingest_seed_providers_unibap_and_ubotica():
    _ingest_seed_providers()
    session = SessionLocal(bind=get_engine())
    try:
        unibap = _registry_row(session, "Unibap AB")
        ubotica = _registry_row(session, "Ubotica Technologies")
        assert unibap is not None
        assert ubotica is not None
        assert (
            unibap.source_metadata.get("integration_status") == "public_data_only"
        )
        assert (
            ubotica.source_metadata.get("integration_status") == "public_data_only"
        )
        assert unibap.source_metadata.get("source_url") == "https://unibap.com/solutions/"
        assert (
            ubotica.source_metadata.get("source_url")
            == "https://ubotica.com/ubotica-cognisat-xe2/"
        )
    finally:
        session.close()


def test_seed_database_automatically_ingests_provider_registry():
    session = SessionLocal(bind=get_engine())
    try:
        result = seed_database(session)
        assert result["infrastructure_providers"] == 6
        assert count_registry_rows(session) == 6
    finally:
        session.close()


def test_ingest_is_idempotent():
    _ingest_seed_providers()
    session = SessionLocal(bind=get_engine())
    try:
        before = count_registry_rows(session)
        ingest_providers_from_config(session, config_dir=PROVIDERS_DIR)
        session.flush()
        after = count_registry_rows(session)
        assert before == after
        assert before >= 6
    finally:
        session.close()


def test_requested_or_documented_access_is_not_connected():
    _ingest_seed_providers()
    session = SessionLocal(bind=get_engine())
    try:
        kp_labs = _registry_row(session, "KP Labs")
        assert kp_labs is not None
        assert kp_labs.access_level == AccessLevel.PUBLIC_INFORMATION.value
        assert IntegrationStatus.DOCUMENTED_API not in CONNECTED_STATUSES
        registry = load_registry_for_planner(session)
        kp_planner = next(
            row for row in registry["edge"] if row["provider_name"] == "KP Labs"
        )
        assert kp_planner["is_public_info_only"] is True
        assert kp_planner["is_connected"] is False
    finally:
        session.close()


def test_ingest_rejects_missing_source_url(tmp_path: Path):
    bad = tmp_path / "bad-provider.yaml"
    bad.write_text(
        yaml.dump(
            {
                "provider_name": "Bad Provider",
                "resource_type": "edge",
                "external_id": "bad",
                "api_available": False,
                "sandbox_available": False,
                "auth_required": False,
                "supported_task_types": [],
                "supported_data_formats": [],
                "geography": None,
                "pricing_source": None,
                "capacity_source": None,
                "current_status": "unknown",
                "data_freshness": "2026-07-17",
                "contact_info": None,
                "integration_status": "public_data_only",
                "truth_status": "PUBLIC_SOURCE",
                "source_url": None,
                "notes": "Missing required source URL.",
            }
        ),
        encoding="utf-8",
    )
    session = SessionLocal(bind=get_engine())
    try:
        with pytest.raises(ValueError, match="source_url is required"):
            ingest_providers_from_config(session, config_dir=tmp_path)
    finally:
        session.close()


def _ensure_session(client: TestClient) -> None:
    response = client.post("/v1/sessions")
    assert response.status_code in (200, 201)


def _create_mission(client: TestClient, *, extra: Dict[str, Any] | None = None) -> str:
    _ensure_session(client)
    payload: Dict[str, Any] = {
        "title": "Registry planner mission",
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


def _add_candidate(mission_id: str) -> None:
    session = SessionLocal(bind=get_engine())
    try:
        row = MissionDataCandidate(
            id=uuid.uuid4(),
            mission_id=uuid.UUID(mission_id),
            source_provider="microsoft-planetary-computer",
            collection="sentinel-1-grd",
            external_item_id="S1A_REGISTRY_TEST",
            acquisition_time=datetime.now(timezone.utc) - timedelta(days=3),
            footprint=WKTElement(COVERING_WKT, srid=4326),
            asset_metadata={},
            estimated_size_bytes=50_000_000,
            source_url="https://example.test/stac/item",
            source_timestamp=datetime.now(timezone.utc),
            truth_status=TruthStatus.PROVIDER_REPORTED,
        )
        session.add(row)
        session.commit()
    finally:
        session.close()


def test_planner_reads_registry_and_distinguishes_integration_status(client: TestClient):
    _ingest_seed_providers()
    mission_id = _create_mission(client)
    _add_candidate(mission_id)

    generated = client.post(f"/v1/missions/{mission_id}/plans")
    assert generated.status_code == 201, generated.text
    plans = generated.json()["plans"]
    by_pattern = {plan["pattern"]: plan for plan in plans}

    cloud_plan = by_pattern["existing_imagery_cloud"]
    edge_plan = by_pattern["existing_imagery_edge"]

    cloud_step = next(
        s for s in cloud_plan["steps"] if s["step_type"] == "cloud_process"
    )
    edge_step = next(
        s for s in edge_plan["steps"] if s["step_type"] == "edge_process"
    )

    assert cloud_step["provider_name"] == "Nomos simulated cloud"
    assert cloud_step["source_metadata"]["integration_status"] == "simulated"
    assert cloud_step["source_metadata"]["is_simulated"] is True
    assert cloud_step["truth_status"] == "SIMULATED"

    assert edge_step["provider_name"] == "KP Labs"
    assert edge_step["source_metadata"]["integration_status"] == "sandbox_requested"
    assert edge_step["source_metadata"]["is_simulated"] is False
    assert edge_step["source_metadata"]["is_public_info_only"] is True
    assert edge_step["source_metadata"]["is_connected"] is False
    assert edge_step["source_metadata"]["source_url"]
    assert "integration readiness" in (
        edge_step["source_metadata"]["provider_selection_reason"]
    )

    session = SessionLocal(bind=get_engine())
    try:
        registry = load_registry_for_planner(session)
        assert len(registry["edge"]) >= 5
        assert any(item["is_simulated"] for item in registry["cloud"])
        assert all(not item["is_simulated"] for item in registry["edge"])
    finally:
        session.close()

    detail = client.get(
        f"/v1/missions/{mission_id}/plans/{cloud_plan['id']}?include_steps=true"
    )
    assert detail.status_code == 200
    detail_cloud = next(
        s
        for s in detail.json()["plan"]["steps"]
        if s["step_type"] == "cloud_process"
    )
    assert detail_cloud["source_metadata"]["integration_status"] == "simulated"


def test_planner_honors_preferred_registry_provider(client: TestClient):
    _ingest_seed_providers()
    mission_id = _create_mission(
        client,
        extra={"preferred_compute_location": "Ubotica Technologies"},
    )
    _add_candidate(mission_id)

    generated = client.post(f"/v1/missions/{mission_id}/plans")
    assert generated.status_code == 201, generated.text
    edge_plan = next(
        plan
        for plan in generated.json()["plans"]
        if plan["pattern"] == "existing_imagery_edge"
    )
    edge_step = next(
        step for step in edge_plan["steps"] if step["step_type"] == "edge_process"
    )
    assert edge_step["provider_name"] == "Ubotica Technologies"
    assert "preferred_compute_location" in (
        edge_step["source_metadata"]["provider_selection_reason"]
    )
