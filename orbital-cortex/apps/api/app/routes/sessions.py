"""Anonymous private session routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core import sessions as session_store
from app.core.config import get_settings
from app.db import get_db
from app.deps.auth import get_optional_anonymous_session, require_anonymous_session
from app.models.errors import ErrorResponse
from app.models.mission import SessionResponse

router = APIRouter(prefix="/v1", tags=["sessions"])


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=201,
    summary="Create or resume a private anonymous session",
    description=(
        "Ensures a private anonymous session cookie. If a valid cookie is "
        "already present, resumes it. Otherwise mints a new session token, "
        "stores only its hash, and sets an HttpOnly cookie."
    ),
    responses={
        200: {"model": SessionResponse, "description": "Existing session resumed"},
    },
)
def ensure_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    settings = get_settings()
    session_store.cleanup_expired_sessions(db)

    existing = get_optional_anonymous_session(request, db)
    if existing is not None:
        db.commit()
        response.status_code = 200
        return {"session": session_store.session_to_dict(existing), "created": False}

    row, raw = session_store.create_anonymous_session(db, settings=settings)
    db.commit()
    session_store.set_session_cookie(
        response, raw, settings=settings, expires_at=row.expires_at
    )
    response.status_code = 201
    return {"session": session_store.session_to_dict(row), "created": True}


@router.get(
    "/sessions/me",
    response_model=SessionResponse,
    summary="Read the current anonymous session",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
    },
)
def current_session(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    row = require_anonymous_session(request, db)
    db.commit()
    return {"session": session_store.session_to_dict(row), "created": False}


@router.delete(
    "/sessions/me",
    status_code=204,
    summary="End the current anonymous session cookie",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
    },
)
def end_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    row = require_anonymous_session(request, db)
    db.delete(row)
    db.commit()
    session_store.clear_session_cookie(response)
    response.status_code = 204
    return response
