"""Persist and summarize private feedback / design-partner leads."""

from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.hashing import hash_session_id
from app.leads.orm import DesignPartnerRequestRow, MissionFeedbackRow
from app.leads.schemas import (
    DesignPartnerRequest,
    DesignPartnerRequestCreate,
    FeedbackRating,
    MissionFeedback,
    MissionFeedbackCreate,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def feedback_to_model(row: MissionFeedbackRow) -> MissionFeedback:
    return MissionFeedback(
        id=row.id,
        mission_id=row.mission_id,
        session_id_hash=row.session_id_hash,
        rating=FeedbackRating(row.rating),
        comment=row.comment,
        created_at=row.created_at,
    )


def design_partner_to_model(row: DesignPartnerRequestRow) -> DesignPartnerRequest:
    return DesignPartnerRequest(
        id=row.id,
        mission_id=row.mission_id,
        name=row.name,
        work_email=row.work_email,
        organization=row.organization,
        role=row.role,
        mission_type=row.mission_type,
        requested_integration=row.requested_integration,
        permission_to_contact=row.permission_to_contact,
        created_at=row.created_at,
    )


def create_feedback(
    db: Session,
    *,
    mission_id: uuid.UUID,
    payload: MissionFeedbackCreate,
    session_id: Optional[uuid.UUID] = None,
) -> MissionFeedbackRow:
    row = MissionFeedbackRow(
        id=uuid.uuid4(),
        mission_id=mission_id,
        session_id_hash=hash_session_id(session_id) if session_id else None,
        rating=payload.rating.value,
        comment=payload.comment,
        created_at=utc_now(),
    )
    db.add(row)
    db.flush()
    return row


def create_design_partner_request(
    db: Session,
    *,
    payload: DesignPartnerRequestCreate,
) -> DesignPartnerRequestRow:
    row = DesignPartnerRequestRow(
        id=uuid.uuid4(),
        mission_id=payload.mission_id,
        name=payload.name,
        work_email=str(payload.work_email),
        organization=payload.organization,
        role=payload.role,
        mission_type=payload.mission_type,
        requested_integration=payload.requested_integration,
        permission_to_contact=True,
        created_at=utc_now(),
    )
    db.add(row)
    db.flush()
    return row


def list_all_feedback(db: Session) -> list[MissionFeedbackRow]:
    return list(
        db.scalars(
            select(MissionFeedbackRow).order_by(MissionFeedbackRow.created_at.desc())
        ).all()
    )


def list_all_design_partner_requests(db: Session) -> list[DesignPartnerRequestRow]:
    return list(
        db.scalars(
            select(DesignPartnerRequestRow).order_by(
                DesignPartnerRequestRow.created_at.desc()
            )
        ).all()
    )


def compute_leads_summary(db: Session) -> dict[str, Any]:
    feedback_rows = list_all_feedback(db)
    lead_rows = list_all_design_partner_requests(db)

    by_rating = Counter(row.rating for row in feedback_rows)
    by_org = Counter(row.organization for row in lead_rows)
    by_mission_type = Counter(row.mission_type for row in lead_rows)

    return {
        "generated_at": utc_now().isoformat(),
        "feedback": {
            "total": len(feedback_rows),
            "by_rating": {
                FeedbackRating.YES.value: by_rating.get(FeedbackRating.YES.value, 0),
                FeedbackRating.PARTLY.value: by_rating.get(
                    FeedbackRating.PARTLY.value, 0
                ),
                FeedbackRating.NO.value: by_rating.get(FeedbackRating.NO.value, 0),
            },
        },
        "design_partner_requests": {
            "total": len(lead_rows),
            "by_organization": dict(by_org.most_common()),
            "by_mission_type": dict(by_mission_type.most_common()),
        },
    }


def feedback_count(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(MissionFeedbackRow)) or 0)


def design_partner_count(db: Session) -> int:
    return int(
        db.scalar(select(func.count()).select_from(DesignPartnerRequestRow)) or 0
    )
