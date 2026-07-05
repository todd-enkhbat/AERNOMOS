"""Routing decision model definitions."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateScore(BaseModel):
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
    reasons: List[str]
    candidate_scores: List[CandidateScore]


class RoutingResponse(BaseModel):
    routing_decision: RoutingDecision
