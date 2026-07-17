"""Versioned allowlisted analytics event schemas.

Each event type has exactly one payload model listing every field that may be
logged. Payload models use ``extra='forbid'`` so any unknown key fails loudly
in dev/CI instead of silently leaking new mission fields.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Type
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventName(str, Enum):
    MISSION_STARTED = "mission_started"
    MISSION_COMPLETED = "mission_completed"
    PLAN_GENERATED = "plan_generated"
    DATA_CANDIDATES_FOUND = "data_candidates_found"
    PLAN_EXPORTED = "plan_exported"
    PLAN_SHARED = "plan_shared"
    EXAMPLE_VIEWED = "example_viewed"
    USER_RETURNED = "user_returned"
    PROVIDER_CONNECTION_REQUESTED = "provider_connection_requested"
    PLANNING_FAILURE = "planning_failure_reason"


class PlanningFailureReason(str, Enum):
    NO_CANDIDATES_FOUND = "no_candidates_found"
    PROVIDER_TIMEOUT = "provider_timeout"
    INVALID_AOI = "invalid_aoi"
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    UNKNOWN = "unknown"


class _AllowlistedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MissionStartedPayload(_AllowlistedPayload):
    mission_id: UUID
    session_id_hash: str
    resource_types_requested: list[str]
    timestamp: datetime


class MissionCompletedPayload(_AllowlistedPayload):
    mission_id: UUID
    plan_id: UUID
    session_id_hash: str
    timestamp: datetime


class PlanGeneratedPayload(_AllowlistedPayload):
    mission_id: UUID
    plan_id: UUID
    step_count: int
    candidate_count: int
    generation_seconds: float
    timestamp: datetime


class DataCandidatesFoundPayload(_AllowlistedPayload):
    mission_id: UUID
    candidate_count: int
    provider_id: str
    search_duration_seconds: float
    timestamp: datetime


class PlanExportedPayload(_AllowlistedPayload):
    mission_id: UUID
    export_type: str = Field(description="json or pdf")
    success: bool
    timestamp: datetime


class PlanSharedPayload(_AllowlistedPayload):
    mission_id: UUID
    share_link_id: UUID
    session_id_hash: str
    timestamp: datetime


class ExampleViewedPayload(_AllowlistedPayload):
    mission_id: UUID
    timestamp: datetime


class UserReturnedPayload(_AllowlistedPayload):
    session_id_hash: str
    days_since_last_seen: float
    timestamp: datetime


class ProviderConnectionRequestedPayload(_AllowlistedPayload):
    mission_id: UUID
    provider_name: str
    integration_status: str
    timestamp: datetime


class PlanningFailurePayload(_AllowlistedPayload):
    mission_id: UUID
    reason: PlanningFailureReason
    timestamp: datetime


PAYLOAD_BY_EVENT: dict[EventName, Type[_AllowlistedPayload]] = {
    EventName.MISSION_STARTED: MissionStartedPayload,
    EventName.MISSION_COMPLETED: MissionCompletedPayload,
    EventName.PLAN_GENERATED: PlanGeneratedPayload,
    EventName.DATA_CANDIDATES_FOUND: DataCandidatesFoundPayload,
    EventName.PLAN_EXPORTED: PlanExportedPayload,
    EventName.PLAN_SHARED: PlanSharedPayload,
    EventName.EXAMPLE_VIEWED: ExampleViewedPayload,
    EventName.USER_RETURNED: UserReturnedPayload,
    EventName.PROVIDER_CONNECTION_REQUESTED: ProviderConnectionRequestedPayload,
    EventName.PLANNING_FAILURE: PlanningFailurePayload,
}


def all_payload_models() -> dict[EventName, Type[_AllowlistedPayload]]:
    return dict(PAYLOAD_BY_EVENT)
