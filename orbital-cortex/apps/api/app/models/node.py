"""Compute node model definitions."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ComputeNode(BaseModel):
    id: str
    name: str
    type: Literal["orbital", "ground_cloud", "ground_station"]
    location: str
    orbit: Optional[str] = None
    gpu_class: str
    supported_models: List[str]
    storage_gb: int
    downlink_mbps: int
    power_state: str
    availability: float = Field(ge=0, le=1)
    compliance_tags: List[str]
    base_cost_usd: float
    latency_minutes: float
    next_contact_minutes: float = 0


class GroundStation(BaseModel):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    latency_minutes: float
    downlink_mbps: int
    availability: float = Field(ge=0, le=1)


class NodesResponse(BaseModel):
    compute_nodes: List[ComputeNode]
    ground_stations: List[GroundStation]
