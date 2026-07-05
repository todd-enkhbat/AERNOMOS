"""Job model definitions (versioned job spec, Pydantic v2)."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.result import Result
from app.models.routing import RoutingDecision


JobType = Literal["ship_detection", "crop_health", "disaster_response"]
Sensor = Literal["SAR", "optical", "hyperspectral", "any"]
Priority = Literal["fastest", "cheapest", "most_reliable"]
ComputePreference = Literal[
    "orbital_if_available",
    "ground_only",
    "cheapest",
    "fastest",
]
JobStatus = Literal[
    "queued",
    "routing",
    "executing",
    "downlinking",
    "complete",
    "failed",
]

CURRENT_JOB_SCHEMA_VERSION = 1


class AreaOfInterest(BaseModel):
    type: Literal["bbox"]
    coordinates: List[float] = Field(min_length=4, max_length=4)

    @field_validator("coordinates")
    @classmethod
    def validate_bbox(cls, value: List[float]) -> List[float]:
        west, south, east, north = value
        if not (-180 <= west <= 180 and -180 <= east <= 180):
            raise ValueError("longitudes must be within [-180, 180]")
        if not (-90 <= south <= 90 and -90 <= north <= 90):
            raise ValueError("latitudes must be within [-90, 90]")
        if west >= east:
            raise ValueError("bbox west must be less than east")
        if south >= north:
            raise ValueError("bbox south must be less than north")
        return value


class JobCreate(BaseModel):
    schema_version: Literal[1] = CURRENT_JOB_SCHEMA_VERSION
    job_type: JobType
    area_of_interest: AreaOfInterest
    sensor: Sensor
    priority: Priority
    compute_preference: ComputePreference
    max_cost_usd: float = Field(gt=0)


class Job(BaseModel):
    id: str
    schema_version: int = CURRENT_JOB_SCHEMA_VERSION
    job_type: JobType
    area_of_interest: AreaOfInterest
    sensor: Sensor
    priority: Priority
    compute_preference: ComputePreference
    max_cost_usd: float
    status: JobStatus
    created_at: str
    updated_at: str
    selected_route_id: Optional[str] = None


class JobCreateResponse(BaseModel):
    job: Job
    # None until the async worker routes the job.
    routing_decision: Optional[RoutingDecision] = None


class JobsListResponse(BaseModel):
    jobs: List[Job]


class JobDetailResponse(BaseModel):
    job: Job
    routing_decision: Optional[RoutingDecision] = None
    result_summary: Optional[str] = None


class SimulateRunResponse(BaseModel):
    job: Job
    events_created: int
    result: Optional[Result] = None
