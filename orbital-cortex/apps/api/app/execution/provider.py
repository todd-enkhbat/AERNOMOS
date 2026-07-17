"""ExecutionProvider interface and the local CPU implementation (Phase M).

LocalCpuExecutionProvider runs real raster tasks (crop_geotiff, thumbnail)
on the existing ARQ worker — no GPUs, no onboard satellites, no fabricated
results. When Redis is unreachable (local dev / tests) submit falls back to
running the job synchronously so the path stays fully real end-to-end.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.queue import enqueue_execution_job
from app.db.mission_orm import ExecutionJob
from app.execution import runner
from app.execution.refs import resolve_input_ref
from app.execution.types import (
    STATUS_FAILED,
    STATUS_QUEUED,
    SUPPORTED_TASK_TYPES,
    ExecutionEstimate,
    ExecutionResult,
    ExecutionStateError,
    ExecutionTask,
    ExecutionValidationError,
    ExternalJob,
    ExternalJobStatus,
    ObservedMetrics,
    ProviderCapabilities,
)

LOCAL_CPU_PROVIDER_ID = "local-cpu"

# Conservative local CPU raster throughput assumption for estimates only
# (observed values always come from real runs, never from this constant).
_ESTIMATE_BASE_SECONDS = 0.2
_ESTIMATE_BYTES_PER_SECOND = 25 * 1024 * 1024


@dataclass(frozen=True)
class ExecutionContext:
    """Mission/plan/step linkage recorded on submitted jobs."""

    mission_id: uuid.UUID
    mission_plan_id: Optional[uuid.UUID] = None
    mission_plan_step_id: Optional[uuid.UUID] = None


class ExecutionProvider:
    """Provider interface — implementations must not fabricate results."""

    def capabilities(self) -> ProviderCapabilities:
        raise NotImplementedError

    def estimate(self, task: ExecutionTask) -> ExecutionEstimate:
        raise NotImplementedError

    def submit(self, task: ExecutionTask, idempotency_key: str) -> ExternalJob:
        raise NotImplementedError

    def status(self, external_job_id: str) -> ExternalJobStatus:
        raise NotImplementedError

    def cancel(self, external_job_id: str) -> None:
        raise NotImplementedError

    def result(self, external_job_id: str) -> ExecutionResult:
        raise NotImplementedError


def derive_idempotency_key(
    *,
    plan_id: uuid.UUID,
    step_id: uuid.UUID,
    task: ExecutionTask,
) -> str:
    """Deterministic key so identical client retries map to one job."""
    payload = json.dumps(
        {
            "plan_id": str(plan_id),
            "step_id": str(step_id),
            "task_type": task.task_type,
            "input_ref": task.input_ref,
            "params": task.params,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class LocalCpuExecutionProvider(ExecutionProvider):
    def __init__(self, db: Session, context: Optional[ExecutionContext] = None) -> None:
        self._db = db
        self._context = context

    def capabilities(self) -> ProviderCapabilities:
        settings = get_settings()
        return ProviderCapabilities(
            provider_id=LOCAL_CPU_PROVIDER_ID,
            supported_task_types=list(SUPPORTED_TASK_TYPES),
            max_input_bytes=settings.execution_max_input_bytes,
            max_execution_seconds=settings.execution_max_seconds,
        )

    def estimate(self, task: ExecutionTask) -> ExecutionEstimate:
        self._validate_task_type(task)
        input_bytes = self._known_input_bytes(task)
        estimated = _ESTIMATE_BASE_SECONDS + (input_bytes / _ESTIMATE_BYTES_PER_SECOND)
        return ExecutionEstimate(
            estimated_seconds=round(estimated, 3),
            estimated_cost_usd=0.0,  # local CPU on existing worker
        )

    def submit(self, task: ExecutionTask, idempotency_key: str) -> ExternalJob:
        if not idempotency_key or len(idempotency_key) > 128:
            raise ExecutionValidationError(
                "idempotency_key must be a non-empty string of at most 128 chars"
            )

        existing = self._by_idempotency_key(idempotency_key)
        if existing is not None:
            # Idempotent replay: return the stored job unchanged. Nothing is
            # re-enqueued and nothing re-runs.
            return _to_external_job(existing)

        if self._context is None:
            raise ExecutionStateError(
                "submit() requires an ExecutionContext (mission/plan/step)"
            )
        self._validate_task_type(task)
        # Raises ExecutionValidationError for anything outside the allowlist.
        resolve_input_ref(task.input_ref, mission_id=self._context.mission_id)

        job = ExecutionJob(
            id=uuid.uuid4(),
            idempotency_key=idempotency_key,
            mission_id=self._context.mission_id,
            mission_plan_id=self._context.mission_plan_id,
            mission_plan_step_id=self._context.mission_plan_step_id,
            provider_id=LOCAL_CPU_PROVIDER_ID,
            task_type=task.task_type,
            input_ref=task.input_ref,
            params=task.params or {},
            status=STATUS_QUEUED,
        )
        self._db.add(job)
        try:
            self._db.flush()
        except Exception:
            # Unique-key race: another submit with the same key won. Return it.
            self._db.rollback()
            existing = self._by_idempotency_key(idempotency_key)
            if existing is not None:
                return _to_external_job(existing)
            raise

        # The worker session must see the row before ARQ (or the sync
        # fallback) picks it up.
        self._db.commit()

        external_id = str(job.id)
        if not enqueue_execution_job(external_id):
            # Redis unreachable (local dev / tests): run the real task
            # synchronously in-process instead of leaving it stuck queued.
            runner.run_execution_job_sync(external_id)
            self._db.expire_all()
            refreshed = self._db.get(ExecutionJob, job.id)
            if refreshed is not None:
                return _to_external_job(refreshed)
        return _to_external_job(job)

    def status(self, external_job_id: str) -> ExternalJobStatus:
        job = self._get_job(external_job_id)
        return ExternalJobStatus(
            external_job_id=str(job.id),
            status=job.status,  # type: ignore[arg-type]
            error=job.error,
        )

    def cancel(self, external_job_id: str) -> None:
        job = self._get_job(external_job_id)
        if job.status != STATUS_QUEUED:
            raise ExecutionStateError(
                f"Only queued jobs can be cancelled (job is {job.status})"
            )
        job.status = STATUS_FAILED
        job.error = "Cancelled before execution"
        job.completed_at = runner.utc_now()
        self._db.flush()

    def result(self, external_job_id: str) -> ExecutionResult:
        job = self._get_job(external_job_id)
        if job.status != "succeeded" or not job.output_key or not job.observed_metrics:
            raise ExecutionStateError(
                f"Job {external_job_id} has no result (status: {job.status})"
            )
        return ExecutionResult(
            external_job_id=str(job.id),
            output_ref=f"artifact:{job.output_key}",
            observed=ObservedMetrics(**job.observed_metrics),
        )

    # --- internals ---------------------------------------------------------

    def _validate_task_type(self, task: ExecutionTask) -> None:
        if task.task_type not in SUPPORTED_TASK_TYPES:
            supported = ", ".join(SUPPORTED_TASK_TYPES)
            raise ExecutionValidationError(
                f"task_type must be one of: {supported}"
            )

    def _known_input_bytes(self, task: ExecutionTask) -> int:
        """Fixture size when resolvable; artifacts are sized at run time."""
        if self._context is None:
            return 0
        try:
            resolved = resolve_input_ref(
                task.input_ref, mission_id=self._context.mission_id
            )
        except ExecutionValidationError:
            return 0
        if resolved.kind == "fixture":
            from pathlib import Path

            return Path(resolved.location).stat().st_size
        return 0

    def _by_idempotency_key(self, idempotency_key: str) -> Optional[ExecutionJob]:
        return self._db.scalars(
            select(ExecutionJob).where(
                ExecutionJob.idempotency_key == idempotency_key
            )
        ).first()

    def _get_job(self, external_job_id: str) -> ExecutionJob:
        try:
            jid = uuid.UUID(external_job_id)
        except ValueError as exc:
            raise ExecutionStateError(
                f"Unknown execution job: {external_job_id}"
            ) from exc
        job = self._db.get(ExecutionJob, jid)
        if job is None:
            raise ExecutionStateError(f"Unknown execution job: {external_job_id}")
        return job


def _to_external_job(job: ExecutionJob) -> ExternalJob:
    return ExternalJob(
        external_job_id=str(job.id),
        idempotency_key=job.idempotency_key,
        status=job.status,  # type: ignore[arg-type]
    )
