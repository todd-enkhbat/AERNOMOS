"""Anonymous session persistence and cookie helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.tokens import hash_token, mint_token
from app.db.mission_orm import AnonymousSession


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def session_to_dict(row: AnonymousSession) -> Dict[str, Any]:
    return {
        "id": str(row.id),
        "created_at": row.created_at.isoformat(),
        "last_seen_at": row.last_seen_at.isoformat(),
        "expires_at": row.expires_at.isoformat(),
        "converted_user_id": (
            str(row.converted_user_id) if row.converted_user_id else None
        ),
    }


def cleanup_expired_sessions(session: Session, *, now: Optional[datetime] = None) -> int:
    """Delete expired anonymous sessions (missions cascade). Returns row count."""
    cutoff = now or utc_now()
    result = session.execute(
        delete(AnonymousSession).where(AnonymousSession.expires_at <= cutoff)
    )
    return int(getattr(result, "rowcount", 0) or 0)


def create_anonymous_session(
    session: Session,
    *,
    settings: Optional[Settings] = None,
) -> tuple[AnonymousSession, str]:
    """Persist a new anonymous session; return (row, raw_token)."""
    settings = settings or get_settings()
    now = utc_now()
    raw = mint_token()
    row = AnonymousSession(
        id=uuid.uuid4(),
        session_token_hash=hash_token(raw),
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=settings.session_ttl_days),
    )
    session.add(row)
    session.flush()
    return row, raw


def get_session_by_raw_token(
    session: Session, raw_token: str, *, now: Optional[datetime] = None
) -> Optional[AnonymousSession]:
    cutoff = now or utc_now()
    token_hash = hash_token(raw_token)
    row = session.scalars(
        select(AnonymousSession).where(
            AnonymousSession.session_token_hash == token_hash,
            AnonymousSession.expires_at > cutoff,
        )
    ).one_or_none()
    return row


def touch_session(row: AnonymousSession, *, now: Optional[datetime] = None) -> None:
    row.last_seen_at = now or utc_now()


def set_session_cookie(
    response: Response,
    raw_token: str,
    *,
    settings: Optional[Settings] = None,
    expires_at: Optional[datetime] = None,
) -> None:
    settings = settings or get_settings()
    max_age = settings.session_ttl_days * 24 * 60 * 60
    if expires_at is not None:
        max_age = max(0, int((expires_at - utc_now()).total_seconds()))
    kwargs: Dict[str, Any] = {
        "key": settings.session_cookie_name,
        "value": raw_token,
        "httponly": True,
        "secure": settings.app_env == "production",
        "samesite": "lax",
        "max_age": max_age,
        "path": "/",
    }
    domain = (settings.session_cookie_domain or "").strip()
    if domain:
        kwargs["domain"] = domain
    response.set_cookie(**kwargs)


def clear_session_cookie(
    response: Response, *, settings: Optional[Settings] = None
) -> None:
    settings = settings or get_settings()
    kwargs: Dict[str, Any] = {
        "key": settings.session_cookie_name,
        "path": "/",
    }
    domain = (settings.session_cookie_domain or "").strip()
    if domain:
        kwargs["domain"] = domain
    response.delete_cookie(**kwargs)
