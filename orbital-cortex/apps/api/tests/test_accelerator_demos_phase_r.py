"""Phase R: accelerator-ready curated demos — reliability suite.

Proves the demos survive cold reset, back-to-back runs, offline (fixture)
catalog mode, and that every SIMULATED / simulated step is visible in the
API payload.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")
os.environ["CATALOG_MODE"] = "fixture"

from app.catalog.fixture_provider import FixtureCatalogProvider, load_fixture_file
from app.catalog.types import CatalogSearchQuery
from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.db.migrate import run_migrations
from app.demos.accelerator import (
    ACCELERATOR_DEMOS,
    reset_accelerator_demo,
    run_demo_cpu_execution,
)
from app.seed import seed_database


@pytest.fixture(scope="module")
def _migrations() -> None:
    get_settings.cache_clear()
    run_migrations()


@pytest.fixture()
def db(_migrations: None):
    session = SessionLocal(bind=get_engine())
    try:
        seed_database(session)
        yield session
    finally:
        session.close()


def _assert_demo_success(summary: Dict[str, Any], *, demo_number: int) -> None:
    assert summary["demo_number"] == demo_number
    assert summary["catalog_mode"] == "fixture"
    assert summary["candidate_count"] >= 1
    assert summary["plan_count"] >= 3
    # At least one candidate is real pinned STAC (PROVIDER_REPORTED).
    assert all(c["truth_status"] == "PROVIDER_REPORTED" for c in summary["candidates"])
    assert summary["candidates"][0]["external_item_id"]
    assert not summary["candidates"][0]["external_item_id"].startswith("example-scene-")
    # Demos 1 and 3 must have a feasible executable process step.
    if demo_number in (1, 3):
        assert summary["executable_step"] is not None, summary["plans"]
        assert summary["recommended_feasibility"] == "feasible"
    # Demo 2 must surface a comparison across feasibility states.
    if demo_number == 2:
        statuses = {p["feasibility_status"] for p in summary["plans"]}
        assert "feasible" in statuses or "conditional" in statuses
        assert "rejected" in statuses


def test_cold_reset_demo_1(db) -> None:
    summary = reset_accelerator_demo(db, 1, live=False)
    db.commit()
    _assert_demo_success(summary, demo_number=1)
    print(
        "COLD DEMO 1 OK ->",
        summary["mission_id"],
        "candidates",
        summary["candidate_count"],
        "item",
        summary["candidates"][0]["external_item_id"],
        "feas",
        summary["recommended_feasibility"],
    )


def test_cold_reset_demo_2(db) -> None:
    summary = reset_accelerator_demo(db, 2, live=False)
    db.commit()
    _assert_demo_success(summary, demo_number=2)
    print(
        "COLD DEMO 2 OK ->",
        summary["mission_id"],
        "plans",
        [(p["pattern"], p["feasibility_status"]) for p in summary["plans"]],
    )


def test_cold_reset_demo_3_with_cpu_execution(db) -> None:
    summary = reset_accelerator_demo(db, 3, live=False)
    db.commit()
    _assert_demo_success(summary, demo_number=3)
    execution = run_demo_cpu_execution(db, demo_number=3)
    db.commit()
    assert execution["status"]["status"] == "succeeded"
    assert execution["observed_truth_status"] == "OBSERVED"
    metrics = execution["observed_metrics"] or {}
    assert float(metrics.get("execution_seconds") or 0) > 0
    assert int(metrics.get("output_bytes") or 0) > 0
    print(
        "COLD DEMO 3 OK -> CPU OBSERVED",
        metrics.get("execution_seconds"),
        "s,",
        metrics.get("output_bytes"),
        "bytes out",
    )


def test_back_to_back_demo_1(db) -> None:
    first = reset_accelerator_demo(db, 1, live=False)
    db.commit()
    _assert_demo_success(first, demo_number=1)
    second = reset_accelerator_demo(db, 1, live=False)
    db.commit()
    _assert_demo_success(second, demo_number=1)
    # Structural identity: same mission id, same real item ids, both feasible.
    assert first["mission_id"] == second["mission_id"]
    assert {c["external_item_id"] for c in first["candidates"]} == {
        c["external_item_id"] for c in second["candidates"]
    }
    assert first["recommended_feasibility"] == second["recommended_feasibility"]
    print(
        "BACK-TO-BACK DEMO 1 OK ->",
        first["mission_id"],
        "run1 candidates",
        first["candidate_count"],
        "run2 candidates",
        second["candidate_count"],
    )


def test_back_to_back_demo_3_cpu(db) -> None:
    first = reset_accelerator_demo(db, 3, live=False)
    db.commit()
    exec1 = run_demo_cpu_execution(db, demo_number=3)
    db.commit()
    second = reset_accelerator_demo(db, 3, live=False)
    db.commit()
    exec2 = run_demo_cpu_execution(db, demo_number=3)
    db.commit()
    assert exec1["status"]["status"] == "succeeded"
    assert exec2["status"]["status"] == "succeeded"
    assert exec1["observed_truth_status"] == "OBSERVED"
    assert exec2["observed_truth_status"] == "OBSERVED"
    assert float((exec1["observed_metrics"] or {}).get("execution_seconds") or 0) > 0
    assert float((exec2["observed_metrics"] or {}).get("execution_seconds") or 0) > 0
    # Distinct job ids — no silent idempotent replay leaking state.
    assert exec1["job"]["external_job_id"] != exec2["job"]["external_job_id"]
    print(
        "BACK-TO-BACK DEMO 3 OK -> jobs",
        exec1["job"]["external_job_id"],
        "then",
        exec2["job"]["external_job_id"],
        "OBSERVED",
        (exec1["observed_metrics"] or {}).get("execution_seconds"),
        "s /",
        (exec2["observed_metrics"] or {}).get("execution_seconds"),
        "s",
    )


def test_offline_all_three_demos_on_fixtures(db, monkeypatch) -> None:
    """Confirm demos complete with live STAC unreachable.

    Accelerator demos use pinned fixtures by default (live=False). We also
    monkeypatch PlanetaryComputerCatalog.search so any accidental live call
    would fail hard — proving the isolation claim is real.
    """

    def _blocked(self: Any, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("network blocked for offline demo test")

    monkeypatch.setattr(
        "app.catalog.planetary_computer.PlanetaryComputerCatalog.search",
        _blocked,
    )
    monkeypatch.setenv("CATALOG_MODE", "fixture")
    get_settings.cache_clear()

    results = []
    for number in (1, 2, 3):
        summary = reset_accelerator_demo(db, number, live=False)
        db.commit()
        _assert_demo_success(summary, demo_number=number)
        results.append(
            (
                number,
                summary["candidate_count"],
                summary["recommended_feasibility"],
                summary["catalog_mode"],
            )
        )
    print("OFFLINE ALL DEMOS OK ->", results)


def test_disclosure_simulated_steps_visible_in_payload(db) -> None:
    for number in (1, 2, 3):
        summary = reset_accelerator_demo(db, number, live=False)
        db.commit()
        visible = summary["simulated_steps_visible"]
        assert visible, f"Demo {number} has no visible simulated steps"
        for step in visible:
            assert (
                step["truth_status"] == "SIMULATED"
                or step["integration_status"] == "simulated"
            )
            assert step["title"]
        print(
            f"DISCLOSURE DEMO {number} ->",
            [
                {
                    "title": s["title"],
                    "truth_status": s["truth_status"],
                    "integration_status": s["integration_status"],
                }
                for s in visible[:3]
            ],
        )


def test_fixture_provider_serves_pinned_real_items() -> None:
    from pathlib import Path

    from app.catalog.fixture_provider import FIXTURES_DIR

    provider = FixtureCatalogProvider()
    items = provider.search(
        CatalogSearchQuery(
            collections=["sentinel-1-grd"],
            bbox=(-74.3, 40.3, -73.5, 41.0),
            limit=5,
        )
    )
    assert items
    assert items[0].external_item_id.startswith("S1A_")
    assert items[0].properties.get("nomos_fixture", {}).get("pinned") is True

    _, meta = load_fixture_file(FIXTURES_DIR / str(ACCELERATOR_DEMOS[1]["fixture"]))
    assert meta.get("source") == "microsoft-planetary-computer"
    assert meta.get("captured_at")
    _ = Path  # silence unused if any