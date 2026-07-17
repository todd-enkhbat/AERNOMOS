"""Phase M: lightweight real CPU execution (crop_geotiff + thumbnail).

Every assertion here runs against real files and real measured durations —
Redis is unreachable in the test env, so submit() falls back to executing the
task synchronously in-process (the same runner the ARQ worker calls).
"""

from __future__ import annotations

import io
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pytest
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

from app.core.config import API_DIR, get_settings
from app.db import SessionLocal, get_engine
from app.db.mission_orm import ExecutionJob, MissionDataCandidate, MissionPlanStep
from app.db.truth import TruthStatus
from app.main import app, run_migrations

FIXTURE_DIR = API_DIR / "var" / "test_execution_fixtures"
os.environ["EXECUTION_FIXTURE_DIR"] = str(FIXTURE_DIR)

AOI = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}
COVERING_WKT = (
    "POLYGON((-74.2 40.4, -73.6 40.4, -73.6 40.9, -74.2 40.9, -74.2 40.4))"
)
CROP_BOUNDS = [-74.1, 40.5, -73.7, 40.8]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


@pytest.fixture(scope="module", autouse=True)
def geotiff_fixtures() -> Dict[str, Path]:
    """Write a real georeferenced GeoTIFF (and a corrupt file) to the
    allowlisted fixture dir."""
    import rasterio
    from rasterio.transform import from_bounds

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    sample = FIXTURE_DIR / "sample.tif"
    width = height = 96
    transform = from_bounds(-74.3, 40.3, -73.5, 41.0, width, height)
    data = (
        np.linspace(0, 255, width * height).reshape(height, width).astype("uint8")
    )
    with rasterio.open(
        sample,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    corrupt = FIXTURE_DIR / "corrupt.tif"
    corrupt.write_bytes(b"this is not a geotiff at all" * 10)
    return {"sample": sample, "corrupt": corrupt}


@pytest.fixture()
def client():
    get_settings.cache_clear()
    run_migrations()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def _create_mission_with_plan(client: TestClient) -> Dict[str, Any]:
    """Create a mission + covering catalog candidate, generate plans, return
    the imagery-cloud plan and its executable cloud_process step."""
    assert client.post("/v1/sessions").status_code in (200, 201)
    created = client.post(
        "/v1/missions",
        json={
            "title": "Execution mission",
            "objective_type": "analyze_imagery",
            "area_of_interest": AOI,
            "data_source_preference": ["sentinel-1-grd"],
            "start_time": "2024-01-01T00:00:00+00:00",
            "end_time": "2024-01-31T23:59:59+00:00",
        },
    )
    assert created.status_code == 201, created.text
    mission_id = created.json()["mission"]["id"]

    db = SessionLocal(bind=get_engine())
    try:
        db.add(
            MissionDataCandidate(
                id=uuid.uuid4(),
                mission_id=uuid.UUID(mission_id),
                source_provider="microsoft-planetary-computer",
                collection="sentinel-1-grd",
                external_item_id=f"S1A_EXEC_{uuid.uuid4().hex[:8]}",
                acquisition_time=_utcnow() - timedelta(days=3),
                footprint=WKTElement(COVERING_WKT, srid=4326),
                asset_metadata={},
                estimated_size_bytes=50_000_000,
                source_url="https://example.test/stac/item",
                source_timestamp=_utcnow(),
                truth_status=TruthStatus.PROVIDER_REPORTED,
            )
        )
        db.commit()
    finally:
        db.close()

    generated = client.post(f"/v1/missions/{mission_id}/plans")
    assert generated.status_code == 201, generated.text
    plans = generated.json()["plans"]
    cloud_plan = next(
        p
        for p in plans
        if any(
            isinstance(a, dict)
            and a.get("kind") == "planner_meta"
            and a.get("pattern") == "existing_imagery_cloud"
            for a in (p.get("assumptions") or [])
        )
    )
    step = next(
        s for s in cloud_plan["steps"] if s["step_type"] == "cloud_process"
    )
    assert step["feasibility_status"] == "feasible", cloud_plan
    assert step["execution_status"] == "planned"
    return {"mission_id": mission_id, "plan": cloud_plan, "step": step}


def _execute(
    client: TestClient,
    ctx: Dict[str, Any],
    *,
    task_type: str = "crop_geotiff",
    input_ref: str = "fixture:sample.tif",
    params: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
):
    body: Dict[str, Any] = {
        "step_id": ctx["step"]["id"],
        "task_type": task_type,
        "input_ref": input_ref,
        "params": params if params is not None else {"bounds": CROP_BOUNDS},
    }
    if idempotency_key:
        body["idempotency_key"] = idempotency_key
    return client.post(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}/execute",
        json=body,
    )


def _get_status(client: TestClient, ctx: Dict[str, Any], external_job_id: str):
    return client.get(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}"
        f"/execute/{external_job_id}"
    )


def _artifact_path(key: str) -> Path:
    return Path(get_settings().artifact_dir) / key


