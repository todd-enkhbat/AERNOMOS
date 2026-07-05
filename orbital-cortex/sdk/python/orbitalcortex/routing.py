"""Routing resource methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orbitalcortex.types import RoutingResponse

if TYPE_CHECKING:
    from orbitalcortex.client import Client


class RoutingResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    def retrieve(self, job_id: str) -> RoutingResponse:
        return self._client._request(
            "GET",
            f"/v1/jobs/{job_id}/routing",
        )  # type: ignore[return-value]
