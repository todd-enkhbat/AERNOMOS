"""Pydantic models for anonymous sessions, missions, and share links."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnonymousSessionOut(BaseModel):
    id: str
    created_at: str
    last_seen_at: str
    expires_at: str
    converted_user_id: Optional[str] = None


class SessionResponse(BaseModel):
    session: AnonymousSessionOut
    created: bool = False


class MissionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    objective_type: str = Field(min_length=1, max_length=64)
    area_of_interest: Dict[str, Any]
    status: str = Field(default="draft", max_length=32)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    deadline: Optional[str] = None
    max_cost_usd: Optional[float] = None
    max_data_volume_mb: Optional[float] = None
    preferred_compute_location: Optional[str] = None
    allowed_regions: List[Any] = Field(default_factory=list)
    data_source_preference: List[Any] = Field(default_factory=list)
    customer_systems: List[Any] = Field(default_factory=list)
    notes: Optional[str] = None


class MissionOut(BaseModel):
    id: str
    anonymous_session_id: Optional[str] = None
    organization_id: Optional[str] = None
    title: str
    objective_type: str
    status: str
    area_of_interest: Dict[str, Any]
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    deadline: Optional[str] = None
    max_cost_usd: Optional[float] = None
    max_data_volume_mb: Optional[float] = None
    preferred_compute_location: Optional[str] = None
    allowed_regions: List[Any] = Field(default_factory=list)
    data_source_preference: List[Any] = Field(default_factory=list)
    customer_systems: List[Any] = Field(default_factory=list)
    notes: Optional[str] = None
    is_example: bool = False
    created_at: str
    updated_at: str


class MissionResponse(BaseModel):
    mission: MissionOut


class MissionsListResponse(BaseModel):
    missions: List[MissionOut]


class ShareLinkCreate(BaseModel):
    expires_at: Optional[str] = None
    permissions: List[str] = Field(default_factory=lambda: ["read"])


class ShareLinkOut(BaseModel):
    id: str
    mission_id: str
    created_at: str
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    permissions: List[Any] = Field(default_factory=list)
    token: Optional[str] = None


class ShareLinkResponse(BaseModel):
    share_link: ShareLinkOut


class DiscoverRequest(BaseModel):
    """Optional overrides for mission catalog discovery."""

    start_time: Optional[str] = None
    end_time: Optional[str] = None
    collections: Optional[List[str]] = None
    limit: Optional[int] = Field(default=None, ge=1, le=50)


class CatalogCandidateAssetOut(BaseModel):
    key: Optional[str] = None
    media_type: Optional[str] = None
    roles: List[Any] = Field(default_factory=list)
    title: Optional[str] = None


class CatalogCandidateOut(BaseModel):
    id: str
    mission_id: str
    source_provider: str
    collection: str
    external_item_id: str
    acquisition_time: str
    footprint: Dict[str, Any]
    asset_metadata: Dict[str, Any] = Field(default_factory=dict)
    available_assets: List[CatalogCandidateAssetOut] = Field(default_factory=list)
    estimated_size_bytes: Optional[int] = None
    source_url: Optional[str] = None
    source_timestamp: str
    truth_status: str
    created_at: str


class CatalogCandidatesResponse(BaseModel):
    candidates: List[CatalogCandidateOut]


class OrbitalSnapshotOut(BaseModel):
    snapshot_id: str
    source: str
    source_url: Optional[str] = None
    epochs: List[Any] = Field(default_factory=list)
    truth_status: str
    retrieved_at: Optional[str] = None
    stale_epoch_days: int = 7
    used_pinned_fallback: bool = False


class MissionSatelliteOut(BaseModel):
    id: str
    name: str
    norad_id: int
    tle_epoch: str
    snapshot_id: str
    source: str
    retrieved_at: Optional[str] = None
    downlink_rate_mbps: float
    resource_type: str = "satellite"
    access_level: str = "public_information"
    truth_status: str


class MissionGroundStationOut(BaseModel):
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
    availability: float
    resource_type: str = "ground_station"
    access_level: str = "public_information"
    source_metadata: Dict[str, Any] = Field(default_factory=dict)
    coordinate_truth_status: str = "PROVIDER_REPORTED"
    ops_params_truth_status: str = "SIMULATED"
    truth_status: str = "PROVIDER_REPORTED"


class MissionInfrastructureResponse(BaseModel):
    mission_id: str
    orbital_snapshot: OrbitalSnapshotOut
    satellites: List[MissionSatelliteOut] = Field(default_factory=list)
    ground_stations: List[MissionGroundStationOut] = Field(default_factory=list)
