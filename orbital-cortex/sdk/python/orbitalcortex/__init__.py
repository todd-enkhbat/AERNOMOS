"""Nomos Orbital Python SDK."""

from orbitalcortex.client import Client
from orbitalcortex.exceptions import (
    APIError,
    JobTimeoutError,
    OrbitalCortexError,
    TransportError,
)

__all__ = [
    "APIError",
    "AsyncClient",
    "Client",
    "JobTimeoutError",
    "OrbitalCortexError",
    "TransportError",
    "__version__",
]
__version__ = "0.2.0"


def __getattr__(name: str):  # lazy: AsyncClient needs the optional httpx extra
    if name == "AsyncClient":
        from orbitalcortex.async_client import AsyncClient

        return AsyncClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
