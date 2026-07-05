"""Job model definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

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
JobStatus = Literal["queued", "scheduled", "running", "completed", "failed"]


class JobCreate(BaseModel):
    job_type: JobType
    area_of_interest: Dict[str, Any]
    sensor: Sensor
    priority: Priority
    compute_preference: ComputePreference
    max_cost_usd: float = Field(gt=0)


class Job(BaseModel):
    id: str
    job_type: JobType
    area_of_interest: Dict[str, Any]
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
    routing_decision: RoutingDecision


class JobsListResponse(BaseModel):
    jobs: List[Job]


class JobDetailResponse(BaseModel):
    job: Job
    routing_decision: Optional[RoutingDecision] = None
    result_summary: Optional[str] = None


class SimulateRunResponse(BaseModel):
    job: Job
    events_created: int
    result: Result
