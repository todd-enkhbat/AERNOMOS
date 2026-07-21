"""Versioned infrastructure provider registry — load, validate, upsert, query."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence
from uuid import UUID

import yaml
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.infrastructure_types import (
    PROVIDER_REGISTRY_KIND,
    IntegrationStatus,
)
from app.db.infrastructure_types import (
    InfrastructureResource as ProviderContract,
)
from app.db.mission_orm import InfrastructureResource as InfrastructureResourceRow
from app.db.session import REPO_ROOT
from app.db.truth import AccessLevel, TruthStatus

logger = logging.getLogger(__name__)

PROVIDERS_DIR = REPO_ROOT / "config" / "providers"

PLANNER_RESOURCE_TYPES = frozenset({"cloud", "edge", "ground_station", "orbital_compute"})

# Integration statuses that represent live or sandbox-connected availability.
CONNECTED_STATUSES = frozenset(
    {
        IntegrationStatus.SANDBOX_CONNECTED,
        IntegrationStatus.PARTNER_CONNECTED,
    }
)

PUBLIC_INFO_STATUSES = frozenset(
    {
        IntegrationStatus.PUBLIC_DATA_ONLY,
        IntegrationStatus.DOCUMENTED_API,
        IntegrationStatus.SANDBOX_REQUESTED,
    }
)

_SELECTION_PRIORITY = {
    IntegrationStatus.PARTNER_CONNECTED.value: 0,
    IntegrationStatus.SANDBOX_CONNECTED.value: 1,
    IntegrationStatus.DOCUMENTED_API.value: 2,
    IntegrationStatus.SANDBOX_REQUESTED.value: 3,
    IntegrationStatus.PUBLIC_DATA_ONLY.value: 4,
    IntegrationStatus.SIMULATED.value: 5,
    IntegrationStatus.UNAVAILABLE.value: 6,
}


def providers_config_dir(config_dir: Path | None = None) -> Path:
    return config_dir or PROVIDERS_DIR


def list_provider_config_paths(config_dir: Path | None = None) -> List[Path]:
    root = providers_config_dir(config_dir)
    if not root.is_dir():
        return []
    return sorted(root.glob("*.yaml")) + sorted(root.glob("*.yml"))


def load_provider_contract(path: Path) -> ProviderContract:
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    return ProviderContract.model_validate(raw)


def load_all_provider_contracts(
    config_dir: Path | None = None,
) -> List[ProviderContract]:
    contracts: List[ProviderContract] = []
    for path in list_provider_config_paths(config_dir):
        contracts.append(load_provider_contract(path))
    return contracts


def _access_level_for(status: IntegrationStatus) -> str:
    if status == IntegrationStatus.SIMULATED:
        return AccessLevel.SIMULATED.value
    if status == IntegrationStatus.SANDBOX_CONNECTED:
        return AccessLevel.SANDBOX_AVAILABLE.value
    if status == IntegrationStatus.PARTNER_CONNECTED:
        return AccessLevel.PARTNER_REQUIRED.value
    if status == IntegrationStatus.UNAVAILABLE:
        return AccessLevel.PRIVATE.value
    return AccessLevel.PUBLIC_INFORMATION.value


def _truth_status_for(contract: ProviderContract) -> TruthStatus:
    if contract.truth_status == "SIMULATED":
        return TruthStatus.SIMULATED
    return TruthStatus.PROVIDER_REPORTED


def _freshness_dt(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


def contract_to_row_fields(contract: ProviderContract) -> Dict[str, Any]:
    """Map a validated contract onto InfrastructureResource ORM columns."""
    return {
        "provider_name": contract.provider_name,
        "resource_type": contract.resource_type,
        "external_resource_id": contract.upsert_external_key(),
        "name": contract.provider_name,
        "location": None,
        "capabilities": {
            "api_available": contract.api_available,
            "sandbox_available": contract.sandbox_available,
            "auth_required": contract.auth_required,
            "supported_task_types": list(contract.supported_task_types),
            "supported_data_formats": list(contract.supported_data_formats),
            "current_status": contract.current_status,
        },
        "constraints": {
            "geography": contract.geography,
            "pricing_source": contract.pricing_source,
            "capacity_source": contract.capacity_source,
        },
        "pricing": None,
        "access_level": _access_level_for(contract.integration_status),
        "source_metadata": {
            "kind": PROVIDER_REGISTRY_KIND,
            "integration_status": contract.integration_status.value,
            "registry_truth_status": contract.truth_status,
            "source_url": contract.source_url,
            "notes": contract.notes,
            "contact_info": contract.contact_info,
            "data_freshness": contract.data_freshness.isoformat(),
            "external_id": contract.external_id,
        },
        "truth_status": _truth_status_for(contract),
        "data_freshness_at": _freshness_dt(contract.data_freshness),
        "active": contract.current_status != "deprecated",
    }


def find_registry_row(
    session: Session,
    contract: ProviderContract,
) -> InfrastructureResourceRow | None:
    external_key = contract.upsert_external_key()
    return session.scalars(
        select(InfrastructureResourceRow).where(
            InfrastructureResourceRow.provider_name == contract.provider_name,
            func.coalesce(InfrastructureResourceRow.external_resource_id, "")
            == external_key,
            InfrastructureResourceRow.source_metadata["kind"].astext
            == PROVIDER_REGISTRY_KIND,
        )
    ).one_or_none()


def upsert_provider_contract(
    session: Session,
    contract: ProviderContract,
    *,
    row_id: UUID | None = None,
) -> InfrastructureResourceRow:
    """Insert or update a registry-backed InfrastructureResource row."""
    row = find_registry_row(session, contract)
    fields = contract_to_row_fields(contract)
    if row is None:
        row = InfrastructureResourceRow(id=row_id or contract.id)
        session.add(row)
    for key, value in fields.items():
        setattr(row, key, value)
    session.flush()
    return row


def ingest_providers_from_config(
    session: Session,
    config_dir: Path | None = None,
) -> Dict[str, int]:
    """Validate and upsert all checked-in provider YAML files."""
    paths = list_provider_config_paths(config_dir)
    if not paths:
        raise FileNotFoundError(
            f"No provider YAML files found under {providers_config_dir(config_dir)}"
        )
    ingested = 0
    for path in paths:
        try:
            contract = load_provider_contract(path)
        except (ValidationError, ValueError) as exc:
            logger.error("Provider schema rejection (%s): %s", path.name, exc)
            raise ValueError(f"Provider schema rejection in {path.name}: {exc}") from exc
        upsert_provider_contract(session, contract)
        ingested += 1
    session.flush()
    return {"ingested": ingested, "files": len(paths)}


def is_registry_row(row: InfrastructureResourceRow) -> bool:
    meta = row.source_metadata if isinstance(row.source_metadata, dict) else {}
    return meta.get("kind") == PROVIDER_REGISTRY_KIND


def row_to_planner_dict(row: InfrastructureResourceRow) -> Dict[str, Any]:
    meta = row.source_metadata if isinstance(row.source_metadata, dict) else {}
    caps = row.capabilities if isinstance(row.capabilities, dict) else {}
    constraints = row.constraints if isinstance(row.constraints, dict) else {}
    integration_status = str(meta.get("integration_status") or "")
    registry_truth = str(meta.get("registry_truth_status") or "")
    return {
        "id": str(row.id),
        "provider_name": row.provider_name,
        "resource_type": row.resource_type,
        "external_id": meta.get("external_id"),
        "integration_status": integration_status,
        "registry_truth_status": registry_truth,
        "truth_status": (
            row.truth_status.value
            if isinstance(row.truth_status, TruthStatus)
            else str(row.truth_status)
        ),
        "source_url": meta.get("source_url"),
        "notes": meta.get("notes"),
        "access_level": row.access_level,
        "api_available": caps.get("api_available"),
        "sandbox_available": caps.get("sandbox_available"),
        "auth_required": caps.get("auth_required"),
        "supported_task_types": caps.get("supported_task_types") or [],
        "geography": constraints.get("geography"),
        "pricing_source": constraints.get("pricing_source"),
        "capacity_source": constraints.get("capacity_source"),
        "current_status": caps.get("current_status"),
        "is_simulated": integration_status == IntegrationStatus.SIMULATED.value,
        "is_public_info_only": integration_status
        in {s.value for s in PUBLIC_INFO_STATUSES},
        "is_connected": integration_status in {s.value for s in CONNECTED_STATUSES},
    }


def load_registry_for_planner(session: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Return active registry resources grouped by resource_type for the planner."""
    rows = session.scalars(
        select(InfrastructureResourceRow)
        .where(InfrastructureResourceRow.active.is_(True))
        .order_by(
            InfrastructureResourceRow.resource_type.asc(),
            InfrastructureResourceRow.provider_name.asc(),
        )
    ).all()
    grouped: Dict[str, List[Dict[str, Any]]] = {
        key: [] for key in PLANNER_RESOURCE_TYPES
    }
    for row in rows:
        if not is_registry_row(row):
            continue
        if row.resource_type not in grouped:
            continue
        grouped[row.resource_type].append(row_to_planner_dict(row))
    return grouped


