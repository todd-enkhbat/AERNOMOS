"""SDK exceptions."""

from __future__ import annotations

from typing import Any, Dict, Optional


class OrbitalCortexError(Exception):
    """Base class for SDK errors."""


class APIError(OrbitalCortexError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str = "api_error",
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.response = response or {}

    def __repr__(self) -> str:
        return (
            f"APIError(status_code={self.status_code!r}, "
            f"code={self.code!r}, message={str(self)!r})"
        )


class TransportError(OrbitalCortexError):
    """Raised when the SDK cannot reach the API."""
