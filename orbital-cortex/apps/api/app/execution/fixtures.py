"""Ensure allowlisted execution fixture rasters exist on disk (Phase M).

The CPU demo uses `fixture:sample.tif`. `var/` is gitignored, so we write a
small real GeoTIFF at seed/startup rather than committing binary assets.
"""

from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings

# Stable inner crop used by tests and the web demo when mission AOI parsing fails.
DEMO_CROP_BOUNDS = [-74.1, 40.5, -73.7, 40.8]

SAMPLE_FIXTURE_NAME = "sample.tif"


def fixture_dir() -> Path:
    return Path(get_settings().execution_fixture_dir)


def sample_fixture_path() -> Path:
    return fixture_dir() / SAMPLE_FIXTURE_NAME


def ensure_execution_fixtures() -> Path:
    """Write sample.tif when missing. Idempotent."""
    path = sample_fixture_path()
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_sample_geotiff(path)
    return path


def _write_sample_geotiff(path: Path) -> None:
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds

    # NY harbor extent — matches default mission builder AOI and test fixtures.
    west, south, east, north = -74.3, 40.3, -73.5, 41.0
    width = height = 96
    transform = from_bounds(west, south, east, north, width, height)
    data = (
        np.linspace(0, 255, width * height).reshape(height, width).astype("uint8")
    )
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)
