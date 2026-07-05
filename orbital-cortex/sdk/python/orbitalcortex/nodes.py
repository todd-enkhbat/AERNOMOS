"""Node registry resource methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from orbitalcortex.types import (
    ContactWindowsResponse,
    GroundStationsResponse,
    NodesResponse,
    SatellitesResponse,
)

if TYPE_CHECKING:
    from orbitalcortex.client import Client


class NodesResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    def list(self) -> NodesResponse:
        return self._client._request("GET", "/v1/nodes")  # type: ignore[return-value]

    def ground_stations(self) -> GroundStationsResponse:
        return self._client._request(
            "GET", "/v1/ground-stations"
        )  # type: ignore[return-value]

    def satellites(self) -> SatellitesResponse:
        return self._client._request(
            "GET", "/v1/satellites"
        )  # type: ignore[return-value]

    def contact_windows(
        self,
        satellite_id: Optional[str] = None,
        ground_station_id: Optional[str] = None,
        date: Optional[str] = None,
        upcoming: bool = False,
    ) -> ContactWindowsResponse:
        params = []
        if satellite_id:
            params.append(f"satellite_id={satellite_id}")
        if ground_station_id:
            params.append(f"ground_station_id={ground_station_id}")
        if date:
            params.append(f"date={date}")
        if upcoming:
            params.append("upcoming=true")
        query = f"?{'&'.join(params)}" if params else ""
        return self._client._request(
            "GET", f"/v1/contact-windows{query}"
        )  # type: ignore[return-value]
