import unittest
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from orbitalcortex import APIError, Client


class FakeTransport:
    def __init__(self) -> None:
        self.requests: List[Dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        timeout: float,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "timeout": timeout,
                "json_body": json_body,
            }
        )
        path = urlparse(url).path

        if method == "GET" and path == "/health":
            return {"status": "ok", "service": "orbital-cortex-api"}

        if method == "POST" and path == "/v1/jobs":
            return {
                "job": {
                    "id": "job_test",
                    "job_type": json_body["job_type"],
                    "area_of_interest": json_body["area_of_interest"],
                    "sensor": json_body["sensor"],
                    "priority": json_body["priority"],
                    "compute_preference": json_body["compute_preference"],
                    "max_cost_usd": json_body["max_cost_usd"],
                    "status": "queued",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "selected_route_id": None,
                },
                "routing_decision": None,
            }

        if method == "GET" and path == "/v1/jobs":
            return {"jobs": [_job()]}

        if method == "GET" and path == "/v1/jobs/job_test":
            return {
                "job": _job(),
                "routing_decision": _routing_decision(),
                "result_summary": None,
            }

        if method == "GET" and path == "/v1/jobs/job_test/events":
            return {
                "events": [
                    {
                        "id": "evt_test",
                        "job_id": "job_test",
                        "event_type": "job_created",
                        "message": "Job accepted.",
                        "payload": {},
                        "ts_utc": "2026-01-01T00:00:00Z",
                    }
                ]
            }

        if method == "GET" and path == "/v1/jobs/job_test/result":
            return {
                "result": {
                    "id": "res_test",
                    "job_id": "job_test",
                    "summary": "Detected 17 likely vessels in New York Harbor.",
                    "confidence": 0.91,
                    "geojson": {"type": "FeatureCollection", "features": []},
                    "output_files": [],
                }
            }

        if method == "GET" and path == "/v1/routing/job_test":
            return {"routing_decision": _routing_decision()}

        if method == "POST" and path == "/v1/simulate/run/job_test":
            return {
                "job": {**_job(), "status": "complete"},
                "events_created": 4,
                "result": {
                    "id": "res_test",
                    "job_id": "job_test",
                    "summary": "Detected 17 likely vessels in New York Harbor.",
                    "confidence": 0.91,
                    "geojson": {"type": "FeatureCollection", "features": []},
                    "output_files": [],
                },
            }

        if method == "GET" and path == "/v1/nodes":
            return {
                "compute_nodes": [
                    {
                        "id": "sim_leo_02",
                        "name": "Sim LEO 02",
                        "type": "orbital",
                        "location": "LEO inclination 53.0",
                        "orbit": "LEO",
                        "gpu_class": "Vera Rubin class simulated",
                        "supported_models": ["ship_detection"],
                        "storage_gb": 2048,
                        "downlink_mbps": 450,
                        "power_state": "nominal",
                        "availability": 0.92,
                        "compliance_tags": ["non_defense"],
                        "base_cost_usd": 180,
                        "latency_minutes": 24,
                        "satellite_id": "sat_sentinel_1a",
                    }
                ],
                "ground_stations": [],
            }

        raise APIError(
            f"No fake response for {method} {path}",
            status_code=404,
            code="not_found",
        )


class ClientTest(unittest.TestCase):
    def test_create_job_sends_expected_payload_and_headers(self) -> None:
        transport = FakeTransport()
        client = Client(
            api_key="oc_test_123",
            base_url="http://127.0.0.1:8000/",
            transport=transport,
            timeout=12,
        )

        response = client.jobs.create(
            job_type="ship_detection",
            area_of_interest={
                "type": "bbox",
                "coordinates": [-74.3, 40.3, -73.5, 41.0],
            },
            sensor="SAR",
            priority="fastest",
            compute_preference="orbital_if_available",
            max_cost_usd=500,
        )

        self.assertEqual(response["job"]["id"], "job_test")
        self.assertIsNone(response["routing_decision"])

        request = transport.requests[-1]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["url"], "http://127.0.0.1:8000/v1/jobs")
        self.assertEqual(request["headers"]["Authorization"], "Bearer oc_test_123")
        self.assertEqual(request["headers"]["Content-Type"], "application/json")
        self.assertEqual(request["timeout"], 12)
        self.assertEqual(request["json_body"]["job_type"], "ship_detection")

    def test_control_plane_resources(self) -> None:
        transport = FakeTransport()
        client = Client(transport=transport)

        self.assertEqual(client.health()["status"], "ok")
        self.assertEqual(client.jobs.list()["jobs"][0]["id"], "job_test")
        self.assertEqual(client.jobs.retrieve("job_test")["job"]["id"], "job_test")
        self.assertEqual(client.jobs.events("job_test")["events"][0]["event_type"], "job_created")
        self.assertEqual(client.jobs.routing("job_test")["routing_decision"]["id"], "route_test")
        self.assertEqual(client.routing.retrieve("job_test")["routing_decision"]["id"], "route_test")
        self.assertEqual(client.jobs.run("job_test")["job"]["status"], "complete")
        self.assertEqual(client.jobs.result("job_test")["result"]["confidence"], 0.91)
        self.assertEqual(client.nodes.list()["compute_nodes"][0]["id"], "sim_leo_02")


def _job() -> Dict[str, Any]:
    return {
        "id": "job_test",
        "job_type": "ship_detection",
        "area_of_interest": {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
        "sensor": "SAR",
        "priority": "fastest",
        "compute_preference": "orbital_if_available",
        "max_cost_usd": 500,
        "status": "queued",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "selected_route_id": "route_test",
    }


def _routing_decision() -> Dict[str, Any]:
    return {
        "id": "route_test",
        "job_id": "job_test",
        "selected_node_id": "sim_leo_02",
        "selected_ground_station_id": "svalbard_gs",
        "fallback_node_id": "aws_us_east_gpu",
        "estimated_latency_minutes": 35,
        "estimated_cost_usd": 214,
        "confidence": 0.86,
        "reasons": ["Supports requested job type"],
        "candidate_scores": [
            {
                "node_id": "sim_leo_02",
                "score": 89.4,
                "eligible": True,
                "estimated_latency_minutes": 35,
                "estimated_cost_usd": 214,
                "available": True,
                "reasons": ["Eligible candidate"],
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
