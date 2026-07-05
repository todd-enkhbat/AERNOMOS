"""Job resource methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlencode

from orbitalcortex.types import (
    AreaOfInterest,
    ComputePreference,
    JobCreateResponse,
    JobDetailResponse,
    JobEventsResponse,
    JobType,
    JobsListResponse,
    Priority,
    ReplayResponse,
    ResultResponse,
    RoutingResponse,
    SceneResponse,
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

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> JobsListResponse:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        path = "/v1/jobs"
        if params:
            path = f"{path}?{urlencode(params)}"
        return self._client._request("GET", path)  # type: ignore[return-value]

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
            f"/v1/jobs/{job_id}/routing",
        )  # type: ignore[return-value]

    def replay(self, job_id: str) -> ReplayResponse:
        return self._client._request(
            "POST",
            f"/v1/jobs/{job_id}/replay",
        )  # type: ignore[return-value]

    def detections(self, job_id: str) -> Dict[str, Any]:
        """GeoJSON FeatureCollection of detections for the job."""
        return self._client._request(
            "GET",
            f"/v1/jobs/{job_id}/detections",
        )

    def scene(self, job_id: str) -> SceneResponse:
        return self._client._request(
            "GET",
            f"/v1/jobs/{job_id}/scene",
        )  # type: ignore[return-value]

    def wait(
        self,
        job_id: str,
        *,
        timeout: float = 120.0,
        poll_interval: float = 1.0,
    ) -> JobDetailResponse:
        return self._client.wait_for_job(
            job_id, timeout=timeout, poll_interval=poll_interval
        )  # type: ignore[return-value]

    def run(self, job_id: str) -> SimulateRunResponse:
        return self._client._request(
            "POST",
            f"/v1/simulate/run/{job_id}",
        )  # type: ignore[return-value]
