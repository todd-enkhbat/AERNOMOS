"""Redact sensitive tokens from log fields."""

from __future__ import annotations

import re

# Share resolve path embeds the raw token: /v1/share/{token}
_SHARE_PATH_RE = re.compile(r"^(/v1/share/)([^/]+)(.*)$", re.IGNORECASE)


def redact_request_path(path: str) -> str:
    """Replace raw share tokens in request paths before logging."""
    if not path:
        return path
    match = _SHARE_PATH_RE.match(path)
    if match:
        return f"{match.group(1)}[redacted]{match.group(3)}"
    return path
