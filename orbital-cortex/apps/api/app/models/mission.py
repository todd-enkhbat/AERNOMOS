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
