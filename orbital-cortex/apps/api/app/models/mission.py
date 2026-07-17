"""Pydantic models for anonymous sessions, missions, and share links."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.mission_geo import validate_area_of_interest


class ObjectiveType(str, Enum):
    """Customer-facing mission objectives (stable API string values)."""

    analyze_imagery = "analyze_imagery"
    plan_data_delivery = "plan_data_delivery"
    compare_processing = "compare_processing"
    remote_sensing_workflow = "remote_sensing_workflow"
    other = "other"


# Legacy demo / seed values still accepted for existing rows and tests.
LEGACY_OBJECTIVE_TYPES = frozenset(
    {"ship_detection", "crop_health", "disaster_response"}
)

OBJECTIVE_TYPE_VALUES = frozenset(item.value for item in ObjectiveType) | LEGACY_OBJECTIVE_TYPES

MISSION_CREATE_STATUS_VALUES = frozenset({"draft", "exploratory", "active"})

ONBOARD_PROCESSING_VALUES = frozenset({"required", "preferred", "unnecessary"})


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
    max_cost_usd: Optional[float] = Field(default=None, ge=0)
    max_data_volume_mb: Optional[float] = Field(default=None, ge=0)
    preferred_compute_location: Optional[str] = Field(default=None, max_length=64)
    allowed_regions: List[Any] = Field(default_factory=list)
    data_source_preference: List[Any] = Field(default_factory=list)
    customer_systems: List[Any] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None, max_length=8_000)
    # Optional builder fields packed into customer_systems / notes on create.
    organization_name: Optional[str] = Field(default=None, max_length=256)
    use_case: Optional[str] = Field(default=None, max_length=2_000)
    max_age_days: Optional[int] = Field(default=None, ge=1, le=3650)
    onboard_processing: Optional[str] = None
    data_residency: Optional[str] = Field(default=None, max_length=256)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title is required")
        return cleaned

    @field_validator("objective_type")
    @classmethod
    def objective_type_allowed(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned not in OBJECTIVE_TYPE_VALUES:
            allowed = ", ".join(sorted(OBJECTIVE_TYPE_VALUES))
            raise ValueError(f"objective_type must be one of: {allowed}")
        return cleaned

    @field_validator("status")
    @classmethod
    def status_allowed(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned not in MISSION_CREATE_STATUS_VALUES:
            allowed = ", ".join(sorted(MISSION_CREATE_STATUS_VALUES))
            raise ValueError(f"status must be one of: {allowed}")
        return cleaned

    @field_validator("area_of_interest")
    @classmethod
    def area_must_be_valid(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        return validate_area_of_interest(value)

    @field_validator("onboard_processing")
    @classmethod
    def onboard_processing_allowed(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        cleaned = value.strip()
        if cleaned not in ONBOARD_PROCESSING_VALUES:
            allowed = ", ".join(sorted(ONBOARD_PROCESSING_VALUES))
            raise ValueError(f"onboard_processing must be one of: {allowed}")
        return cleaned

    @field_validator("preferred_compute_location")
    @classmethod
    def blank_compute_to_none(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def time_range_order(self) -> MissionCreate:
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("start_time must be before or equal to end_time")
        return self


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
