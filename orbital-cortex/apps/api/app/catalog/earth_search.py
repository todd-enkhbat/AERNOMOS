"""Earth Search (Element84) adapter stub.

Registered behind DataCatalogProvider for a future second source.
Not used by discover in Phase F — Planetary Computer is the live provider.
"""

from __future__ import annotations

from typing import List

from app.catalog.errors import CatalogUnavailableError
from app.catalog.types import CatalogAsset, CatalogItem, CatalogSearchQuery

PROVIDER_ID = "earth-search-element84"
STAC_API_URL = "https://earth-search.aws.element84.com/v1"


class EarthSearchCatalog:
    """Placeholder second STAC provider (unused in Phase F)."""

    provider_id = PROVIDER_ID

    def search(self, query: CatalogSearchQuery) -> List[CatalogItem]:
        raise CatalogUnavailableError(
            "Earth Search provider is registered but not enabled in Phase F."
        )

    def get_item(self, collection: str, external_item_id: str) -> CatalogItem:
        raise CatalogUnavailableError(
            "Earth Search provider is registered but not enabled in Phase F."
        )

    def get_assets(
        self, collection: str, external_item_id: str
    ) -> List[CatalogAsset]:
        raise CatalogUnavailableError(
            "Earth Search provider is registered but not enabled in Phase F."
        )
