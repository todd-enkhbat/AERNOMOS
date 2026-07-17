"""ARQ worker that drives the job pipeline.

Run with:
    arq app.workers.executor.WorkerSettings

The pipeline is resumable: each stage advances from the persisted job status,
so if the worker is killed mid-flight, ARQ's retry re-runs the task and it
continues from where the last committed transition left off.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from arq import cron

from app.core.config import get_settings
from app.core.pipeline import fail_job, run_pipeline
from app.core.queue import redis_settings
from app.db import SessionLocal, get_engine
from app.exports import service as export_service
from app.workers.passes import precompute_passes, refresh_tle_snapshot

logger = logging.getLogger(__name__)


def run_pipeline_sync(job_id: str) -> Dict[str, Any]:
    session = SessionLocal(bind=get_engine())
    try:
        outcome = run_pipeline(
            session,
            job_id,
            stage_delay_s=get_settings().worker_stage_delay_s,
        )
        session.commit()
        return outcome
    except Exception as exc:
        session.rollback()
        try:
            fail_job(session, job_id, str(exc))
            session.commit()
        except Exception:
            session.rollback()
        raise
    finally:
        session.close()


async def execute_job(ctx: Dict[str, Any], job_id: str) -> str:
    logger.info("executing job %s", job_id)
    outcome = await asyncio.to_thread(run_pipeline_sync, job_id)
    return outcome["job"]["status"]


def generate_mission_pdf_export_sync(export_id: str) -> str:
    import uuid

    session = SessionLocal(bind=get_engine())
    try:
        row = export_service.generate_pdf_export(session, uuid.UUID(export_id))
        session.commit()
        return row.status
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def generate_mission_pdf_export(ctx: Dict[str, Any], export_id: str) -> str:
    logger.info("generating mission PDF export %s", export_id)
    return await asyncio.to_thread(generate_mission_pdf_export_sync, export_id)


async def run_execution_job(ctx: Dict[str, Any], external_job_id: str) -> str:
    """Phase M: real CPU plan-step execution (crop_geotiff, thumbnail)."""
    from app.execution.runner import run_execution_job_sync

    logger.info("running execution job %s", external_job_id)
    return await asyncio.to_thread(run_execution_job_sync, external_job_id)


async def startup(ctx: Dict[str, Any]) -> None:
    # Warm the contact-window cache so routing never waits on propagation.
    await precompute_passes(ctx)


class WorkerSettings:
    functions = [
        execute_job,
        precompute_passes,
        refresh_tle_snapshot,
        generate_mission_pdf_export,
        run_execution_job,
    ]
    # Refresh TLEs then recompute passes every 6 hours.
    cron_jobs = [
        cron(refresh_tle_snapshot, hour={0, 6, 12, 18}, minute=0),
        cron(precompute_passes, hour={0, 6, 12, 18}, minute=5),
    ]
    on_startup = startup
    redis_settings = redis_settings()
    max_jobs = 10
    job_timeout = 300
    max_tries = 3
