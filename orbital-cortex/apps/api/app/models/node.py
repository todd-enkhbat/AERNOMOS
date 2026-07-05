"""Compute node model definitions."""

from __future__ import annotations

from typing import List, Literal, Optional

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
    compute_nodes: List[ComputeNode]
    ground_stations: List[GroundStation]


class GroundStationsResponse(BaseModel):
    ground_stations: List[GroundStation]


class SatellitesResponse(BaseModel):
    satellites: List[Satellite]


class ContactWindowsResponse(BaseModel):
    contact_windows: List[ContactWindow]
