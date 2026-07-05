import os

# Deterministic tests: point the queue at an unreachable Redis so job
# creation always falls back to manual (synchronous) execution.
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
# The suite posts more jobs per minute than the production limit allows.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.state import IllegalTransitionError, validate_transition
from app.db import SessionLocal, get_engine
from app.main import app, run_migrations
from app.workers.executor import run_pipeline_sync


def _reset_job_data() -> None:
    """Clear job data from prior test runs; reference data reseeds on boot."""
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

EXPECTED_EVENT_SEQUENCE = [
    "job_created",
    "execution_enqueue_failed",
    "routing_candidates_scored",
    "route_selected",
    "execution_scheduled",
    "contact_window_confirmed",
    "execution_started",
    "inference_completed",
    "downlink_complete",
    "artifacts_uploaded",
    "result_ready",
]


def test_ship_detection_job_routes_and_simulates():
    _reset_job_data()

    with TestClient(app) as client:
        nodes = client.get("/v1/nodes")
        assert nodes.status_code == 200
        assert len(nodes.json()["compute_nodes"]) == 6
        assert len(nodes.json()["ground_stations"]) == 6

        created = client.post("/v1/jobs", json=PAYLOAD)
        assert created.status_code == 201
        created_data = created.json()
        job_id = created_data["job"]["id"]

        assert created_data["job"]["status"] == "queued"
        assert created_data["job"]["schema_version"] == 1
        assert created_data["routing_decision"] is None

        not_ready = client.get(f"/v1/jobs/{job_id}/result")
        assert not_ready.status_code == 404
        assert not_ready.json()["error"]["code"] == "result_not_ready"

        simulated = client.post(f"/v1/simulate/run/{job_id}")
        assert simulated.status_code == 200
        simulated_data = simulated.json()
        assert simulated_data["job"]["status"] == "complete"
        assert simulated_data["events_created"] == 8
        assert simulated_data["result"]["summary"].startswith("Detected 17")
        assert len(simulated_data["result"]["geojson"]["features"]) == 17
        assert simulated_data["result"]["geojson"]["features"][0]["properties"]["harbor_zone"]

        routing = client.get(f"/v1/routing/{job_id}")
        assert routing.status_code == 200
        decision = routing.json()["routing_decision"]
        assert decision["selected_node_id"]
        assert decision["candidate_scores"]

        # B7 DoD: routing references real SGP4 pass times, not a seeded int.
        orbital_with_pass = [
            c for c in decision["candidate_scores"]
            if c["eligible"] and c.get("next_aos_utc")
        ]
        assert orbital_with_pass, "eligible orbital candidates must carry real pass data"
        for candidate in orbital_with_pass:
            assert candidate["next_contact_minutes"] >= 0
            assert candidate["next_max_elevation_deg"] >= 10.0
            assert candidate["est_downlink_mb"] > 0
            assert any("Next pass over gs_" in r for r in candidate["reasons"])

        events = client.get(f"/v1/jobs/{job_id}/events")
        assert events.status_code == 200
        event_list = events.json()["events"]
        assert [event["event_type"] for event in event_list] == EXPECTED_EVENT_SEQUENCE
        assert all("ts_utc" in event and "payload" in event for event in event_list)
        route_event = next(e for e in event_list if e["event_type"] == "route_selected")
        assert route_event["payload"]["status_from"] == "queued"
        assert route_event["payload"]["status_to"] == "routing"
        assert route_event["payload"]["selected_node_id"]

        result = client.get(f"/v1/jobs/{job_id}/result")
        assert result.status_code == 200
        assert result.json()["result"]["confidence"] == 0.91

        detail = client.get(f"/v1/jobs/{job_id}")
        assert detail.status_code == 200
        assert detail.json()["result_summary"].startswith("Detected 17")


def test_worker_pipeline_drives_job_to_complete():
    _reset_job_data()

    with TestClient(app) as client:
        created = client.post("/v1/jobs", json=PAYLOAD)
        assert created.status_code == 201
        job_id = created.json()["job"]["id"]
        assert created.json()["job"]["status"] == "queued"

        # Run the worker's task body directly (no Redis needed).
        outcome = run_pipeline_sync(job_id)
        assert outcome["job"]["status"] == "complete"
        assert outcome["result"]["summary"].startswith("Detected 17")

        # Worker output persisted and is visible through the API.
        detail = client.get(f"/v1/jobs/{job_id}")
        assert detail.json()["job"]["status"] == "complete"
        assert detail.json()["routing_decision"]["selected_node_id"]

        # Re-running the pipeline on a terminal job is a no-op.
        rerun = run_pipeline_sync(job_id)
        assert rerun["events_created"] == 0
        assert rerun["job"]["status"] == "complete"


def test_registry_endpoints_return_real_data():
    _reset_job_data()

    with TestClient(app) as client:
        stations = client.get("/v1/ground-stations")
        assert stations.status_code == 200
        station_list = stations.json()["ground_stations"]
        assert len(station_list) == 6
        providers = {s["provider"] for s in station_list}
        assert {"KSAT", "AWS Ground Station", "Leaf Space"} <= providers
        assert all(s["min_elevation_deg"] == 10.0 for s in station_list)
        svalbard = next(s for s in station_list if s["id"] == "gs_ksat_svalbard")
        assert abs(svalbard["latitude"] - 78.2297) < 0.01

        satellites = client.get("/v1/satellites")
        assert satellites.status_code == 200
        sat_list = satellites.json()["satellites"]
        assert len(sat_list) == 5
        s1a = next(s for s in sat_list if s["norad_id"] == 39634)
        assert s1a["name"] == "SENTINEL-1A"
        assert s1a["tle_line1"].startswith("1 39634U")
        assert s1a["tle_line2"].startswith("2 39634")
        assert s1a["snapshot_id"].startswith("celestrak-")

        windows = client.get(
            "/v1/contact-windows",
            params={"satellite_id": "sat_sentinel_1a", "upcoming": True, "limit": 10},
        )
        assert windows.status_code == 200
        window_list = windows.json()["contact_windows"]
        assert window_list, "precomputed cache must hold upcoming passes"
        for window in window_list:
            assert window["aos_utc"] < window["culminate_utc"] < window["los_utc"]
            assert window["max_elevation_deg"] >= 10.0
            assert window["est_downlink_mb"] > 0


def test_invalid_job_payload_returns_422():
    _reset_job_data()

    invalid_bbox = {
        **PAYLOAD,
        # west >= east makes the bbox invalid
        "area_of_interest": {"type": "bbox", "coordinates": [-73.5, 40.3, -74.3, 41.0]},
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs", json=invalid_bbox)
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "validation_error"
        assert any("west must be less than east" in str(d) for d in error["details"])

        missing_fields = client.post("/v1/jobs", json={"job_type": "ship_detection"})
        assert missing_fields.status_code == 422


def test_state_machine_rejects_illegal_transitions():
    validate_transition("queued", "routing")
    validate_transition("routing", "executing")
    validate_transition("executing", "failed")

    for current, target in [
        ("queued", "complete"),
        ("queued", "executing"),
        ("complete", "queued"),
        ("complete", "failed"),
        ("failed", "queued"),
        ("executing", "routing"),
    ]:
        with pytest.raises(IllegalTransitionError):
            validate_transition(current, target)
