"""Job resource methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orbitalcortex.types import (
    AreaOfInterest,
    ComputePreference,
    JobCreateResponse,
    JobDetailResponse,
    JobEventsResponse,
    JobType,
    JobsListResponse,
    Priority,
    ResultResponse,
    RoutingResponse,
    Sensor,
    SimulateRunResponse,
)

if TYPE_CHECKING:
    from orbitalcortex.client import Client


class JobsResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        *,
        job_type: JobType,
        area_of_interest: AreaOfInterest,
        sensor: Sensor,
        priority: Priority,
        compute_preference: ComputePreference,
        max_cost_usd: float,
    ) -> JobCreateResponse:
        return self._client._request(
            "POST",
            "/v1/jobs",
            json_body={
                "job_type": job_type,
                "area_of_interest": area_of_interest,
                "sensor": sensor,
                "priority": priority,
                "compute_preference": compute_preference,
                "max_cost_usd": max_cost_usd,
            },
        )  # type: ignore[return-value]

    def list(self) -> JobsListResponse:
        return self._client._request("GET", "/v1/jobs")  # type: ignore[return-value]

    def retrieve(self, job_id: str) -> JobDetailResponse:
        return self._client._request("GET", f"/v1/jobs/{job_id}")  # type: ignore[return-value]

    def events(self, job_id: str) -> JobEventsResponse:
        return self._client._request(
            "GET",
            f"/v1/jobs/{job_id}/events",
        )  # type: ignore[return-value]

    def result(self, job_id: str) -> ResultResponse:
        return self._client._request(
            "GET",
            f"/v1/jobs/{job_id}/result",
        )  # type: ignore[return-value]

    def routing(self, job_id: str) -> RoutingResponse:
        return self._client._request(
            "GET",
            f"/v1/routing/{job_id}",
        )  # type: ignore[return-value]

    def run(self, job_id: str) -> SimulateRunResponse:
        return self._client._request(
            "POST",
            f"/v1/simulate/run/{job_id}",
        )  # type: ignore[return-value]
