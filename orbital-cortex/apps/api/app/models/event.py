"""Job event model definitions."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class JobEvent(BaseModel):
    id: str
    job_id: str
    event_type: str
    message: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    ts_utc: str


class JobEventsResponse(BaseModel):
    events: List[JobEvent]
