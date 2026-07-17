"""Compute node model definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


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
    access_level: str = "public_information"
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


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
    retrieved_at: Optional[str] = None


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
    tle_snapshot_id: str = ""
    truth_status: str = "CALCULATED"
    calculation_method: str = "SGP4/Skyfield.find_events"


class NodesResponse(BaseModel):
    compute_nodes: List[ComputeNode]
    ground_stations: List[GroundStation]


class GroundStationsResponse(BaseModel):
    ground_stations: List[GroundStation]


class SatellitesResponse(BaseModel):
    satellites: List[Satellite]


class ContactWindowsResponse(BaseModel):
    contact_windows: List[ContactWindow]
    # Opaque keyset cursor; None when there are no further pages.
    next_cursor: Optional[str] = None
