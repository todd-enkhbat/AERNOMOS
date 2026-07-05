"""Group C/D: routing audit replay, constraints, detections, PostGIS."""

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import SessionLocal, get_engine
from app.main import app, run_migrations
from app.services.scenes import bbox_query_detections
from app.workers.executor import run_pipeline_sync


def _reset_job_data() -> None:
    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        session.execute(text("DELETE FROM jobs"))
        session.commit()
    finally:
        session.close()


PAYLOAD = {
    "job_type": "ship_detection",
    "area_of_interest": {
        "type": "bbox",
        "coordinates": [-74.3, 40.3, -73.5, 41.0],
    },
    "sensor": "SAR",
    "priority": "fastest",
    "compute_preference": "orbital_if_available",
    "max_cost_usd": 500,
}


def test_routing_replay_is_byte_identical():
    _reset_job_data()

    with TestClient(app) as client:
        created = client.post("/v1/jobs", json=PAYLOAD)
        assert created.status_code == 201
        job_id = created.json()["job"]["id"]

        simulated = client.post(f"/v1/simulate/run/{job_id}")
        assert simulated.status_code == 200

        routing = client.get(f"/v1/jobs/{job_id}/routing")
        assert routing.status_code == 200
        decision = routing.json()["routing_decision"]
        assert decision["decision_hash"]
        assert decision["input_hash"]
        assert decision["config_version"]

        replay = client.post(f"/v1/jobs/{job_id}/replay")
        assert replay.status_code == 200
        replay_data = replay.json()
        assert replay_data["match"] is True
        assert replay_data["stored_decision_hash"] == replay_data["replay_decision_hash"]


def test_budget_hard_constraint_excludes_nodes():
    _reset_job_data()

    from app.core import node_registry, storage
    from app.core.storage import utc_now
    from app.routing.scorer import _build_raw_candidate, _score_candidates
    from app.services.contact_windows import next_window_for_satellite

    with TestClient(app) as client:
        created = client.post(
            "/v1/jobs",
            json={**PAYLOAD, "max_cost_usd": 1},
        )
        assert created.status_code == 201
        job_id = created.json()["job"]["id"]

        session = SessionLocal(bind=get_engine())
        try:
            job = storage.get_job(session, job_id)
            compute_nodes = node_registry.list_compute_nodes(session)
            ground_stations = node_registry.list_ground_stations(session)
            stations_by_id = {station["id"]: station for station in ground_stations}
            now = utc_now()
            next_windows = {}
            for node in compute_nodes:
                satellite_id = node.get("satellite_id")
                if satellite_id and satellite_id not in next_windows:
                    window = next_window_for_satellite(session, satellite_id, now)
                    if window is not None:
                        next_windows[satellite_id] = window
            raw_candidates = [
                _build_raw_candidate(
                    job,
                    node,
                    next_windows.get(node.get("satellite_id") or ""),
                    stations_by_id,
                    now,
                )
                for node in compute_nodes
            ]
            candidates = _score_candidates(job, raw_candidates)
        finally:
            session.close()
        budget_failures = [
            c
            for c in candidates
            if any(f["constraint"] == "budget_exceeded" for f in c["hard_constraint_failures"])
        ]
        assert budget_failures, "tight budget should trigger budget_exceeded failures"
        assert not any(c["eligible"] for c in candidates)


def test_detections_geojson_and_postgis_bbox():
    _reset_job_data()

    with TestClient(app) as client:
        created = client.post("/v1/jobs", json=PAYLOAD)
        job_id = created.json()["job"]["id"]
        run_pipeline_sync(job_id)

        detections = client.get(f"/v1/jobs/{job_id}/detections")
        assert detections.status_code == 200
        assert detections.headers["content-type"].startswith("application/geo+json")
        geojson = detections.json()
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 17
        first = geojson["features"][0]
        assert first["geometry"]["type"] == "Point"
        assert "dark_ship" in first["properties"]

        scene = client.get(f"/v1/jobs/{job_id}/scene")
        assert scene.status_code == 200
        assert scene.json()["scene"]["sensor"] == "Sentinel-1"
        assert scene.json()["scene"]["stac_item_id"]

        session = SessionLocal(bind=get_engine())
        try:
            ids = bbox_query_detections(
                session,
                job_id,
                west=-74.05,
                south=40.68,
                east=-74.04,
                north=40.70,
            )
        finally:
            session.close()
        assert ids, "bbox query should return detections in upper bay"
