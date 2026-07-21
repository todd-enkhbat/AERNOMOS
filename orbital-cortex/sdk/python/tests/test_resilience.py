"""Retry, timeout, typed-parsing, and wait_for_job behavior (Group E tests)."""

from __future__ import annotations

import asyncio
import unittest
from typing import Any, Dict, List, Optional
from unittest import mock

from orbitalcortex import APIError, Client, JobTimeoutError, TransportError
from orbitalcortex.transport import UrllibTransport, _decode_json


def _job(status: str) -> Dict[str, Any]:
    return {
        "id": "job_test",
        "job_type": "ship_detection",
        "area_of_interest": {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
        "sensor": "SAR",
        "priority": "fastest",
        "compute_preference": "orbital_if_available",
        "max_cost_usd": 500,
        "status": status,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "selected_route_id": None,
    }


class ScriptedTransport:
    """Returns or raises each scripted outcome in order; repeats the last."""

    def __init__(self, outcomes: List[Any]) -> None:
        self.outcomes = list(outcomes)
        self.calls: List[Dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        timeout: float,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.calls.append({"method": method, "url": url})
        outcome = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _client(transport: ScriptedTransport, **kwargs: Any) -> Client:
    kwargs.setdefault("max_retries", 2)
    kwargs.setdefault("retry_backoff_s", 0.001)
    return Client(transport=transport, **kwargs)


class RetryTest(unittest.TestCase):
    def test_get_retries_on_5xx_then_succeeds(self) -> None:
        transport = ScriptedTransport(
            [
                APIError("boom", status_code=500, code="internal"),
                APIError("boom", status_code=503, code="unavailable"),
                {"jobs": [], "next_cursor": None},
            ]
        )
        response = _client(transport).jobs.list()
        self.assertEqual(response["jobs"], [])
        self.assertEqual(len(transport.calls), 3)

    def test_get_retries_on_transport_error(self) -> None:
        transport = ScriptedTransport(
            [TransportError("connection refused"), {"jobs": [], "next_cursor": None}]
        )
        response = _client(transport).jobs.list()
        self.assertEqual(response["jobs"], [])
        self.assertEqual(len(transport.calls), 2)

    def test_get_gives_up_after_max_retries(self) -> None:
        transport = ScriptedTransport(
            [APIError("boom", status_code=500, code="internal")]
        )
        with self.assertRaises(APIError) as ctx:
            _client(transport).jobs.list()
        self.assertEqual(ctx.exception.status_code, 500)
        # 1 initial + 2 retries
        self.assertEqual(len(transport.calls), 3)

    def test_get_does_not_retry_on_4xx(self) -> None:
        transport = ScriptedTransport(
            [APIError("not found", status_code=404, code="job_not_found")]
        )
        with self.assertRaises(APIError):
            _client(transport).jobs.retrieve("job_missing")
        self.assertEqual(len(transport.calls), 1)

    def test_post_never_retries_on_5xx(self) -> None:
        transport = ScriptedTransport(
            [APIError("boom", status_code=500, code="internal")]
        )
        with self.assertRaises(APIError):
            _client(transport).jobs.replay("job_test")
        self.assertEqual(len(transport.calls), 1)


class TimeoutTest(unittest.TestCase):
    def test_socket_timeout_maps_to_transport_error(self) -> None:
        # The transport routes requests through a cookie-aware opener so the
        # private session cookie persists; a socket timeout must still surface
        # as a TransportError.
        transport = UrllibTransport()
        with mock.patch.object(transport._opener, "open", side_effect=TimeoutError()):
            with self.assertRaises(TransportError) as ctx:
                transport.request(
                    "GET",
                    "http://127.0.0.1:8000/healthz",
                    headers={},
                    timeout=0.01,
                )
        self.assertIn("Timed out", str(ctx.exception))

    def test_timeout_is_passed_to_opener(self) -> None:
        transport = UrllibTransport()
        with mock.patch.object(transport._opener, "open") as open_mock:
            open_mock.return_value.__enter__.return_value.read.return_value = b"{}"
            client = Client(transport=transport, timeout=7.5)
            client.health()
        _, kwargs = open_mock.call_args
        self.assertEqual(kwargs["timeout"], 7.5)


class TypedParsingTest(unittest.TestCase):
    def test_non_object_payload_raises_transport_error(self) -> None:
        with self.assertRaises(TransportError):
            _decode_json(b"[1, 2, 3]")

    def test_invalid_json_raises_transport_error(self) -> None:
        with self.assertRaises(TransportError):
            _decode_json(b"not json at all")

    def test_api_error_carries_typed_fields(self) -> None:
        transport = ScriptedTransport(
            [
                APIError(
                    "No job exists for id job_x.",
                    status_code=404,
                    code="job_not_found",
                    response={"error": {"code": "job_not_found"}},
                )
            ]
        )
        with self.assertRaises(APIError) as ctx:
            _client(transport).jobs.retrieve("job_x")
        self.assertEqual(ctx.exception.code, "job_not_found")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(
            ctx.exception.response["error"]["code"], "job_not_found"
        )


class WaitForJobTest(unittest.TestCase):
    def test_wait_reaches_terminal_state(self) -> None:
        transport = ScriptedTransport(
            [
                {"job": _job("queued"), "routing_decision": None, "result_summary": None},
                {"job": _job("executing"), "routing_decision": None, "result_summary": None},
                {"job": _job("complete"), "routing_decision": None, "result_summary": "ok"},
            ]
        )
        detail = _client(transport).wait_for_job(
            "job_test", timeout=5.0, poll_interval=0.001
        )
        self.assertEqual(detail["job"]["status"], "complete")
        self.assertEqual(len(transport.calls), 3)

    def test_wait_reaches_failed_state(self) -> None:
        transport = ScriptedTransport(
            [
                {"job": _job("executing"), "routing_decision": None, "result_summary": None},
                {"job": _job("failed"), "routing_decision": None, "result_summary": None},
            ]
        )
        detail = _client(transport).jobs.wait(
            "job_test", timeout=5.0, poll_interval=0.001
        )
        self.assertEqual(detail["job"]["status"], "failed")

    def test_wait_times_out(self) -> None:
        transport = ScriptedTransport(
            [{"job": _job("executing"), "routing_decision": None, "result_summary": None}]
        )
        with self.assertRaises(JobTimeoutError) as ctx:
            _client(transport).wait_for_job(
                "job_test", timeout=0.05, poll_interval=0.01
            )
        self.assertEqual(ctx.exception.job_id, "job_test")
        self.assertEqual(ctx.exception.last_status, "executing")


class AsyncClientTest(unittest.TestCase):
    def test_async_wait_for_job_and_retry(self) -> None:
        import httpx

        from orbitalcortex import AsyncClient

        statuses = iter(["queued", "executing", "complete"])
        attempts = {"health": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/healthz":
                attempts["health"] += 1
                if attempts["health"] < 2:
                    return httpx.Response(
                        503,
                        json={"error": {"code": "unavailable", "message": "warming"}},
                    )
                return httpx.Response(200, json={"status": "ok"})
            return httpx.Response(
                200,
                json={
                    "job": _job(next(statuses)),
                    "routing_decision": None,
                    "result_summary": None,
                },
            )

        async def scenario() -> None:
            async with AsyncClient(
                http_transport=httpx.MockTransport(handler),
                max_retries=2,
                retry_backoff_s=0.001,
            ) as client:
                health = await client.health()
                assert health["status"] == "ok"
                assert attempts["health"] == 2  # first 503 was retried
                detail = await client.wait_for_job(
                    "job_test", timeout=5.0, poll_interval=0.001
                )
                assert detail["job"]["status"] == "complete"

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
