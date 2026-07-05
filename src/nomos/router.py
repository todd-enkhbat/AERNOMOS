"""Routing: pick the best available node for a job.

MVS scope: one registered node, so "best" degenerates to "the one that's
available and supports the job type." The interface is shaped so a real
scheduler (multiple nodes, range windows, job-type fit, priority) can
replace the body of `select_node` later without touching callers.
"""

from __future__ import annotations

from .models import Job
from .nodes.base import Node


class NoAvailableNodeError(RuntimeError):
    """Raised when no registered node can currently take the job."""


class Router:
    def __init__(self, nodes: list[Node]):
        self._nodes = nodes

    def select_node(self, job: Job) -> Node:
        candidates = [n for n in self._nodes if n.supports(job.job_type)]
        if not candidates:
            raise NoAvailableNodeError(
                f"no registered node supports job_type={job.job_type!r}"
            )

        available = [n for n in candidates if n.is_available()]
        if not available:
            raise NoAvailableNodeError(
                f"no available node (in range) for job_type={job.job_type!r}"
            )

        # MVS: first available match. Future: rank by range window,
        # queue depth, cost, etc.
        return available[0]
