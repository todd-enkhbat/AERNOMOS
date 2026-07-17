"""Infrastructure provider registry contracts (Phase N).

Single source of truth for field names and validation — ingestion and the
mission planner import from here; do not duplicate shapes elsewhere.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class IntegrationStatus(str, Enum):
    PUBLIC_DATA_ONLY = "public_data_only"
    DOCUMENTED_API = "documented_api"
    SANDBOX_REQUESTED = "sandbox_requested"
    SANDBOX_CONNECTED = "sandbox_connected"
    PARTNER_CONNECTED = "partner_connected"
    SIMULATED = "simulated"
    UNAVAILABLE = "unavailable"


RegistryTruthStatus = Literal["VERIFIED", "PUBLIC_SOURCE", "SIMULATED"]
RegistryResourceType = Literal["cloud", "edge", "ground_station", "orbital_compute"]
RegistryCurrentStatus = Literal["active", "beta", "deprecated", "unknown"]

PROVIDER_REGISTRY_KIND = "provider_registry"


class InfrastructureResource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    provider_name: str
    resource_type: RegistryResourceType
    external_id: Optional[str] = None
    api_available: bool
    sandbox_available: bool
    auth_required: bool
    supported_task_types: list[str]
    supported_data_formats: list[str]
    geography: Optional[str] = None
    pricing_source: Optional[str] = None
    capacity_source: Optional[str] = None
    current_status: RegistryCurrentStatus
    data_freshness: date
    contact_info: Optional[str] = None
    integration_status: IntegrationStatus
    truth_status: RegistryTruthStatus
    source_url: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _require_source_url_for_non_simulated(self) -> "InfrastructureResource":
        if self.integration_status == IntegrationStatus.SIMULATED:
            if self.truth_status != "SIMULATED":
                raise ValueError(
                    "Simulated registry entries must set truth_status=SIMULATED"
                )
            return self
        if self.truth_status == "SIMULATED":
            raise ValueError(
                "truth_status=SIMULATED requires integration_status=simulated"
            )
        if not self.source_url or not str(self.source_url).strip():
            raise ValueError(
                f"source_url is required for non-simulated provider "
                f"'{self.provider_name}' (integration_status="
                f"{self.integration_status.value})"
            )
        return self

    def upsert_external_key(self) -> str:
        """Stable idempotency key segment when external_id is unknown."""
        return self.external_id or ""


def integration_status_from_raw(value: object) -> IntegrationStatus:
    if isinstance(value, IntegrationStatus):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError("integration_status is required")
    try:
        return IntegrationStatus(value.strip().lower())
    except ValueError as exc:
        allowed = ", ".join(s.value for s in IntegrationStatus)
        raise ValueError(
            f"Invalid integration_status '{value}'. Expected one of: {allowed}"
        ) from exc
