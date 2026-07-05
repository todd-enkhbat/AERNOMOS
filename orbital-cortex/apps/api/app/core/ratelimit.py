"""slowapi rate limiter shared by the app and route decorators.

Lives in its own module so routes can import the limiter without a
circular import through app.main.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=get_settings().rate_limit_enabled,
)


def jobs_rate_limit() -> str:
    # Callable so tests and env changes take effect per-request.
    return get_settings().rate_limit_jobs
