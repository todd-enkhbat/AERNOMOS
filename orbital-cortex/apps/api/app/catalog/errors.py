"""Catalog provider errors — never invent items to hide these."""

from __future__ import annotations


class CatalogError(Exception):
    """Base catalog error."""

    code: str = "catalog_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CatalogUnavailableError(CatalogError):
    """Upstream STAC API unreachable, timed out, or returned 5xx."""

    code = "catalog_unavailable"


class CatalogRateLimitedError(CatalogError):
    """Upstream STAC API rate-limited the request."""

    code = "catalog_rate_limited"


class CatalogNotFoundError(CatalogError):
    """Requested collection or item was not found upstream."""

    code = "catalog_not_found"
