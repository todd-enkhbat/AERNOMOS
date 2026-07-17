"""DataCatalogProvider protocol."""

from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from app.catalog.types import CatalogAsset, CatalogItem, CatalogSearchQuery


@runtime_checkable
class DataCatalogProvider(Protocol):
    """Public satellite catalog search interface (STAC-backed)."""

    provider_id: str

    def search(self, query: CatalogSearchQuery) -> List[CatalogItem]:
        """Search for catalog items. Never fabricates results."""
        ...

    def get_item(self, collection: str, external_item_id: str) -> CatalogItem:
        """Fetch a single catalog item by collection + id."""
        ...

    def get_assets(
        self, collection: str, external_item_id: str
    ) -> List[CatalogAsset]:
        """Return assets for a catalog item."""
        ...
