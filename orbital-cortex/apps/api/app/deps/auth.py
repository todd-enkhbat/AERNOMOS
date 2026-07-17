"""Auth dependencies for anonymous sessions and mission access."""

from __future__ import annotations

from typing import Optional

from fastapi import Cookie, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core import missions as mission_store
from app.core import sessions as session_store
from app.core.config import get_settings
from app.db import get_db
from app.db.mission_orm import AnonymousSession, Mission


def _api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message}},
    )


def _raw_session_token(request: Request) -> Optional[str]:
    settings = get_settings()
    return request.cookies.get(settings.session_cookie_name)


def get_optional_anonymous_session(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[AnonymousSession]:
    raw = _raw_session_token(request)
    if not raw:
        return None
    row = session_store.get_session_by_raw_token(db, raw)
    if row is None:
        return None
    session_store.touch_session(row)
    return row


def require_anonymous_session(
    request: Request,
    db: Session = Depends(get_db),
) -> AnonymousSession:
    row = get_optional_anonymous_session(request, db)
    if row is None:
        raise _api_error(
            401,
            "session_required",
            "A private anonymous session cookie is required.",
        )
    return row


def load_mission_for_access(
    *,
    db: Session,
    mission_id: str,
    owner: Optional[AnonymousSession],
    share_token: Optional[str],
) -> Mission:
    try:
        mid = mission_store.parse_mission_id(mission_id)
    except ValueError as exc:
        raise _api_error(404, "mission_not_found", "Mission not found.") from exc

    mission = mission_store.get_mission(db, mid)
    if mission is None:
        raise _api_error(404, "mission_not_found", "Mission not found.")

    if mission.is_example:
        return mission

    if owner is not None and mission_store.session_owns_mission(owner, mission):
        return mission

    token = (share_token or "").strip() or None
    if token:
        link = mission_store.get_active_share_link(db, token)
        if link is not None and link.mission_id == mission.id:
            return mission
        raise _api_error(
            403,
            "share_token_invalid",
            "Share link is invalid, expired, or revoked.",
        )

    if owner is None:
        raise _api_error(
            401,
            "session_required",
            "A private anonymous session cookie or share token is required.",
        )
    raise _api_error(
        403,
        "mission_forbidden",
        "This mission belongs to another private session.",
    )


def get_mission_for_read(
    mission_id: str,
    request: Request,
    db: Session = Depends(get_db),
    x_nomos_share_token: Optional[str] = Header(default=None),
    share_token: Optional[str] = Query(default=None),
) -> Mission:
    owner = get_optional_anonymous_session(request, db)
    token = x_nomos_share_token or share_token
    return load_mission_for_access(
        db=db,
        mission_id=mission_id,
        owner=owner,
        share_token=token,
    )


def get_owned_mission(
    mission_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> Mission:
    owner = require_anonymous_session(request, db)
    mission = load_mission_for_access(
        db=db,
        mission_id=mission_id,
        owner=owner,
        share_token=None,
    )
    if mission.is_example or not mission_store.session_owns_mission(owner, mission):
        raise _api_error(
            403,
            "mission_forbidden",
            "This mission belongs to another private session.",
        )
    return mission


# Cookie is read via Request so the configured cookie name is honored.
_ = Cookie
