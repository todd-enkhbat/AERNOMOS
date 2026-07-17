"""Phase L: curated example missions and safe demo reset."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import get_settings
from app.core.missions import (
    CURATED_EXAMPLE_MISSIONS,
    ensure_example_missions,
    example_mission_id,
)
from app.core.storage import create_job, mark_jobs_as_examples
from app.db import SessionLocal, get_engine
from app.db.mission_orm import Mission
from app.db.orm import Job
from app.main import app, run_migrations
from app.seed import reset_demo_data, seed_database


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client


def test_example_missions_seed_four_with_disclosures(client: TestClient):
    examples = client.get("/v1/missions/examples")
    assert examples.status_code == 200
    missions = examples.json()["missions"]
    assert len(missions) >= 4
    assert all(m["is_example"] is True for m in missions)

    titles = {m["title"] for m in missions}
    for spec in CURATED_EXAMPLE_MISSIONS:
        assert spec["title"] in titles

    for mission in missions:
        systems = mission.get("customer_systems") or []
        disclosures = [
            item
            for item in systems
            if isinstance(item, dict) and item.get("kind") == "example_disclosure"
        ]
        # Prefer curated specs; legacy thin examples may lack disclosures.
        if mission["title"] in titles and any(
            mission["title"] == spec["title"] for spec in CURATED_EXAMPLE_MISSIONS
        ):
            assert disclosures, f"missing disclosure on {mission['title']}"
            disclosure = disclosures[0]
            for key in (
                "real_data",
                "real_calculations",
                "estimated_steps",
                "simulated_steps",
                "unavailable_integrations",
            ):
                assert disclosure.get(key), f"{key} missing on {mission['title']}"


def test_ensure_example_missions_is_idempotent():
    session = SessionLocal(bind=get_engine())
    try:
        first = ensure_example_missions(session)
        session.commit()
        second = ensure_example_missions(session)
        session.commit()
        assert first == len(CURATED_EXAMPLE_MISSIONS)
        assert second == len(CURATED_EXAMPLE_MISSIONS)
        stable_ids = {
            example_mission_id(spec["slug"]) for spec in CURATED_EXAMPLE_MISSIONS
        }
        rows = session.scalars(select(Mission).where(Mission.id.in_(stable_ids))).all()
        assert len(rows) == len(CURATED_EXAMPLE_MISSIONS)
        count = session.scalar(
            select(func.count()).select_from(Mission).where(Mission.is_example.is_(True))
        )
        assert count >= len(CURATED_EXAMPLE_MISSIONS)
    finally:
        session.close()


def test_reset_preserves_example_jobs_and_missions():
    session = SessionLocal(bind=get_engine())
    try:
        ensure_example_missions(session)
        visitor = create_job(
            session,
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
        visitor_id = visitor["id"]

        example = create_job(
            session,
            {
                "job_type": "ship_detection",
                "area_of_interest": {
                    "type": "bbox",
                    "coordinates": [-74.3, 40.3, -73.5, 41.0],
                },
                "sensor": "SAR",
                "priority": "fastest",
                "compute_preference": "orbital_if_available",
                "max_cost_usd": 50,
            },
        )
        example_id = example["id"]
        mark_jobs_as_examples(session, [example_id])
        session.commit()

        deleted = reset_demo_data(session)
        assert deleted >= 1
        assert session.get(Job, visitor_id) is None
        assert session.get(Job, example_id) is not None
        assert session.get(Job, example_id).is_example is True

        seed_database(session)
        for spec in CURATED_EXAMPLE_MISSIONS:
            row = session.get(Mission, example_mission_id(spec["slug"]))
            assert row is not None
            assert row.is_example is True
    finally:
        session.close()


def test_examples_excluded_from_private_list(client: TestClient):
    client.post("/v1/sessions")
    private = client.get("/v1/missions")
    assert private.status_code == 200
    assert all(m["is_example"] is False for m in private.json()["missions"])


def test_example_missions_have_recommended_plan(client: TestClient):
    for spec in CURATED_EXAMPLE_MISSIONS:
        mission_id = example_mission_id(spec["slug"])
        response = client.get(f"/v1/missions/{mission_id}/plans")
        assert response.status_code == 200, spec["slug"]
        plans = response.json()["plans"]
        assert plans, f"no plans generated for {spec['slug']}"
        recommended = [p for p in plans if p["recommended"]]
        assert recommended, f"no recommended plan for {spec['slug']}"
        # Recommended existing-imagery path is built on an explicitly SIMULATED
        # reference scene; the truth mix must never masquerade as observed.
        detail = client.get(
            f"/v1/missions/{mission_id}/plans/{recommended[0]['id']}"
        ).json()["plan"]
        step_status = {s["truth_status"] for s in (detail.get("steps") or [])}
        assert "SIMULATED" in step_status, spec["slug"]


def test_example_plans_are_idempotent_across_reseed():
    session = SessionLocal(bind=get_engine())
    try:
        from app.db.mission_orm import MissionPlan

        seed_database(session)
        counts = {
            spec["slug"]: session.scalar(
                select(func.count())
                .select_from(MissionPlan)
                .where(MissionPlan.mission_id == example_mission_id(spec["slug"]))
            )
            for spec in CURATED_EXAMPLE_MISSIONS
        }
        assert all(count and count > 0 for count in counts.values())

        seed_database(session)
        for spec in CURATED_EXAMPLE_MISSIONS:
            after = session.scalar(
                select(func.count())
                .select_from(MissionPlan)
                .where(MissionPlan.mission_id == example_mission_id(spec["slug"]))
            )
            assert after == counts[spec["slug"]], spec["slug"]
    finally:
        session.close()
