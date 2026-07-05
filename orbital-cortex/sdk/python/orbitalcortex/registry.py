"""Ground-station, satellite, and contact-window registry methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlencode

from orbitalcortex.types import (
    ContactWindowsResponse,
    GroundStationsResponse,
    SatellitesResponse,
)

if TYPE_CHECKING:
    from orbitalcortex.client import Client


class RegistryResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    def ground_stations(self) -> GroundStationsResponse:
        return self._client._request("GET", "/v1/ground-stations")  # type: ignore[return-value]

    def satellites(self) -> SatellitesResponse:
        return self._client._request("GET", "/v1/satellites")  # type: ignore[return-value]

    def contact_windows(
        self,
        *,
        satellite_id: Optional[str] = None,
        ground_station_id: Optional[str] = None,
        date: Optional[str] = None,
        upcoming: bool = False,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ContactWindowsResponse:
        params: Dict[str, Any] = {}
        if satellite_id is not None:
            params["satellite_id"] = satellite_id
        if ground_station_id is not None:
            params["ground_station_id"] = ground_station_id
        if date is not None:
            params["date"] = date
        if upcoming:
            params["upcoming"] = "true"
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        path = "/v1/contact-windows"
        if params:
            path = f"{path}?{urlencode(params)}"
        return self._client._request("GET", path)  # type: ignore[return-value]
