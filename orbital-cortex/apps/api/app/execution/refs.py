"""input_ref validation against an explicit allowlist.

Two forms are accepted — anything else is rejected loudly (4xx at the API
boundary), never silently ignored:

- ``fixture:<filename>``  — a file inside the configured execution fixture
  directory. Plain filenames only; path traversal is rejected.
- ``artifact:<key>``      — an object-store key previously produced for the
  same mission (``missions/{mission_id}/...``), enabling chained tasks such
  as crop_geotiff → thumbnail.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.core.config import get_settings
from app.execution.types import ExecutionValidationError

_FIXTURE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

FIXTURE_PREFIX = "fixture:"
ARTIFACT_PREFIX = "artifact:"


@dataclass(frozen=True)
class ResolvedInputRef:
    kind: Literal["fixture", "artifact"]
    # Absolute path for fixtures; object-store key for artifacts.
    location: str


def fixture_dir() -> Path:
    return Path(get_settings().execution_fixture_dir)


def resolve_input_ref(input_ref: str, *, mission_id: uuid.UUID) -> ResolvedInputRef:
    """Validate input_ref against the allowlist or raise ExecutionValidationError."""
    if not isinstance(input_ref, str) or not input_ref:
        raise ExecutionValidationError("input_ref is required")

    if input_ref.startswith(FIXTURE_PREFIX):
        name = input_ref[len(FIXTURE_PREFIX):]
        if not _FIXTURE_NAME_RE.match(name) or ".." in name:
            raise ExecutionValidationError(
                "fixture input_ref must be a plain filename (no paths)"
            )
        path = (fixture_dir() / name).resolve()
        root = fixture_dir().resolve()
        if not str(path).startswith(str(root)):
            raise ExecutionValidationError("fixture input_ref escapes the fixture dir")
        if not path.is_file():
            raise ExecutionValidationError(f"fixture not found: {name}")
        return ResolvedInputRef(kind="fixture", location=str(path))

    if input_ref.startswith(ARTIFACT_PREFIX):
        key = input_ref[len(ARTIFACT_PREFIX):]
        allowed_prefix = f"missions/{mission_id}/"
        if not key.startswith(allowed_prefix) or ".." in key:
            raise ExecutionValidationError(
                "artifact input_ref must reference an artifact belonging to "
                "this mission (missions/{mission_id}/...)"
            )
        return ResolvedInputRef(kind="artifact", location=key)

    if input_ref.startswith(("http://", "https://", "ftp://")):
        # Remote fetches are gated by app.security.remote_urls; Phase M does
        # not download STAC assets yet — reject early with an explicit error.
        from app.security.remote_urls import RemoteUrlError, assert_remote_url_allowed

        try:
            assert_remote_url_allowed(input_ref)
        except RemoteUrlError as exc:
            raise ExecutionValidationError(str(exc)) from exc
        raise ExecutionValidationError(
            "Remote URL input_refs are not enabled; use fixture: or artifact:"
        )

    raise ExecutionValidationError(
        "input_ref must start with 'fixture:' (allowlisted fixture directory) "
        "or 'artifact:' (an artifact of this mission)"
    )
