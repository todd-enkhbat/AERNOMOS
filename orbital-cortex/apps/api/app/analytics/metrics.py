"""Operational metrics and accelerator traction summary."""

from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.orm import AnalyticsEvent
from app.analytics.schemas import EventName
from app.db.mission_orm import ExecutionJob, Mission, MissionExport, ShareLink
from app.db.orm import Satellite
from app.execution.types import STATUS_SUCCEEDED
from app.exports.service import EXPORT_TYPE_PDF, STATUS_FAILED, STATUS_READY
from app.services import tle_cache


def _percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _event_count(db: Session, event_name: str) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(AnalyticsEvent.event_name == event_name)
        )
        or 0
    )


def _event_payloads(db: Session, event_name: str) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(AnalyticsEvent)
        .where(AnalyticsEvent.event_name == event_name)
        .order_by(AnalyticsEvent.created_at.asc())
    ).all()
    return [row.payload for row in rows]


def compute_analytics_summary(db: Session) -> dict[str, Any]:
    """Aggregate product events and ops health for admin / CLI."""
    missions_started = _event_count(db, EventName.MISSION_STARTED.value)
    plans_generated = _event_count(db, EventName.PLAN_GENERATED.value)
    missions_completed = _event_count(db, EventName.MISSION_COMPLETED.value)

    completion_rate: float | None = None
    if missions_started:
        completion_rate = round(missions_completed / missions_started, 4)

    plan_gen_payloads = _event_payloads(db, EventName.PLAN_GENERATED.value)
    gen_seconds = [
        float(p["generation_seconds"])
        for p in plan_gen_payloads
        if p.get("generation_seconds") is not None
    ]

    catalog_payloads = _event_payloads(db, EventName.DATA_CANDIDATES_FOUND.value)
    catalog_durations = [
        float(p["search_duration_seconds"])
        for p in catalog_payloads
        if p.get("search_duration_seconds") is not None
    ]
    catalog_failures = _event_count(db, EventName.PLANNING_FAILURE.value)

    missions_by_status = dict(
        db.execute(
            select(Mission.status, func.count())
            .where(Mission.is_example.is_(False))
            .group_by(Mission.status)
        ).all()
    )

    export_failures = int(
        db.scalar(
            select(func.count())
            .select_from(MissionExport)
            .where(MissionExport.status == STATUS_FAILED)
        )
        or 0
    )

    share_links_created = int(
        db.scalar(select(func.count()).select_from(ShareLink)) or 0
    )
    share_links_active = int(
        db.scalar(
            select(func.count())
            .select_from(ShareLink)
            .where(ShareLink.revoked_at.is_(None))
        )
        or 0
    )

    exec_total = int(db.scalar(select(func.count()).select_from(ExecutionJob)) or 0)
    exec_succeeded = int(
        db.scalar(
            select(func.count())
            .select_from(ExecutionJob)
            .where(ExecutionJob.status == STATUS_SUCCEEDED)
        )
        or 0
    )
    cpu_success_rate: float | None = None
    if exec_total:
        cpu_success_rate = round(exec_succeeded / exec_total, 4)

    satellites = list(db.scalars(select(Satellite)).all())
    orbital_meta = tle_cache.metadata_from_db_satellites(satellites)
    orbital_freshness_hours: float | None = None
    retrieved_raw = orbital_meta.get("retrieved_at")
    if retrieved_raw:
        try:
            retrieved_dt = tle_cache.parse_iso_utc(str(retrieved_raw))
            now = datetime.now(timezone.utc)
            orbital_freshness_hours = round(
                (now - retrieved_dt).total_seconds() / 3600.0, 2
            )
        except ValueError:
            orbital_freshness_hours = None
    elif orbital_meta.get("epochs"):
        try:
            newest_epoch = max(
                tle_cache.parse_iso_utc(str(epoch))
                for epoch in orbital_meta["epochs"]
            )
            now = datetime.now(timezone.utc)
            orbital_freshness_hours = round(
                (now - newest_epoch).total_seconds() / 3600.0, 2
            )
        except ValueError:
            orbital_freshness_hours = None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "traction": {
            "missions_started": missions_started,
            "plans_generated": plans_generated,
            "missions_completed": missions_completed,
            "completion_rate": completion_rate,
            "example_views": _event_count(db, EventName.EXAMPLE_VIEWED.value),
            "user_returns": _event_count(db, EventName.USER_RETURNED.value),
        },
        "catalog": {
            "searches": len(catalog_payloads),
            "failures": catalog_failures,
            "avg_search_seconds": (
                round(statistics.mean(catalog_durations), 4) if catalog_durations else None
            ),
            "p50_search_seconds": _percentile(catalog_durations, 0.5),
            "p95_search_seconds": _percentile(catalog_durations, 0.95),
        },
        "planner": {
            "generations": len(gen_seconds),
            "avg_generation_seconds": (
                round(statistics.mean(gen_seconds), 4) if gen_seconds else None
            ),
            "p50_generation_seconds": _percentile(gen_seconds, 0.5),
            "p95_generation_seconds": _percentile(gen_seconds, 0.95),
        },
        "missions_by_status": {str(k): int(v) for k, v in missions_by_status.items()},
        "exports": {
            "pdf_ready": int(
                db.scalar(
                    select(func.count())
                    .select_from(MissionExport)
                    .where(
                        MissionExport.export_type == EXPORT_TYPE_PDF,
                        MissionExport.status == STATUS_READY,
                    )
                )
                or 0
            ),
            "failures": export_failures,
        },
        "sharing": {
            "links_created": share_links_created,
            "links_active": share_links_active,
            "plan_shared_events": _event_count(db, EventName.PLAN_SHARED.value),
        },
        "execution": {
            "jobs_total": exec_total,
            "jobs_succeeded": exec_succeeded,
            "success_rate": cpu_success_rate,
        },
        "orbital_data": {
            "snapshot_id": orbital_meta.get("snapshot_id"),
            "truth_status": orbital_meta.get("truth_status"),
            "newest_satellite_update_hours_ago": orbital_freshness_hours,
        },
    }