def test_crop_geotiff_end_to_end_observed_metrics(client: TestClient):
    ctx = _create_mission_with_plan(client)

    submitted = _execute(client, ctx)
    assert submitted.status_code == 201, submitted.text
    payload = submitted.json()
    job = payload["job"]
    assert payload["provider_id"] == "local-cpu"
    assert payload["estimate"]["estimated_cost_usd"] == 0.0
    # Redis is unreachable in tests, so the real task already ran synchronously.
    assert job["status"] == "succeeded"

    status = _get_status(client, ctx, job["external_job_id"])
    assert status.status_code == 200, status.text
    body = status.json()
    assert body["job"]["status"] == "succeeded"
    assert body["job"]["error"] is None
    assert body["observed_truth_status"] == "OBSERVED"
    assert body["download_url"]

    result = body["result"]
    assert result["external_job_id"] == job["external_job_id"]
    assert result["output_ref"].startswith("artifact:missions/")

    observed = result["observed"]
    assert observed["transfer_seconds"] > 0
    assert observed["execution_seconds"] > 0
    assert observed["input_bytes"] == (FIXTURE_DIR / "sample.tif").stat().st_size
    assert observed["output_bytes"] > 0
    assert observed["storage_location"].startswith(("local:", "s3://"))

    # The artifact really exists on disk with nonzero size.
    key = result["output_ref"].removeprefix("artifact:")
    artifact = _artifact_path(key)
    assert artifact.is_file(), f"missing artifact at {artifact}"
    assert artifact.stat().st_size == observed["output_bytes"]

    # The cropped output is a real, smaller GeoTIFF.
    import rasterio

    with rasterio.open(artifact) as cropped:
        assert cropped.width < 96 and cropped.height < 96
        assert cropped.width > 0 and cropped.height > 0

    # Plan step flipped planned -> executed in the DB (queried directly).
    db = SessionLocal(bind=get_engine())
    try:
        step = db.get(MissionPlanStep, uuid.UUID(ctx["step"]["id"]))
        assert step is not None
        assert step.execution_status == "executed"
        assert step.executed_at is not None
        execution_meta = (step.source_metadata or {}).get("execution")
        assert execution_meta["truth_status"] == "OBSERVED"
        assert execution_meta["observed"]["execution_seconds"] > 0
        assert execution_meta["external_job_id"] == job["external_job_id"]
    finally:
        db.close()

    # Plan detail API reflects the executed step.
    detail = client.get(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}"
    )
    assert detail.status_code == 200
    api_step = next(
        s for s in detail.json()["plan"]["steps"] if s["id"] == ctx["step"]["id"]
    )
    assert api_step["execution_status"] == "executed"
    assert api_step["executed_at"]


