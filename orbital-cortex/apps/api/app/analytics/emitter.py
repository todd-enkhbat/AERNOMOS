"""Strict allowlisted analytics event emitter."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.analytics.orm import AnalyticsEvent
from app.analytics.schemas import PAYLOAD_BY_EVENT, EventName, _AllowlistedPayload


class AnalyticsPayloadError(ValueError):
    """Raised when an analytics payload violates the allowlist."""


def emit_event(
    db: Session,
    event: EventName,
    payload: _AllowlistedPayload | dict[str, Any],
) -> AnalyticsEvent:
    """Validate and persist one analytics event.

    Rejects payloads with keys outside the event allowlist (Pydantic
    ``extra='forbid'``). Never silently drops fields.
    """
    payload_cls = PAYLOAD_BY_EVENT[event]
    try:
        if isinstance(payload, BaseModel):
            validated = payload_cls.model_validate(payload.model_dump())
        else:
            validated = payload_cls.model_validate(payload)
    except ValidationError as exc:
        raise AnalyticsPayloadError(
            f"Analytics payload rejected for {event.value}: {exc}"
        ) from exc

    row = AnalyticsEvent(
        id=uuid.uuid4(),
        event_name=event.value,
        payload=validated.model_dump(mode="json"),
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.flush()
    return row
