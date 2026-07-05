"""Routing decision model definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
    routing_decision: RoutingDecision


class ReplayResponse(BaseModel):
    match: bool
    stored_decision_hash: str
    replay_decision_hash: str
    config_version: str
    input_hash: str
