"""Nomos Orbital Python SDK."""

from orbitalcortex.client import Client
from orbitalcortex.exceptions import (
    APIError,
    ExpiredShareLink,
    InvalidGeographicInput,
    JobTimeoutError,
    MissionValidationError,
    NoCatalogData,
    NoFeasiblePlan,
    NomosError,
    OrbitalCortexError,
    StaleOrbitalData,
    TransportError,
    UnauthorizedMission,
    UpstreamProviderUnavailable,
)

__all__ = [
    "APIError",
    "AsyncClient",
    "Client",
    "ExpiredShareLink",
    "InvalidGeographicInput",
    "JobTimeoutError",
    "MissionValidationError",
    "NoCatalogData",
    "NoFeasiblePlan",
    "NomosError",
    "OrbitalCortexError",
    "StaleOrbitalData",
    "TransportError",
    "UnauthorizedMission",
    "UpstreamProviderUnavailable",
    "__version__",
]
__version__ = "0.3.0"


def __getattr__(name: str):  # lazy: AsyncClient needs the optional httpx extra
    if name == "AsyncClient":
        from orbitalcortex.async_client import AsyncClient

        return AsyncClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
