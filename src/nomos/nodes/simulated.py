"""A faithfully-simulated orbital node.

Stands in for any real node during the MVS. Simulates:
- a visibility window (is the node "in range" right now)
- job runtime (a short, bounded delay)
- occasional failure, so the router/logger failure path is exercised

This is generic on purpose — it is not a stand-in for any one satellite.
Swap in a real Node subclass per integration when that hardware exists.
"""

from __future__ import annotations

import random
import time

from ..models import Job, JobResult, JobStatus
from .base import Node


class SimulatedNode(Node):
    def __init__(
        self,
        name: str = "sim-node-1",
        capabilities: set[str] | None = None,
        *,
        always_available: bool = True,
        failure_rate: float = 0.0,
        min_runtime_s: float = 0.05,
        max_runtime_s: float = 0.2,
        seed: int | None = None,
    ) -> None:
        self.name = name
        self.capabilities = capabilities or {"generic-compute"}
        self._always_available = always_available
        self._failure_rate = failure_rate
        self._min_runtime_s = min_runtime_s
        self._max_runtime_s = max_runtime_s
        self._rng = random.Random(seed)

    def is_available(self) -> bool:
        if self._always_available:
            return True
        # Placeholder for a real visibility-window check.
        return self._rng.random() > 0.2

    def run(self, job: Job) -> JobResult:
        start = time.monotonic()
        runtime = self._rng.uniform(self._min_runtime_s, self._max_runtime_s)
        time.sleep(runtime)
        duration = time.monotonic() - start

        if self._rng.random() < self._failure_rate:
            return JobResult(
                job_id=job.job_id,
                status=JobStatus.FAILED,
                node_name=self.name,
                error="simulated node failure",
                duration_s=duration,
            )

        return JobResult(
            job_id=job.job_id,
            status=JobStatus.COMPLETED,
            node_name=self.name,
            output={"echo": job.payload, "simulated": True},
            duration_s=duration,
        )
