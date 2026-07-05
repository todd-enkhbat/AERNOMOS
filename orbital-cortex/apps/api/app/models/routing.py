"""Routing decision model definitions."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.config import JsonDict

# Canonical NY Harbor demo decision, reused by the OpenAPI examples here
# and in app.models.job.
EXAMPLE_CANDIDATE: JsonDict = {
    "node_id": "sim_leo_01",
    "score": 0.87,
    "eligible": True,
    "hard_constraint_failures": [],
    "binding_constraint": None,
    "weights": {
        "model_support": 25,
        "latency": 25,
        "cost": 10,
        "availability": 15,
        "contact": 10,
        "preference": 10,
        "compliance": 5,
    },
    "model_support_score": 1.0,
    "latency_score": 0.92,
    "cost_score": 0.74,
    "availability_score": 0.97,
    "contact_score": 0.88,
    "preference_score": 1.0,
    "compliance_score": 1.0,
    "estimated_latency_minutes": 38.0,
    "estimated_cost_usd": 84.0,
    "available": True,
    "selected_ground_station_id": "gs_ksat_svalbard",
    "next_contact_minutes": 27.5,
    "next_aos_utc": "2026-07-05T14:27:30+00:00",
    "next_max_elevation_deg": 63.4,
    "est_downlink_mb": 42.0,
    "reasons": [
        "Onboard ship_detection model eliminates raw-scene downlink.",
        "Next Svalbard contact in 28 minutes fits the fastest priority.",
    ],
}

EXAMPLE_DECISION: JsonDict = {
    "id": "route_5b8e2f7c9d01",
    "job_id": "job_9f2c41d3a8b7",
    "selected_node_id": "sim_leo_01",
    "selected_ground_station_id": "gs_ksat_svalbard",
    "fallback_node_id": "aws_us_east_gpu",
    "estimated_latency_minutes": 38.0,
    "estimated_cost_usd": 84.0,
    "confidence": 0.87,
    "config_version": "2026.07.05-1",
    "input_hash": "a3f1c6e29b8d4c07",
    "decision_hash": "5d9e0b2a7c41f386",
    "tle_snapshot_id": "celestrak-2026-07-05",
    "seed": 42,
    "decided_at_utc": "2026-07-05T14:00:01+00:00",
    "reasons": [
        "sim_leo_01 scored highest for fastest priority with an onboard model.",
        "Fallback aws_us_east_gpu retained in case the contact window slips.",
    ],
    "candidate_scores": [EXAMPLE_CANDIDATE],
}


class HardConstraintFailure(BaseModel):
    constraint: str
    detail: str


class CandidateScore(BaseModel):
    node_id: str
    score: float
    eligible: bool
    hard_constraint_failures: List[HardConstraintFailure] = Field(default_factory=list)
    binding_constraint: Optional[str] = None
    weights: Dict[str, float] = Field(default_factory=dict)
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
    selected_ground_station_id: Optional[str] = None
    next_contact_minutes: Optional[float] = None
    next_aos_utc: Optional[str] = None
    next_max_elevation_deg: Optional[float] = None
    est_downlink_mb: Optional[float] = None
    reasons: List[str]


class RoutingDecision(BaseModel):
    id: str
    job_id: str
    selected_node_id: str
    selected_ground_station_id: Optional[str] = None
    fallback_node_id: Optional[str] = None
    estimated_latency_minutes: float
    estimated_cost_usd: float
    confidence: float = Field(ge=0, le=1)
    config_version: Optional[str] = None
    input_hash: Optional[str] = None
    decision_hash: Optional[str] = None
    tle_snapshot_id: Optional[str] = None
    seed: Optional[int] = None
    decided_at_utc: Optional[str] = None
    reasons: List[str]
    candidate_scores: List[CandidateScore]


class RoutingResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"routing_decision": EXAMPLE_DECISION}}
    )

    routing_decision: RoutingDecision


class ReplayResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match": True,
                "stored_decision_hash": "5d9e0b2a7c41f386",
                "replay_decision_hash": "5d9e0b2a7c41f386",
                "config_version": "2026.07.05-1",
                "input_hash": "a3f1c6e29b8d4c07",
            }
        }
    )

    match: bool
    stored_decision_hash: str
    replay_decision_hash: str
    config_version: str
    input_hash: str
