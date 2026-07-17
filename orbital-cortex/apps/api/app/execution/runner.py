"""Execute a queued ExecutionJob for real and persist OBSERVED metrics.

Runs on the ARQ worker (see app.workers.executor.run_execution_job) or
synchronously as a dev fallback when Redis is unreachable. All durations and
byte counts are measured from the actual run — never estimated or stubbed.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.object_store import content_type_for, get_object_store
from app.db import SessionLocal, get_engine
from app.db.mission_orm import ExecutionJob, MissionPlanStep
from app.db.truth import TruthStatus
from app.execution import tasks as task_impl
from app.execution.refs import resolve_input_ref
from app.execution.types import (
    STATUS_FAILED,
    STATUS_QUEUED,
    STATUS_RUNNING,
    STATUS_SUCCEEDED,
    STEP_EXECUTION_EXECUTED,
    STEP_EXECUTION_FAILED,
    STEP_EXECUTION_RUNNING,
    ExecutionError,
    ObservedMetrics,
)

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def storage_location() -> str:
    settings = get_settings()
    if settings.s3_bucket:
        return f"s3://{settings.s3_bucket}"
    return f"local:{settings.artifact_dir}"


def output_key_for(job: ExecutionJob) -> str:
    filename = task_impl.output_filename(job.task_type)
    return f"missions/{job.mission_id}/execution/{job.id}/{filename}"


def run_execution_job_sync(external_job_id: str) -> str:
    """Load the job, run it with guards, persist the outcome. Returns status."""
    session = SessionLocal(bind=get_engine())
    try:
        job = session.get(ExecutionJob, uuid.UUID(external_job_id))
        if job is None:
            raise ValueError(f"execution job not found: {external_job_id}")
        if job.status != STATUS_QUEUED:
            # Re-delivery of an already-run job (ARQ retry): do not re-run.
            return job.status

        job.status = STATUS_RUNNING
        job.started_at = utc_now()
        _update_step(session, job, STEP_EXECUTION_RUNNING)
        session.commit()

        try:
            observed = _execute(session, job)
        except ExecutionError as exc:
            _mark_failed(session, job, str(exc))
            session.commit()
            return STATUS_FAILED
        except Exception as exc:  # unexpected: still fail visibly, no hang
            logger.exception("execution job %s failed unexpectedly", job.id)
            _mark_failed(session, job, f"Unexpected execution failure: {exc}")
            session.commit()
            return STATUS_FAILED

        job.status = STATUS_SUCCEEDED
        job.error = None
        job.completed_at = utc_now()
        job.observed_metrics = observed.model_dump()
        _update_step(
            session,
            job,
            STEP_EXECUTION_EXECUTED,
            observed=observed,
            output_ref=f"artifact:{job.output_key}",
        )
        session.commit()
        return STATUS_SUCCEEDED
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _execute(session: Session, job: ExecutionJob) -> ObservedMetrics:
    """Stage input → run task with timeout → upload output. Measures all phases."""
    settings = get_settings()
    resolved = resolve_input_ref(job.input_ref, mission_id=job.mission_id)

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"nomos-exec-{job.id}-"))
    try:
        # --- Transfer in (measured) --------------------------------------
        input_path = tmp_dir / "input"
        transfer_started = time.perf_counter()
        if resolved.kind == "fixture":
            source = Path(resolved.location)
            input_bytes = source.stat().st_size
            if input_bytes > settings.execution_max_input_bytes:
                raise ExecutionError(
                    f"Input is {input_bytes} bytes which exceeds the provider "
                    f"limit of {settings.execution_max_input_bytes} bytes"
                )
            shutil.copyfile(source, input_path)
        else:
            data = get_object_store().get_bytes(resolved.location)
            if data is None:
                raise ExecutionError(
                    f"Input artifact not found in object store: {resolved.location}"
                )
            input_bytes = len(data)
            if input_bytes > settings.execution_max_input_bytes:
                raise ExecutionError(
                    f"Input is {input_bytes} bytes which exceeds the provider "
                    f"limit of {settings.execution_max_input_bytes} bytes"
                )
            input_path.write_bytes(data)
        transfer_in_seconds = time.perf_counter() - transfer_started

        # --- Execute with timeout (measured) ------------------------------
        output_path = tmp_dir / task_impl.output_filename(job.task_type)
        params = dict(job.params or {})
        timeout_s = settings.execution_max_seconds
        execution_started = time.perf_counter()
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(
                task_impl.run_task, job.task_type, input_path, output_path, params
            )
            future.result(timeout=timeout_s)
        except FutureTimeoutError as exc:
            raise ExecutionError(
                f"Execution exceeded the {timeout_s}s provider timeout and was "
                "marked failed"
            ) from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
        execution_seconds = time.perf_counter() - execution_started

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise ExecutionError("Task produced no output file")

        # --- Transfer out (measured); upload only after success -----------
        output_data = output_path.read_bytes()
        key = output_key_for(job)
        upload_started = time.perf_counter()
        get_object_store().put_bytes(key, output_data, content_type_for(key))
        transfer_out_seconds = time.perf_counter() - upload_started
        job.output_key = key

        return ObservedMetrics(
            transfer_seconds=transfer_in_seconds + transfer_out_seconds,
            execution_seconds=execution_seconds,
            input_bytes=input_bytes,
            output_bytes=len(output_data),
            storage_location=storage_location(),
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _mark_failed(session: Session, job: ExecutionJob, error: str) -> None:
    job.status = STATUS_FAILED
    job.error = error[:2000]
    job.completed_at = utc_now()
    job.output_key = None  # never point at a partial artifact
    _update_step(session, job, STEP_EXECUTION_FAILED, error=error)


def _update_step(
    session: Session,
    job: ExecutionJob,
    execution_status: str,
    *,
    observed: Optional[ObservedMetrics] = None,
    output_ref: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Persist execution state onto the mission plan step (planned → executed/failed)."""
    if job.mission_plan_step_id is None:
        return
    step = session.get(MissionPlanStep, job.mission_plan_step_id)
    if step is None:
        return
    step.execution_status = execution_status
    execution_record: dict[str, object] = {
        "external_job_id": str(job.id),
        "provider_id": job.provider_id,
        "task_type": job.task_type,
        "status": execution_status,
        "input_ref": job.input_ref,
    }
    if observed is not None:
        # Real measured values from this run — the only place OBSERVED is set.
        execution_record["observed"] = observed.model_dump()
        execution_record["truth_status"] = TruthStatus.OBSERVED.value
        step.executed_at = utc_now()
    if output_ref is not None:
        execution_record["output_ref"] = output_ref
    if error is not None:
        execution_record["error"] = error[:2000]
    # Reassign (not mutate) so SQLAlchemy detects the JSONB change.
    step.source_metadata = {
        **(step.source_metadata or {}),
        "execution": execution_record,
    }
