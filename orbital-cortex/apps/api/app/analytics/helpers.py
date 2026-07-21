"""Route-level helpers for firing privacy-safe analytics events."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.emitter import emit_event
from app.analytics.hashing import hash_session_id
from app.analytics.schemas import (
    DataCandidatesFoundPayload,
    EventName,
    ExampleViewedPayload,
    MissionCompletedPayload,
    MissionStartedPayload,
    PlanExportedPayload,
    PlanGeneratedPayload,
    PlanningFailurePayload,
    PlanningFailureReason,
    PlanSharedPayload,
    ProviderConnectionRequestedPayload,
    UserReturnedPayload,
)
from app.db.mission_orm import (
    AnonymousSession,
    Mission,
    MissionPlan,
    MissionPlanStep,
    ShareLink,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def track_mission_started(
    db: Session,
    *,
    mission: Mission,
    owner: AnonymousSession,
) -> None:
    resources = list(mission.data_source_preference or [])
    if not resources and mission.objective_type:
        resources = [mission.objective_type]
    emit_event(
        db,
        EventName.MISSION_STARTED,
        MissionStartedPayload(
            mission_id=mission.id,
            session_id_hash=hash_session_id(owner.id),
            resource_types_requested=resources,
            timestamp=_now(),
        ),
    )


def track_data_candidates_found(
    db: Session,
    *,
    mission_id: uuid.UUID,
    candidate_count: int,
    provider_id: str,
    search_duration_seconds: float,
) -> None:
    emit_event(
        db,
        EventName.DATA_CANDIDATES_FOUND,
        DataCandidatesFoundPayload(
            mission_id=mission_id,
            candidate_count=candidate_count,
            provider_id=provider_id,
            search_duration_seconds=round(search_duration_seconds, 6),
            timestamp=_now(),
        ),
    )


def track_planning_failure(
    db: Session,
    *,
    mission_id: uuid.UUID,
    reason: PlanningFailureReason,
) -> None:
    emit_event(
        db,
        EventName.PLANNING_FAILURE,
        PlanningFailurePayload(
            mission_id=mission_id,
            reason=reason,
            timestamp=_now(),
        ),
    )


def track_plan_generated(
    db: Session,
    *,
    mission: Mission,
    owner: AnonymousSession,
    plan: MissionPlan,
    step_count: int,
    candidate_count: int,
    generation_seconds: float,
) -> None:
    emit_event(
        db,
        EventName.PLAN_GENERATED,
        PlanGeneratedPayload(
            mission_id=mission.id,
            plan_id=plan.id,
            step_count=step_count,
            candidate_count=candidate_count,
            generation_seconds=round(generation_seconds, 6),
            timestamp=_now(),
        ),
    )
    if plan.recommended:
        emit_event(
            db,
            EventName.MISSION_COMPLETED,
            MissionCompletedPayload(
                mission_id=mission.id,
                plan_id=plan.id,
                session_id_hash=hash_session_id(owner.id),
                timestamp=_now(),
            ),
        )


def track_provider_connection_requests(
    db: Session,
    *,
    mission_id: uuid.UUID,
    providers: Sequence[tuple[str, str]],
) -> None:
    seen: set[tuple[str, str]] = set()
    for provider_name, integration_status in providers:
        key = (provider_name, integration_status)
        if key in seen:
            continue
        seen.add(key)
        if integration_status not in {"sandbox_requested", "partner_connected"}:
            continue
        emit_event(
            db,
            EventName.PROVIDER_CONNECTION_REQUESTED,
            ProviderConnectionRequestedPayload(
                mission_id=mission_id,
                provider_name=provider_name,
                integration_status=integration_status,
                timestamp=_now(),
            ),
        )


def track_plan_exported(
    db: Session,
    *,
    mission_id: uuid.UUID,
    export_type: str,
    success: bool,
) -> None:
    emit_event(
        db,
        EventName.PLAN_EXPORTED,
        PlanExportedPayload(
            mission_id=mission_id,
            export_type=export_type,
            success=success,
            timestamp=_now(),
        ),
    )


def track_plan_shared(
    db: Session,
    *,
    mission: Mission,
    owner: AnonymousSession,
    link: ShareLink,
) -> None:
    emit_event(
        db,
        EventName.PLAN_SHARED,
        PlanSharedPayload(
            mission_id=mission.id,
            share_link_id=link.id,
            session_id_hash=hash_session_id(owner.id),
            timestamp=_now(),
        ),
    )


def track_example_viewed(db: Session, *, mission: Mission) -> None:
    if not mission.is_example:
        return
    emit_event(
        db,
        EventName.EXAMPLE_VIEWED,
        ExampleViewedPayload(
            mission_id=mission.id,
            timestamp=_now(),
        ),
    )


def track_user_returned(
    db: Session,
    *,
    session_row: AnonymousSession,
    previous_last_seen: datetime,
) -> None:
    now = _now()
    prev = previous_last_seen
    if prev.tzinfo is None:
        prev = prev.replace(tzinfo=timezone.utc)
    days = max(0.0, (now - prev).total_seconds() / 86400.0)
    emit_event(
        db,
        EventName.USER_RETURNED,
        UserReturnedPayload(
            session_id_hash=hash_session_id(session_row.id),
            days_since_last_seen=round(days, 4),
            timestamp=now,
        ),
    )


def providers_from_plan(db: Session, plan: MissionPlan) -> list[tuple[str, str]]:
    steps = db.scalars(
        select(MissionPlanStep).where(MissionPlanStep.mission_plan_id == plan.id)
    ).all()
    providers: list[tuple[str, str]] = []
    for step in steps:
        meta = step.source_metadata or {}
        integration = meta.get("integration_status")
        if step.provider_name and integration:
            providers.append((step.provider_name, str(integration)))
    return providers


class CatalogSearchTimer:
    """Context manager for catalog search duration."""

    def __init__(self) -> None:
        self._started = 0.0
        self.duration_seconds = 0.0

    def __enter__(self) -> CatalogSearchTimer:
        self._started = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self.duration_seconds = time.perf_counter() - self._started
