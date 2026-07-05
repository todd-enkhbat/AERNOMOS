"""Job event model definitions."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class JobEvent(BaseModel):
    id: str
    job_id: str
    event_type: str
    message: str
    timestamp: str


class JobEventsResponse(BaseModel):
    events: List[JobEvent]
