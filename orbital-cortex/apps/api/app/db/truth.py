"""Shared truth-status vocabulary for mission-planning data.

Every user-facing value derived from external sources, models, or estimates
must carry one of these labels. Values match the Nomos build plan and
capability-truth docs exactly (uppercase snake identifiers).
"""

from __future__ import annotations

from enum import Enum


class TruthStatus(str, Enum):
    OBSERVED = "OBSERVED"
    CALCULATED = "CALCULATED"
    PROVIDER_REPORTED = "PROVIDER_REPORTED"
    ESTIMATED = "ESTIMATED"
    SIMULATED = "SIMULATED"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


TRUTH_STATUS_VALUES = tuple(status.value for status in TruthStatus)


class InfrastructureResourceType(str, Enum):
    """Supported ``InfrastructureResource.resource_type`` values."""

    SATELLITE = "satellite"
    ORBITAL_COMPUTE = "orbital_compute"
    GROUND_STATION = "ground_station"
    CLOUD_COMPUTE = "cloud_compute"
    CUSTOMER_EDGE = "customer_edge"
    STORAGE = "storage"
    NETWORK = "network"


class AccessLevel(str, Enum):
    """How a planner may use an infrastructure resource today."""

    PUBLIC_INFORMATION = "public_information"
    SANDBOX_AVAILABLE = "sandbox_available"
    PARTNER_REQUIRED = "partner_required"
    PRIVATE = "private"
    SIMULATED = "simulated"


ACCESS_LEVEL_VALUES = tuple(level.value for level in AccessLevel)
