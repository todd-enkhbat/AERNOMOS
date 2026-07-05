"""Typed request and response shapes for the Orbital Cortex SDK."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


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


class AreaOfInterest(TypedDict):
    type: str
    coordinates: List[float]


class JobCreateParams(TypedDict):
    job_type: JobType
    area_of_interest: AreaOfInterest
    sensor: Sensor
    priority: Priority
    compute_preference: ComputePreference
    max_cost_usd: float


class Job(TypedDict):
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
    selected_route_id: Optional[str]


class ComputeNode(TypedDict):
    id: str
    name: str
    type: Literal["orbital", "ground_cloud", "ground_station"]
    location: str
    orbit: Optional[str]
    gpu_class: str
    supported_models: List[str]
    storage_gb: int
    downlink_mbps: int
    power_state: str
    availability: float
    compliance_tags: List[str]
    base_cost_usd: float
    latency_minutes: float
    next_contact_minutes: float


class GroundStation(TypedDict):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    latency_minutes: float
    downlink_mbps: int
    availability: float


class CandidateScore(TypedDict, total=False):
    node_id: str
    score: float
    eligible: bool
    model_support_score: float
    latency_score: float
    cost_score: float
    availability_score: float
    contact_score: float
    preference_score: float
    compliance_score: float
    estimated_latency_minutes: float
    estimated_cost_usd: float
    available: bool
    selected_ground_station_id: Optional[str]
    reasons: List[str]


class RoutingDecision(TypedDict):
    id: str
    job_id: str
    selected_node_id: str
    selected_ground_station_id: Optional[str]
    fallback_node_id: Optional[str]
    estimated_latency_minutes: float
    estimated_cost_usd: float
    confidence: float
    reasons: List[str]
    candidate_scores: List[CandidateScore]


class JobEvent(TypedDict):
    id: str
    job_id: str
    event_type: str
    message: str
    timestamp: str


class Result(TypedDict):
    id: str
    job_id: str
    summary: str
    confidence: float
    geojson: Dict[str, Any]
    output_files: List[str]


class JobCreateResponse(TypedDict):
    job: Job
    routing_decision: RoutingDecision


class JobsListResponse(TypedDict):
    jobs: List[Job]


class JobDetailResponse(TypedDict):
    job: Job
    routing_decision: Optional[RoutingDecision]
    result_summary: Optional[str]


class JobEventsResponse(TypedDict):
    events: List[JobEvent]


class ResultResponse(TypedDict):
    result: Result


class NodesResponse(TypedDict):
    compute_nodes: List[ComputeNode]
    ground_stations: List[GroundStation]


class RoutingResponse(TypedDict):
    routing_decision: RoutingDecision


class SimulateRunResponse(TypedDict):
    job: Job
    events_created: int
    result: Result
