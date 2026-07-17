"""HMAC-SHA256 hashing for analytics identifiers.

Raw session cookies and share tokens are never logged. Hashed values use a
dedicated ``ANALYTICS_HASH_SALT`` (separate from auth signing keys) so hashes
are not reversible even if another secret leaks. The same input always
produces the same hash, enabling return-user analysis without identifying
the underlying token.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid

from app.core.config import Settings, get_settings


def hash_session_id(session_id: uuid.UUID, *, settings: Settings | None = None) -> str:
    """Hash an anonymous session row id for analytics (never the cookie token)."""
    settings = settings or get_settings()
    return _hmac_hex(str(session_id), settings)


def hash_share_token(raw_token: str, *, settings: Settings | None = None) -> str:
    """Hash a raw share token before any analytics reference."""
    settings = settings or get_settings()
    return _hmac_hex(raw_token, settings)


def _hmac_hex(value: str, settings: Settings) -> str:
    salt = (settings.analytics_hash_salt or "").strip()
    if not salt:
        raise ValueError("ANALYTICS_HASH_SALT is required for analytics hashing")
    return hmac.new(
        salt.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
