"""ARQ task: precompute contact windows off the request hot path."""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.services.contact_windows import precompute_windows

logger = logging.getLogger(__name__)


def precompute_passes_sync() -> int:
    session = SessionLocal(bind=get_engine())
    try:
        created = precompute_windows(
            session, horizon_hours=get_settings().pass_horizon_hours
        )
        session.commit()
        return created
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def precompute_passes(ctx: Dict[str, Any]) -> int:
    import asyncio

    created = await asyncio.to_thread(precompute_passes_sync)
    logger.info("precomputed %d contact windows", created)
    return created
