"""Cryptographic token minting and hashing for sessions and share links.

Raw tokens are never persisted. Only SHA-256 hex digests are stored.
"""

from __future__ import annotations

import hashlib
import secrets


def mint_token() -> str:
    """Return a URL-safe opaque token suitable for cookies or share URLs."""
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    """SHA-256 hex digest (64 chars) of a raw session or share token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
