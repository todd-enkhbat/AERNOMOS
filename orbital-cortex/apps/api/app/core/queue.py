"""ARQ/Redis queue helpers."""

from __future__ import annotations

import asyncio

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import get_settings


def redis_settings() -> RedisSettings:
    settings = RedisSettings.from_dsn(get_settings().redis_url)
    settings.conn_retries = 1  # fail fast so job creation never hangs on Redis
    return settings


async def _enqueue(job_id: str) -> None:
    pool = await create_pool(redis_settings())
    try:
        await pool.enqueue_job("execute_job", job_id)
    finally:
        await pool.aclose()


def enqueue_job_execution(job_id: str) -> bool:
    """Enqueue async execution. Returns False when Redis is unreachable
    (the job stays queued and can be driven via /v1/simulate/run)."""
    try:
        asyncio.run(_enqueue(job_id))
        return True
    except Exception:
        return False
