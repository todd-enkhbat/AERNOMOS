"""Optional Redis / in-process TTL cache for catalog search responses."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any, Dict, Optional

from app.core.config import get_settings

# Short TTL: catalog freshness matters; avoid long-lived stale scenes.
DEFAULT_TTL_SECONDS = 300


class _MemoryCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> Optional[str]:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= now:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + ttl_seconds, value)


_MEMORY = _MemoryCache()


def cache_key(prefix: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
    return f"nomos:catalog:{prefix}:{digest}"


def _redis_client() -> Any:
    """Return a sync Redis client or None when unreachable."""
    try:
        import redis
    except ImportError:
        return None
    try:
        client = redis.Redis.from_url(
            get_settings().redis_url,
            socket_connect_timeout=0.4,
            socket_timeout=0.4,
            decode_responses=True,
        )
        client.ping()
        return client
    except Exception:
        return None


def cache_get(key: str) -> Optional[str]:
    client = _redis_client()
    if client is not None:
        try:
            value = client.get(key)
            if isinstance(value, str):
                return value
        except Exception:
            pass
    return _MEMORY.get(key)


def cache_set(key: str, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
    client = _redis_client()
    if client is not None:
        try:
            client.setex(key, ttl_seconds, value)
            return
        except Exception:
            pass
    _MEMORY.set(key, value, ttl_seconds)
