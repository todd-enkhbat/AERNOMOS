"""Compute node model definitions."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.config import JsonDict

# Canonical registry rows (real seed data) for the OpenAPI examples.
EXAMPLE_GROUND_STATION: JsonDict = {
    "id": "gs_ksat_svalbard",
    "name": "KSAT Svalbard",
    "location": "Svalbard, Norway",
    "provider": "KSAT",
    "latitude": 78.23,
    "longitude": 15.39,
    "altitude_m": 458.0,
    "min_elevation_deg": 10.0,
    "latency_minutes": 8.0,
    "downlink_mbps": 600,
    "availability": 0.98,
}

EXAMPLE_SATELLITE: JsonDict = {
    "id": "sat_sentinel_1a",
    "name": "SENTINEL-1A",
    "norad_id": 39634,
    "tle_line1": (
        "1 39634U 14016A   26186.51782528  .00000714  00000+0  19052-3 0  9995"
    ),
    "tle_line2": (
        "2 39634  98.1813 187.6273 0001341  81.4767 278.6588 14.59198614652873"
    ),
    "tle_epoch": "2026-07-05T12:25:40+00:00",
    "source": "celestrak",
    "snapshot_id": "celestrak-2026-07-05",
    "downlink_rate_mbps": 520.0,
}

EXAMPLE_CONTACT_WINDOW: JsonDict = {
    "id": "cw_7a1b3c5d9e2f",
    "satellite_id": "sat_sentinel_1a",
    "ground_station_id": "gs_ksat_svalbard",
    "date": "2026-07-05",
    "aos_utc": "2026-07-05T14:27:30+00:00",
    "culminate_utc": "2026-07-05T14:32:10+00:00",
    "los_utc": "2026-07-05T14:36:45+00:00",
    "max_elevation_deg": 63.4,
    "duration_s": 555.0,
    "est_downlink_mb": 42.0,
}

EXAMPLE_COMPUTE_NODE: JsonDict = {
    "id": "sim_leo_01",
    "name": "Simulated LEO SAR node 01",
    "type": "orbital",
    "location": "LEO / sun-synchronous",
    "orbit": "SSO ~700 km",
    "gpu_class": "edge-tpu-class",
    "supported_models": ["ship_detection"],
    "storage_gb": 512,
    "downlink_mbps": 400,
    "power_state": "nominal",
    "availability": 0.97,
    "compliance_tags": ["civilian", "commercial"],
    "base_cost_usd": 60.0,
    "latency_minutes": 30.0,
    "satellite_id": "sat_sentinel_1a",
}


class ComputeNode(BaseModel):
    id: str
    name: str
    type: Literal["orbital", "ground_cloud", "ground_station"]
    location: str
    orbit: Optional[str] = None
    gpu_class: str
    supported_models: List[str]
    storage_gb: int
    downlink_mbps: int
    power_state: str
    availability: float = Field(ge=0, le=1)
    compliance_tags: List[str]
    base_cost_usd: float
    latency_minutes: float
    satellite_id: Optional[str] = None


class GroundStation(BaseModel):
    id: str
    name: str
    location: str
    provider: str = ""
    latitude: float
    longitude: float
    altitude_m: float = 0
    min_elevation_deg: float = 10.0
    latency_minutes: float
    downlink_mbps: int
    availability: float = Field(ge=0, le=1)


class Satellite(BaseModel):
    id: str
    name: str
    norad_id: int
    tle_line1: str
    tle_line2: str
    tle_epoch: str
    source: str
    snapshot_id: str
    downlink_rate_mbps: float


class ContactWindow(BaseModel):
    id: str
    satellite_id: str
    ground_station_id: str
    date: str
    aos_utc: str
    culminate_utc: str
    los_utc: str
    max_elevation_deg: float
    duration_s: float
    est_downlink_mb: float


class NodesResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "compute_nodes": [EXAMPLE_COMPUTE_NODE],
                "ground_stations": [EXAMPLE_GROUND_STATION],
            }
        }
    )

    compute_nodes: List[ComputeNode]
    ground_stations: List[GroundStation]


class GroundStationsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"ground_stations": [EXAMPLE_GROUND_STATION]}
        }
    )

    ground_stations: List[GroundStation]


class SatellitesResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"satellites": [EXAMPLE_SATELLITE]}}
    )

    satellites: List[Satellite]


class ContactWindowsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact_windows": [EXAMPLE_CONTACT_WINDOW],
                "next_cursor": (
                    "MjAyNi0wNy0wNVQxNDoyNzozMCswMDowMHxjd183YTFiM2M1ZDllMmY="
                ),
            }
        }
    )

    contact_windows: List[ContactWindow]
    # Opaque keyset cursor; None when there are no further pages.
    next_cursor: Optional[str] = None
