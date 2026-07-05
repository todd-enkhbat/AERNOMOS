"""The customer-facing SDK entry point.

`NomosClient(nodes=[...]).submit_job(...)` is the one call a customer
makes — same shape as calling a cloud provider's API. Everything about
routing, node heterogeneity, and logging happens behind it.
"""

from __future__ import annotations

from typing import Any

from .job_log import JobLogger
from .models import Job, JobResult, JobStatus
from .nodes.base import Node
from .router import NoAvailableNodeError, Router


class NomosClient:
    def __init__(self, nodes: list[Node], logger: JobLogger | None = None):
        self._router = Router(nodes)
        self._log = logger or JobLogger()

    def submit_job(self, job_type: str, payload: dict[str, Any] | None = None) -> JobResult:
        job = Job(job_type=job_type, payload=payload or {})
        self._log.log_submitted(job)

        try:
            node = self._router.select_node(job)
        except NoAvailableNodeError as exc:
            result = JobResult(job_id=job.job_id, status=JobStatus.FAILED, error=str(exc))
            self._log.log_result(result)
            return result

        self._log.log_routed(job, node.name)

        try:
            result = node.run(job)
        except Exception as exc:  # node misbehaved; don't let it crash the client
            result = JobResult(
                job_id=job.job_id,
                status=JobStatus.FAILED,
                node_name=node.name,
                error=f"node raised unexpectedly: {exc}",
            )

        self._log.log_result(result)
        return result
