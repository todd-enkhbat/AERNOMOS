"""Optional live Planetary Computer STAC search (env-gated).

Skip unless RUN_LIVE_STAC=1. Requires network access to
https://planetarycomputer.microsoft.com/api/stac/v1
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from app.catalog.planetary_computer import PlanetaryComputerCatalog
from app.catalog.types import CatalogSearchQuery

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_STAC") != "1",
    reason="Set RUN_LIVE_STAC=1 to hit live Planetary Computer STAC",
)

# New York Harbor bbox from the phase prompt.
NY_HARBOR_BBOX = (-74.3, 40.3, -73.5, 41.0)


def test_live_sentinel1_ny_harbor_returns_real_items():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=45)
    catalog = PlanetaryComputerCatalog(use_cache=False, timeout_seconds=60.0)
    items = catalog.search(
        CatalogSearchQuery(
            collections=["sentinel-1-grd"],
            bbox=NY_HARBOR_BBOX,
            start=start,
            end=end,
            limit=5,
        )
    )
    assert len(items) >= 1
    first = items[0]
    assert first.external_item_id
    assert first.collection == "sentinel-1-grd"
    assert first.source_provider == "microsoft-planetary-computer"
    assert first.footprint.get("type") in {"Polygon", "MultiPolygon"}
    assert first.acquisition_time is not None
    assert first.source_url
