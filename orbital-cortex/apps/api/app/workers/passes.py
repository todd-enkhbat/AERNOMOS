"""ARQ tasks: TLE refresh + contact-window precompute."""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.core.config import get_settings
from app.db import SessionLocal, get_engine
from app.seed import apply_orbital_snapshot
from app.services import tle_cache
from app.services.contact_windows import precompute_windows

logger = logging.getLogger(__name__)


def refresh_tle_snapshot_sync(*, prefer_live: bool = True) -> Dict[str, Any]:
    """Fetch live TLEs (fallback to pinned), persist fleet rows, return metadata."""
    snapshot = tle_cache.resolve_orbital_snapshot(prefer_live=prefer_live)
    session = SessionLocal(bind=get_engine())
    try:
        apply_orbital_snapshot(session, snapshot)
        from app.services.mission_infrastructure import upsert_infrastructure_resources

        # Satellite infra only; ground stations are seeded separately.
        upsert_infrastructure_resources(
            session, snapshot=snapshot, ground_stations=[]
        )
        session.commit()
        meta = tle_cache.get_orbital_snapshot_metadata(snapshot)
        logger.info(
            "refreshed TLE snapshot %s source=%s truth=%s",
            meta["snapshot_id"],
            meta["source"],
            meta["truth_status"],
        )
        return meta
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


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


async def refresh_tle_snapshot(ctx: Dict[str, Any]) -> Dict[str, Any]:
    import asyncio

    return await asyncio.to_thread(refresh_tle_snapshot_sync)


async def precompute_passes(ctx: Dict[str, Any]) -> int:
    import asyncio

    created = await asyncio.to_thread(precompute_passes_sync)
    logger.info("precomputed %d contact windows", created)
    return created
