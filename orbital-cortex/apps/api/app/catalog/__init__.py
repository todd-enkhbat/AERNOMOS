"""Public satellite catalog discovery (STAC providers)."""

from __future__ import annotations

from app.catalog.base import DataCatalogProvider
from app.catalog.errors import (
    CatalogNotFoundError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.catalog.fixture_provider import FixtureCatalogProvider
from app.catalog.planetary_computer import (
    PROVIDER_ID as PLANETARY_COMPUTER_PROVIDER_ID,
)
from app.catalog.planetary_computer import (
    PlanetaryComputerCatalog,
)
from app.catalog.types import CatalogAsset, CatalogItem, CatalogSearchQuery

__all__ = [
    "CatalogAsset",
    "CatalogItem",
    "CatalogNotFoundError",
    "CatalogRateLimitedError",
    "CatalogSearchQuery",
    "CatalogUnavailableError",
    "DataCatalogProvider",
    "FixtureCatalogProvider",
    "PLANETARY_COMPUTER_PROVIDER_ID",
    "PlanetaryComputerCatalog",
]
