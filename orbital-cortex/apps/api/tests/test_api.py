import os

os.environ.setdefault("ORBITAL_CORTEX_DB_PATH", "/tmp/orbital-cortex-test.sqlite3")

from fastapi.testclient import TestClient

from app.main import app


def test_ship_detection_job_routes_and_simulates(tmp_path, monkeypatch):
    monkeypatch.setenv("ORBITAL_CORTEX_DB_PATH", str(tmp_path / "api.sqlite3"))

    payload = {
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

    with TestClient(app) as client:
        nodes = client.get("/v1/nodes")
        assert nodes.status_code == 200
        assert len(nodes.json()["compute_nodes"]) == 6
        assert len(nodes.json()["ground_stations"]) == 4

        created = client.post("/v1/jobs", json=payload)
        assert created.status_code == 201
        created_data = created.json()
        job_id = created_data["job"]["id"]

        assert created_data["job"]["status"] == "queued"
        assert created_data["routing_decision"]["selected_node_id"] == "sim_leo_02"
        assert created_data["routing_decision"]["candidate_scores"]

        not_ready = client.get(f"/v1/jobs/{job_id}/result")
        assert not_ready.status_code == 404
        assert not_ready.json()["error"]["code"] == "result_not_ready"

        simulated = client.post(f"/v1/simulate/run/{job_id}")
        assert simulated.status_code == 200
        simulated_data = simulated.json()
        assert simulated_data["job"]["status"] == "completed"
        assert simulated_data["events_created"] == 6
        assert simulated_data["result"]["summary"].startswith("Detected 17")
        assert len(simulated_data["result"]["geojson"]["features"]) == 17
        assert simulated_data["result"]["geojson"]["features"][0]["properties"]["harbor_zone"]

        events = client.get(f"/v1/jobs/{job_id}/events")
        assert events.status_code == 200
        assert [event["event_type"] for event in events.json()["events"]] == [
            "job_created",
            "routing_candidates_scored",
            "route_selected",
            "execution_scheduled",
            "contact_window_confirmed",
            "execution_started",
            "inference_completed",
            "downlink_complete",
            "result_ready",
        ]

        result = client.get(f"/v1/jobs/{job_id}/result")
        assert result.status_code == 200
        assert result.json()["result"]["confidence"] == 0.91

        detail = client.get(f"/v1/jobs/{job_id}")
        assert detail.status_code == 200
        assert detail.json()["result_summary"].startswith("Detected 17")
