"""Public write endpoints for feedback and design-partner capture.

No public read endpoints — leads and feedback are private.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import missions as mission_store
from app.core.ratelimit import leads_rate_limit, limiter
from app.db import get_db
from app.db.mission_orm import AnonymousSession, Mission
from app.deps.auth import get_optional_anonymous_session, get_owned_mission
from app.leads import service as leads_service
from app.leads.schemas import (
    HONEYPOT_FIELD,
    DesignPartnerRequestCreate,
    DesignPartnerRequestResponse,
    MissionFeedbackCreate,
    MissionFeedbackResponse,
)
from app.models.errors import ErrorResponse

router = APIRouter(prefix="/v1", tags=["leads"])


def _api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message}},
    )


@router.post(
    "/missions/{mission_id}/feedback",
    response_model=MissionFeedbackResponse,
    status_code=201,
    summary="Submit optional mission plan feedback",
    description=(
        "Lightweight yes/partly/no feedback after a plan exists. Never required "
        "for planning. Comment is capped server-side (reject, not truncate)."
    ),
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    },
)
@limiter.limit(leads_rate_limit)
def submit_mission_feedback(
    request: Request,
    payload: MissionFeedbackCreate,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
    owner: Optional[AnonymousSession] = Depends(get_optional_anonymous_session),
) -> Dict[str, Any]:
    row = leads_service.create_feedback(
        db,
        mission_id=mission.id,
        payload=payload,
        session_id=owner.id if owner else None,
    )
    db.commit()
    db.refresh(row)
    return {"feedback": leads_service.feedback_to_model(row)}


@router.post(
    "/design-partner-requests",
    response_model=DesignPartnerRequestResponse,
    status_code=201,
    summary="Request a design-partner conversation",
    description=(
        "Stores a private design-partner lead. permission_to_contact must be true. "
        "A honeypot field is accepted but never persisted when filled."
    ),
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    },
)
@limiter.limit(leads_rate_limit)
def submit_design_partner_request(
    request: Request,
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if not isinstance(body, dict):
        raise _api_error(422, "validation_error", "JSON object required.")

    # Honeypot lives outside DesignPartnerRequestCreate — strip before validate.
    honeypot = body.get(HONEYPOT_FIELD)
    if isinstance(honeypot, str) and honeypot.strip():
        # Silent success — do not persist bot submissions.
        return {
            "request": {
                "id": "00000000-0000-4000-8000-0000000000b0",
                "mission_id": None,
                "name": "accepted",
                "work_email": "noreply@example.com",
                "organization": "accepted",
                "role": "accepted",
                "mission_type": "accepted",
                "requested_integration": "accepted",
                "permission_to_contact": True,
                "created_at": leads_service.utc_now().isoformat(),
            }
        }

    cleaned = {k: v for k, v in body.items() if k != HONEYPOT_FIELD}
    try:
        payload = DesignPartnerRequestCreate.model_validate(cleaned)
    except ValidationError as exc:
        errors = exc.errors()
        if errors:
            first = errors[0]
            loc = ".".join(str(p) for p in first.get("loc", ()) if p != "body")
            msg = first.get("msg", "Request validation failed.")
            message = f"{loc}: {msg}" if loc else str(msg)
        else:
            message = "Request validation failed."
        raise _api_error(422, "validation_error", message) from exc

    if payload.mission_id is not None:
        mission = mission_store.get_mission(db, payload.mission_id)
        if mission is None:
            raise _api_error(404, "mission_not_found", "Mission not found.")

    row = leads_service.create_design_partner_request(db, payload=payload)
    db.commit()
    db.refresh(row)
    return {"request": leads_service.design_partner_to_model(row)}