def test_idempotent_submit_enqueues_exactly_once(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    ctx = _create_mission_with_plan(client)

    enqueue_calls: list[str] = []

    def _record_enqueue(external_job_id: str) -> bool:
        enqueue_calls.append(external_job_id)
        return True  # pretend Redis accepted it so nothing runs synchronously

    monkeypatch.setattr(
        "app.execution.provider.enqueue_execution_job", _record_enqueue
    )

    # Unique per test run: the Postgres test DB persists between pytest
    # invocations and idempotency keys are globally unique by design.
    key = f"phase-m-idempotency-{uuid.uuid4().hex}"
    first = _execute(client, ctx, idempotency_key=key)
    second = _execute(client, ctx, idempotency_key=key)
    assert first.status_code == 201 and second.status_code == 201
    first_job = first.json()["job"]
    second_job = second.json()["job"]

    assert first_job["external_job_id"] == second_job["external_job_id"]
    assert first_job["idempotency_key"] == key
    assert len(enqueue_calls) == 1, "same idempotency_key must enqueue exactly once"

    db = SessionLocal(bind=get_engine())
    try:
        rows = (
            db.query(ExecutionJob)
            .filter(ExecutionJob.idempotency_key == key)
            .all()
        )
        assert len(rows) == 1
        assert rows[0].status == "queued"
    finally:
        db.close()


def test_failure_corrupt_input_no_partial_artifact(client: TestClient):
    ctx = _create_mission_with_plan(client)

    submitted = _execute(client, ctx, input_ref="fixture:corrupt.tif")
    assert submitted.status_code == 201, submitted.text
    job = submitted.json()["job"]
    assert job["status"] == "failed"

    status = _get_status(client, ctx, job["external_job_id"])
    body = status.json()
    assert body["job"]["status"] == "failed"
    assert body["job"]["error"], "failed jobs must carry a human-readable error"
    assert body["result"] is None
    assert body["download_url"] is None

    # No orphaned artifact directory for the failed job.
    job_dir = _artifact_path(
        f"missions/{ctx['mission_id']}/execution/{job['external_job_id']}"
    )
    assert not job_dir.exists(), f"orphaned artifact left behind at {job_dir}"

    db = SessionLocal(bind=get_engine())
    try:
        row = db.get(ExecutionJob, uuid.UUID(job["external_job_id"]))
        assert row is not None
        assert row.status == "failed"
        assert row.output_key is None
        step = db.get(MissionPlanStep, uuid.UUID(ctx["step"]["id"]))
        assert step is not None and step.execution_status == "failed"
        assert (step.source_metadata or {}).get("execution", {}).get("error")
    finally:
        db.close()


def test_oversized_input_rejected_before_processing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    ctx = _create_mission_with_plan(client)
    monkeypatch.setenv("EXECUTION_MAX_INPUT_BYTES", "16")
    get_settings.cache_clear()
    try:
        submitted = _execute(client, ctx)
        assert submitted.status_code == 201
        job = submitted.json()["job"]
        assert job["status"] == "failed"

        body = _get_status(client, ctx, job["external_job_id"]).json()
        assert body["job"]["status"] == "failed"
        assert "exceeds" in body["job"]["error"]
        job_dir = _artifact_path(
            f"missions/{ctx['mission_id']}/execution/{job['external_job_id']}"
        )
        assert not job_dir.exists()
    finally:
        get_settings.cache_clear()


def test_chained_crop_then_thumbnail(client: TestClient):
    ctx = _create_mission_with_plan(client)

    crop = _execute(client, ctx).json()["job"]
    assert crop["status"] == "succeeded"
    crop_result = _get_status(client, ctx, crop["external_job_id"]).json()["result"]
    crop_output_ref = crop_result["output_ref"]

    thumb = _execute(
        client,
        ctx,
        task_type="thumbnail",
        input_ref=crop_output_ref,
        params={"max_size": 64},
    )
    assert thumb.status_code == 201, thumb.text
    thumb_job = thumb.json()["job"]
    assert thumb_job["status"] == "succeeded"

    body = _get_status(client, ctx, thumb_job["external_job_id"]).json()
    observed = body["result"]["observed"]
    assert observed["input_bytes"] == crop_result["observed"]["output_bytes"]
    assert observed["output_bytes"] > 0
    assert observed["execution_seconds"] > 0

    # Both artifacts exist; the thumbnail is a real, openable PNG.
    crop_path = _artifact_path(crop_output_ref.removeprefix("artifact:"))
    thumb_path = _artifact_path(
        body["result"]["output_ref"].removeprefix("artifact:")
    )
    assert crop_path.is_file() and crop_path.stat().st_size > 0
    assert thumb_path.is_file() and thumb_path.stat().st_size > 0

    from PIL import Image

    with Image.open(io.BytesIO(thumb_path.read_bytes())) as image:
        assert image.format == "PNG"
        assert max(image.size) <= 64
        image.load()


def test_input_ref_allowlist_rejections(client: TestClient):
    ctx = _create_mission_with_plan(client)

    for bad_ref in (
        "https://example.com/evil.tif",
        "/etc/passwd",
        "fixture:../../etc/passwd",
        "fixture:missing-file.tif",
        f"artifact:missions/{uuid.uuid4()}/execution/x/crop.tif",  # other mission
    ):
        denied = _execute(client, ctx, input_ref=bad_ref)
        assert denied.status_code == 422, f"{bad_ref} → {denied.status_code}"
        assert denied.json()["error"]["code"] == "execution_invalid"

    # No jobs were created for rejected refs beyond validation.
    denied_bad_task = _execute(client, ctx, task_type="gpu_inference")
    assert denied_bad_task.status_code == 422


def test_non_executable_step_rejected(client: TestClient):
    ctx = _create_mission_with_plan(client)
    select_step = next(
        s
        for s in ctx["plan"]["steps"]
        if s["step_type"] == "select_catalog_scene"
    )
    denied = client.post(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}/execute",
        json={
            "step_id": select_step["id"],
            "task_type": "crop_geotiff",
            "input_ref": "fixture:sample.tif",
            "params": {"bounds": CROP_BOUNDS},
        },
    )
    assert denied.status_code == 422
    assert denied.json()["error"]["code"] == "step_not_executable"


def test_ensure_execution_fixtures_writes_sample_tif(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_FIXTURE_DIR", str(tmp_path))
    get_settings.cache_clear()
    from app.execution.fixtures import ensure_execution_fixtures, sample_fixture_path

    path = ensure_execution_fixtures()
    assert path == sample_fixture_path()
    assert path.is_file()
    assert path.stat().st_size > 0
    # Idempotent second call.
    assert ensure_execution_fixtures() == path
    get_settings.cache_clear()


def test_execute_owner_only(client: TestClient):
    ctx = _create_mission_with_plan(client)

    stranger = TestClient(app)
    denied = stranger.post(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}/execute",
        json={
            "step_id": ctx["step"]["id"],
            "task_type": "crop_geotiff",
            "input_ref": "fixture:sample.tif",
            "params": {"bounds": CROP_BOUNDS},
        },
    )
    assert denied.status_code == 401
    stranger.close()

    other = TestClient(app)
    assert other.post("/v1/sessions").status_code == 201
    forbidden = other.post(
        f"/v1/missions/{ctx['mission_id']}/plans/{ctx['plan']['id']}/execute",
        json={
            "step_id": ctx["step"]["id"],
            "task_type": "crop_geotiff",
            "input_ref": "fixture:sample.tif",
            "params": {"bounds": CROP_BOUNDS},
        },
    )
    assert forbidden.status_code == 403
    other.close()
