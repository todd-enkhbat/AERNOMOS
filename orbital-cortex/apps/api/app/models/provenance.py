"""Provenance envelope for mission-facing numeric and temporal values."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from app.db.truth import TruthStatus

# Standard explanation copy for truth-status popovers.
EXPLANATION_SIMULATED = (
    "This value is generated for demonstration and is not connected to a provider."
)
EXPLANATION_UNAVAILABLE = (
    "Nomos has not connected to a provider capable of performing this action."
)
EXPLANATION_ESTIMATED = (
    "Derived from provider metadata or heuristics — not directly measured."
)
EXPLANATION_CALCULATED_CONTACT = (
    "Pass geometry computed from a TLE snapshot using SGP4 propagation."
)
EXPLANATION_PROVIDER_STAC = (
    "Reported by the upstream STAC catalog provider."
)

FRESHNESS_FRESH = "fresh"
FRESHNESS_STALE = "stale"
FRESHNESS_UNKNOWN = "unknown"


def freshness_for(
    truth_status: Union[TruthStatus, str],
    *,
    retrieved_at: Optional[str] = None,
    stale_epoch_days: int = 7,
) -> str:
    """Map truth status + retrieval time to a freshness label."""
    status = (
        truth_status
        if isinstance(truth_status, TruthStatus)
        else TruthStatus(str(truth_status))
    )
    if status in (TruthStatus.STALE, TruthStatus.UNAVAILABLE):
        return FRESHNESS_STALE
    if status in (TruthStatus.SIMULATED, TruthStatus.ESTIMATED):
        return FRESHNESS_UNKNOWN
    if not retrieved_at:
        return FRESHNESS_UNKNOWN
    try:
        normalized = retrieved_at.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days
        if age_days > stale_epoch_days:
            return FRESHNESS_STALE
        return FRESHNESS_FRESH
    except (TypeError, ValueError):
        return FRESHNESS_UNKNOWN


class ProvenancedValue(BaseModel):
    value: Any
    truth_status: TruthStatus
    source: Optional[str] = None
    retrieved_at: Optional[str] = None
    effective_at: Optional[str] = None
    method: Optional[str] = None
    explanation: Optional[str] = None
    freshness: Optional[str] = None  # fresh | stale | unknown


def provenanced(
    value: Any,
    truth_status: Union[TruthStatus, str],
    *,
    source: Optional[str] = None,
    retrieved_at: Optional[str] = None,
    effective_at: Optional[str] = None,
    method: Optional[str] = None,
    explanation: Optional[str] = None,
    freshness: Optional[str] = None,
    stale_epoch_days: int = 7,
) -> Dict[str, Any]:
    """Build a JSON-serializable provenance envelope."""
    status = (
        truth_status
        if isinstance(truth_status, TruthStatus)
        else TruthStatus(str(truth_status))
    )
    resolved_freshness = freshness or freshness_for(
        status,
        retrieved_at=retrieved_at,
        stale_epoch_days=stale_epoch_days,
    )
    envelope = ProvenancedValue(
        value=value,
        truth_status=status,
        source=source,
        retrieved_at=retrieved_at,
        effective_at=effective_at,
        method=method,
        explanation=explanation,
        freshness=resolved_freshness,
    )
    return envelope.model_dump(mode="json")