def select_provider(
    resources: Sequence[Dict[str, Any]],
    *,
    preferred_name: str | None = None,
    prefer_non_simulated: bool = True,
) -> Dict[str, Any] | None:
    if not resources:
        return None
    if preferred_name:
        pref = preferred_name.strip().lower()
        for item in resources:
            name = str(item.get("provider_name") or "").lower()
            if pref in name or name in pref:
                return {
                    **item,
                    "selection_reason": (
                        f"Matched mission preferred_compute_location "
                        f"'{preferred_name.strip()}'."
                    ),
                }

    candidates = [
        item
        for item in resources
        if not (prefer_non_simulated and item.get("is_simulated"))
    ]
    if not candidates:
        candidates = list(resources)
    selected = min(
        candidates,
        key=lambda item: (
            _SELECTION_PRIORITY.get(
                str(item.get("integration_status") or ""),
                len(_SELECTION_PRIORITY),
            ),
            str(item.get("provider_name") or "").lower(),
        ),
    )
    return {
        **selected,
        "selection_reason": (
            "Selected by integration readiness, then provider name for "
            "deterministic tie-breaking."
        ),
    }


def count_registry_rows(session: Session) -> int:
    rows = session.scalars(select(InfrastructureResourceRow)).all()
    return sum(1 for row in rows if is_registry_row(row))


def registry_rows_for_display(session: Session) -> List[Dict[str, Any]]:
    rows = session.scalars(
        select(InfrastructureResourceRow)
        .where(InfrastructureResourceRow.active.is_(True))
        .order_by(
            InfrastructureResourceRow.source_metadata["integration_status"].astext.asc(),
            InfrastructureResourceRow.provider_name.asc(),
        )
    ).all()
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not is_registry_row(row):
            continue
        meta = row.source_metadata if isinstance(row.source_metadata, dict) else {}
        out.append(
            {
                "provider_name": row.provider_name,
                "resource_type": row.resource_type,
                "integration_status": meta.get("integration_status"),
                "registry_truth_status": meta.get("registry_truth_status"),
                "source_url": meta.get("source_url"),
            }
        )
    return out
