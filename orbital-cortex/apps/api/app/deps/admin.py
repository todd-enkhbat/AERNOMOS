"""Admin auth dependency shared by internal export endpoints."""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException

from app.core.config import get_settings


def verify_admin_token(provided: str) -> bool:
    """Constant-time compare against ADMIN_TOKEN. Empty expected → always False."""
    settings = get_settings()
    expected = (settings.admin_token or "").strip()
    if not expected:
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


def require_admin_token(
    x_nomos_admin_token: str = Header(default="", alias="X-Nomos-Admin-Token"),
) -> None:
    if not verify_admin_token(x_nomos_admin_token):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "admin_unauthorized",
                    "message": "Valid X-Nomos-Admin-Token required.",
                }
            },
        )
