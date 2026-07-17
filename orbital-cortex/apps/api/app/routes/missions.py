"""Private mission and share-link routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core import missions as mission_store
from app.core.config import get_settings
from app.db import get_db
from app.db.mission_orm import AnonymousSession, Mission, ShareLink
from app.deps.auth import (
    get_mission_for_read,
    get_owned_mission,
    require_anonymous_session,
)
from app.models.errors import ErrorResponse
from app.models.mission import (
    MissionCreate,
    MissionResponse,
    MissionsListResponse,
    ShareLinkCreate,
    ShareLinkResponse,
)

router = APIRouter(prefix="/v1", tags=["missions"])


def _api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message}},
    )


def _parse_optional_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _api_error(422, "validation_error", f"Invalid datetime: {value}") from exc


@router.get(
    "/missions/examples",
    response_model=MissionsListResponse,
    summary="List curated public example missions",
    description=(
        "Returns missions explicitly marked as public examples. These are "
        "not private user submissions and are safe to show without a session."
    ),
)
def list_examples(db: Session = Depends(get_db)) -> Dict[str, Any]:
    rows = mission_store.list_example_missions(db)
    return {
        "missions": [mission_store.mission_to_dict(db, row) for row in rows],
    }


@router.get(
    "/missions",
    response_model=MissionsListResponse,
    summary="List missions for the current private session",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
    },
)
def list_missions(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    owner = require_anonymous_session(request, db)
    rows = mission_store.list_session_missions(db, owner.id)
    db.commit()
    return {
        "missions": [mission_store.mission_to_dict(db, row) for row in rows],
    }


@router.post(
    "/missions",
    response_model=MissionResponse,
    status_code=201,
    summary="Create a private mission for the current session",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
        422: {"model": ErrorResponse, "description": "Invalid mission payload"},
    },
)
def create_mission(
    payload: MissionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    owner = require_anonymous_session(request, db)
    data = payload.model_dump()
    data["start_time"] = _parse_optional_dt(payload.start_time)
    data["end_time"] = _parse_optional_dt(payload.end_time)
    data["deadline"] = _parse_optional_dt(payload.deadline)
    try:
        mission = mission_store.create_mission(db, owner=owner, payload=data)
    except ValueError as exc:
        raise _api_error(422, "validation_error", str(exc)) from exc
    db.commit()
    db.refresh(mission)
    return {"mission": mission_store.mission_to_dict(db, mission)}


@router.get(
    "/missions/{mission_id}",
    response_model=MissionResponse,
    summary="Read a mission (owner session or valid share token)",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden or invalid share token"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def get_mission(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    db.commit()
    return {"mission": mission_store.mission_to_dict(db, mission)}


@router.post(
    "/missions/{mission_id}/share-links",
    response_model=ShareLinkResponse,
    status_code=201,
    summary="Create a private share link for a mission you own",
    description=(
        "Returns the raw share token once. Only the SHA-256 hash is stored. "
        "Pass the token as `X-Nomos-Share-Token` or `share_token` query param."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def create_share_link(
    payload: ShareLinkCreate,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    expires_at = _parse_optional_dt(payload.expires_at)
    link, raw = mission_store.create_share_link(
        db,
        mission,
        settings=get_settings(),
        expires_at=expires_at,
        permissions=payload.permissions,
    )
    db.commit()
    return {
        "share_link": mission_store.share_link_to_dict(link, include_token=raw),
    }


@router.post(
    "/missions/{mission_id}/share-links/{share_link_id}/revoke",
    response_model=ShareLinkResponse,
    summary="Revoke a share link you own",
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Share link not found"},
    },
)
def revoke_share_link(
    share_link_id: str,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        link_id = mission_store.parse_mission_id(share_link_id)
    except ValueError as exc:
        raise _api_error(404, "share_link_not_found", "Share link not found.") from exc

    link = db.get(ShareLink, link_id)
    if link is None or link.mission_id != mission.id:
        raise _api_error(404, "share_link_not_found", "Share link not found.")

    mission_store.revoke_share_link(link)
    db.commit()
    return {"share_link": mission_store.share_link_to_dict(link)}


# Keep owner type referenced for mypy/docs.
_ = AnonymousSession
