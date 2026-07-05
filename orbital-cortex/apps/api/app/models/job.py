"""Job model definitions (versioned job spec, Pydantic v2)."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.config import JsonDict

from app.models.result import EXAMPLE_RESULT, Result
from app.models.routing import EXAMPLE_DECISION, RoutingDecision

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

CURRENT_JOB_SCHEMA_VERSION: Literal[1] = 1

# Canonical NY Harbor demo job, reused by the OpenAPI response examples.
EXAMPLE_JOB: JsonDict = {
    "id": "job_9f2c41d3a8b7",
    "schema_version": 1,
    "job_type": "ship_detection",
    "area_of_interest": {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
    "sensor": "SAR",
    "priority": "fastest",
    "compute_preference": "orbital_if_available",
    "max_cost_usd": 500.0,
    "status": "complete",
    "created_at": "2026-07-05T14:00:00+00:00",
    "updated_at": "2026-07-05T14:00:09+00:00",
    "selected_route_id": "route_5b8e2f7c9d01",
}


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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "schema_version": 1,
                    "job_type": "ship_detection",
                    "area_of_interest": {
                        "type": "bbox",
                        "coordinates": [-74.3, 40.3, -73.5, 41.0],
                    },
                    "sensor": "SAR",
                    "priority": "fastest",
                    "compute_preference": "orbital_if_available",
                    "max_cost_usd": 500,
                }
            ]
        }
    )

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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job": {
                    **EXAMPLE_JOB,
                    "status": "queued",
                    "updated_at": "2026-07-05T14:00:00+00:00",
                    "selected_route_id": None,
                },
                "routing_decision": None,
            }
        }
    )

    job: Job
    # None until the async worker routes the job.
    routing_decision: Optional[RoutingDecision] = None


class JobsListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jobs": [EXAMPLE_JOB],
                "next_cursor": "MjAyNi0wNy0wNVQxNDowMDowMCswMDowMHxqb2JfOWYyYzQxZDNhOGI3",
            }
        }
    )

    jobs: List[Job]
    # Opaque keyset cursor; None when there are no further pages.
    next_cursor: Optional[str] = None


class JobDetailResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job": EXAMPLE_JOB,
                "routing_decision": EXAMPLE_DECISION,
                "result_summary": "Detected 17 vessels in New York Harbor.",
            }
        }
    )

    job: Job
    routing_decision: Optional[RoutingDecision] = None
    result_summary: Optional[str] = None


class SimulateRunResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job": EXAMPLE_JOB,
                "events_created": 8,
                "result": EXAMPLE_RESULT,
            }
        }
    )

    job: Job
    events_created: int
    result: Optional[Result] = None
