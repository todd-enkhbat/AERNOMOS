"""Core data models for a Nomos compute job.

Kept intentionally minimal for the MVS: a job in, a result out, and the
statuses needed to log a full lifecycle. Billing/compliance fields will
extend JobResult later — not in scope for this skeleton.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    SUBMITTED = "submitted"
    ROUTED = "routed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Job:
    """A unit of compute work a customer wants run on an orbital node."""

    job_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    submitted_at: str = field(default_factory=_now)


@dataclass
class JobResult:
    """Outcome of running a Job, whatever node it landed on."""

    job_id: str
    status: JobStatus
    node_name: str | None = None
    output: dict[str, Any] | None = None
    error: str | None = None
    duration_s: float | None = None
