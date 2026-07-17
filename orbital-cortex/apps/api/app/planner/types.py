"""Shared types for the mission planning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PlanPattern(str, Enum):
    EXISTING_IMAGERY_CLOUD = "existing_imagery_cloud"
    EXISTING_IMAGERY_EDGE = "existing_imagery_edge"
    SATELLITE_GROUND_CLOUD = "satellite_ground_cloud"
    ONBOARD_PROCESSING = "onboard_processing"


class FeasibilityStatus(str, Enum):
    FEASIBLE = "feasible"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"


class PlanStatus(str, Enum):
    """Persisted MissionPlan.status values."""

    FEASIBLE = "feasible"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ConstraintFailure:
    code: str
    message: str


@dataclass
class ProvenancedEstimate:
    value: Optional[float]
    truth_status: str
    method: Optional[str] = None
    source: Optional[str] = None
    unit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "truth_status": self.truth_status,
            "method": self.method,
            "source": self.source,
            "unit": self.unit,
        }


@dataclass
class DraftStep:
    sequence: int
    step_type: str
    provider_name: str
    title: str
    description: str
    truth_status: str
    feasibility_status: str
    rejection_reason: Optional[str] = None
    resource_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    input_artifact: Optional[str] = None
    output_artifact: Optional[str] = None
    source_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DraftPlan:
    pattern: PlanPattern
    summary: str
    steps: List[DraftStep]
    feasibility_status: FeasibilityStatus = FeasibilityStatus.FEASIBLE
    rejection_reasons: List[ConstraintFailure] = field(default_factory=list)
    assumptions: List[Any] = field(default_factory=list)
    estimated_total_time_seconds: Optional[float] = None
    estimated_total_cost_usd: Optional[float] = None
    estimated_data_movement_mb: Optional[float] = None
    duration_truth_status: str = "ESTIMATED"
    cost_truth_status: str = "UNAVAILABLE"
    data_movement_truth_status: str = "ESTIMATED"
    duration_method: Optional[str] = None
    cost_method: Optional[str] = None
    data_movement_method: Optional[str] = None
    confidence: Optional[float] = None
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    plan_hash: str = ""
    candidate_id: Optional[str] = None
    contact_window_id: Optional[str] = None
    tle_snapshot_id: Optional[str] = None
    orbital_truth_status: Optional[str] = None
    explanation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionPlannerContext:
    """Immutable snapshot of mission inputs used for deterministic planning."""

    mission_id: str
    objective_type: str
    deadline: Optional[datetime]
    max_cost_usd: Optional[float]
    max_data_volume_mb: Optional[float]
    preferred_compute_location: Optional[str]
    allowed_regions: List[Any]
    data_source_preference: List[Any]
    customer_systems: List[Any]
    max_age_days: Optional[int]
    onboard_preference: Optional[str]
    data_residency: Optional[str]
    now_utc: datetime
    tle_snapshot_id: Optional[str]
    orbital_truth_status: str
    catalog_snapshot: List[Dict[str, Any]]
    contact_windows: List[Dict[str, Any]]
    coverage_by_candidate: Dict[str, float]
    planner_config_version: str

    def input_bundle(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "objective_type": self.objective_type,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "max_cost_usd": self.max_cost_usd,
            "max_data_volume_mb": self.max_data_volume_mb,
            "preferred_compute_location": self.preferred_compute_location,
            "allowed_regions": self.allowed_regions,
            "data_source_preference": self.data_source_preference,
            "customer_systems": self.customer_systems,
            "max_age_days": self.max_age_days,
            "onboard_preference": self.onboard_preference,
            "data_residency": self.data_residency,
            "now_utc": self.now_utc.isoformat(),
            "tle_snapshot_id": self.tle_snapshot_id,
            "orbital_truth_status": self.orbital_truth_status,
            "catalog_snapshot": self.catalog_snapshot,
            "contact_windows": [
                {
                    "id": w.get("id"),
                    "satellite_id": w.get("satellite_id"),
                    "ground_station_id": w.get("ground_station_id"),
                    "aos_utc": w.get("aos_utc"),
                    "los_utc": w.get("los_utc"),
                    "duration_s": w.get("duration_s"),
                    "est_downlink_mb": w.get("est_downlink_mb"),
                    "tle_snapshot_id": w.get("tle_snapshot_id"),
                }
                for w in self.contact_windows
            ],
            "coverage_by_candidate": self.coverage_by_candidate,
            "planner_config_version": self.planner_config_version,
        }
