"""Real CPU task implementations: crop_geotiff (rasterio) and thumbnail (Pillow).

Each task reads a staged input file and writes a real output file. Failures
raise ExecutionError with a human-readable message; nothing is fabricated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

from app.execution.types import (
    TASK_CROP_GEOTIFF,
    TASK_THUMBNAIL,
    ExecutionError,
    ExecutionValidationError,
)

DEFAULT_THUMBNAIL_MAX_SIZE = 256


def run_task(task_type: str, input_path: Path, output_path: Path, params: Dict[str, Any]) -> None:
    """Dispatch to the concrete task. output_path is created on success only."""
    if task_type == TASK_CROP_GEOTIFF:
        crop_geotiff(input_path, output_path, params)
    elif task_type == TASK_THUMBNAIL:
        thumbnail(input_path, output_path, params)
    else:
        raise ExecutionValidationError(f"Unsupported task_type: {task_type}")


def output_filename(task_type: str) -> str:
    if task_type == TASK_CROP_GEOTIFF:
        return "crop.tif"
    if task_type == TASK_THUMBNAIL:
        return "thumbnail.png"
    raise ExecutionValidationError(f"Unsupported task_type: {task_type}")


def _parse_bounds(params: Dict[str, Any]) -> Tuple[float, float, float, float]:
    bounds = params.get("bounds")
    if (
        not isinstance(bounds, (list, tuple))
        or len(bounds) != 4
        or not all(isinstance(v, (int, float)) for v in bounds)
    ):
        raise ExecutionValidationError(
            "crop_geotiff requires params.bounds = [minx, miny, maxx, maxy]"
        )
    minx, miny, maxx, maxy = (float(v) for v in bounds)
    if minx >= maxx or miny >= maxy:
        raise ExecutionValidationError(
            "crop_geotiff bounds must satisfy minx < maxx and miny < maxy"
        )
    return minx, miny, maxx, maxy


def crop_geotiff(input_path: Path, output_path: Path, params: Dict[str, Any]) -> None:
    """Crop a GeoTIFF to the given geographic bounds with rasterio."""
    import rasterio
    from rasterio.errors import RasterioIOError
    from rasterio.windows import from_bounds

    minx, miny, maxx, maxy = _parse_bounds(params)

    try:
        with rasterio.open(input_path) as src:
            window = from_bounds(minx, miny, maxx, maxy, transform=src.transform)
            window = window.round_lengths().round_offsets()
            full = rasterio.windows.Window(0, 0, src.width, src.height)
            window = window.intersection(full)
            if window.width < 1 or window.height < 1:
                raise ExecutionError(
                    "Crop bounds do not intersect the raster extent "
                    f"(raster bounds: {tuple(src.bounds)})"
                )
            data = src.read(window=window)
            profile = src.profile.copy()
            profile.update(
                width=int(window.width),
                height=int(window.height),
                transform=src.window_transform(window),
                driver="GTiff",
            )
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(data)
    except ExecutionError:
        raise
    except RasterioIOError as exc:
        raise ExecutionError(f"Input is not a readable GeoTIFF: {exc}") from exc
    except Exception as exc:  # malformed rasters can fail in many layers
        raise ExecutionError(f"crop_geotiff failed: {exc}") from exc


def thumbnail(input_path: Path, output_path: Path, params: Dict[str, Any]) -> None:
    """Render a PNG thumbnail from a raster (typically the crop output)."""
    import rasterio
    from PIL import Image
    from rasterio.errors import RasterioIOError

    max_size = params.get("max_size", DEFAULT_THUMBNAIL_MAX_SIZE)
    if not isinstance(max_size, int) or not (16 <= max_size <= 2048):
        raise ExecutionValidationError(
            "thumbnail params.max_size must be an integer between 16 and 2048"
        )

    try:
        with rasterio.open(input_path) as src:
            band_count = min(src.count, 3)
            data = src.read(list(range(1, band_count + 1))).astype("float64")
    except RasterioIOError as exc:
        raise ExecutionError(f"Input is not a readable raster: {exc}") from exc
    except Exception as exc:
        raise ExecutionError(f"thumbnail failed reading raster: {exc}") from exc

    try:
        # Per-band min/max stretch to uint8 for display.
        stretched = np.zeros_like(data, dtype="uint8")
        for i in range(data.shape[0]):
            band = data[i]
            finite = band[np.isfinite(band)]
            if finite.size == 0:
                continue
            lo, hi = float(finite.min()), float(finite.max())
            if hi > lo:
                stretched[i] = np.clip((band - lo) / (hi - lo) * 255.0, 0, 255).astype(
                    "uint8"
                )
        if stretched.shape[0] == 1:
            image = Image.fromarray(stretched[0], mode="L")
        else:
            if stretched.shape[0] == 2:
                stretched = np.concatenate([stretched, stretched[:1]], axis=0)
            image = Image.fromarray(np.moveaxis(stretched, 0, -1), mode="RGB")
        image.thumbnail((max_size, max_size))
        image.save(output_path, format="PNG")
    except ExecutionError:
        raise
    except Exception as exc:
        raise ExecutionError(f"thumbnail failed rendering PNG: {exc}") from exc
