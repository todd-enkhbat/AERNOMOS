"""Shared geographic validation for mission areas of interest."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple

# Reject continent-scale AOIs. ~500,000 km² is roughly Spain-sized.
MAX_AOI_AREA_KM2 = 500_000.0
# Soft floor so accidental points / tiny slivers fail clearly.
MIN_AOI_AREA_KM2 = 0.01
MAX_GEOJSON_CHARS = 200_000
MAX_RING_VERTICES = 5_000

EARTH_RADIUS_KM = 6371.0088


def _as_lon_lat(pair: Any) -> Tuple[float, float]:
    if not isinstance(pair, (list, tuple)) or len(pair) < 2:
        raise ValueError("Each coordinate must be [longitude, latitude]")
    lon = float(pair[0])
    lat = float(pair[1])
    if not math.isfinite(lon) or not math.isfinite(lat):
        raise ValueError("Coordinates must be finite WGS84 numbers")
    if lon < -180.0 or lon > 180.0:
        raise ValueError("Longitude must be between -180 and 180")
    if lat < -90.0 or lat > 90.0:
        raise ValueError("Latitude must be between -90 and 90")
    return lon, lat


def _close_ring(ring: Sequence[Sequence[float]]) -> List[Tuple[float, float]]:
    if len(ring) < 3:
        raise ValueError("Polygon ring needs at least 3 positions")
    if len(ring) > MAX_RING_VERTICES:
        raise ValueError(f"Polygon ring exceeds {MAX_RING_VERTICES} vertices")
    points = [_as_lon_lat(p) for p in ring]
    if points[0] != points[-1]:
        points.append(points[0])
    if len(points) < 4:
        raise ValueError("Closed polygon ring needs at least 4 positions")
    return points


def _ring_area_km2(ring: Sequence[Tuple[float, float]]) -> float:
    """Spherical excess area (km²) for a closed lon/lat ring."""
    if len(ring) < 4:
        return 0.0
    total = 0.0
    for i in range(len(ring) - 1):
        lon1, lat1 = ring[i]
        lon2, lat2 = ring[i + 1]
        total += math.radians(lon2 - lon1) * (
            2.0 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2))
        )
    return abs(total) * EARTH_RADIUS_KM * EARTH_RADIUS_KM / 2.0


def _polygon_area_km2(rings: Sequence[Sequence[Sequence[float]]]) -> float:
    if not rings:
        raise ValueError("Polygon coordinates are required")
    outer = _close_ring(rings[0])
    area = _ring_area_km2(outer)
    for hole in rings[1:]:
        area -= _ring_area_km2(_close_ring(hole))
    return abs(area)


def _bbox_to_polygon_coords(
    coords: Sequence[Any],
) -> List[List[List[float]]]:
    if len(coords) != 4:
        raise ValueError("bbox coordinates must be [west, south, east, north]")
    west, south, east, north = (float(c) for c in coords)
    for value, label, lo, hi in (
        (west, "west", -180.0, 180.0),
        (east, "east", -180.0, 180.0),
        (south, "south", -90.0, 90.0),
        (north, "north", -90.0, 90.0),
    ):
        if not math.isfinite(value) or value < lo or value > hi:
            raise ValueError(f"Invalid bbox {label}")
    if west >= east:
        raise ValueError("bbox west must be less than east")
    if south >= north:
        raise ValueError("bbox south must be less than north")
    return [
        [
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
        ]
    ]


def aoi_area_km2(area: Dict[str, Any]) -> float:
    geom_type = area.get("type")
    if geom_type == "bbox":
        return _polygon_area_km2(_bbox_to_polygon_coords(area.get("coordinates") or []))
    if geom_type == "Polygon":
        return _polygon_area_km2(area.get("coordinates") or [])
    if geom_type == "MultiPolygon":
        total = 0.0
        polygons = area.get("coordinates") or []
        if not polygons:
            raise ValueError("MultiPolygon coordinates are required")
        for polygon in polygons:
            total += _polygon_area_km2(polygon)
        return total
    raise ValueError(
        "area_of_interest must be GeoJSON Polygon/MultiPolygon or {type:'bbox',...}"
    )


def validate_area_of_interest(area: Any) -> Dict[str, Any]:
    """Validate AOI shape, WGS84 bounds, closure, and max area. Returns the dict."""
    if not isinstance(area, dict):
        raise ValueError("area_of_interest must be an object")

    import json

    encoded = json.dumps(area, separators=(",", ":"))
    if len(encoded) > MAX_GEOJSON_CHARS:
        raise ValueError(
            f"area_of_interest exceeds maximum size ({MAX_GEOJSON_CHARS} characters)"
        )

    geom_type = area.get("type")
    if geom_type not in ("bbox", "Polygon", "MultiPolygon"):
        raise ValueError(
            "area_of_interest must be GeoJSON Polygon/MultiPolygon or {type:'bbox',...}"
        )

    # Force ring/bbox validation side effects.
    area_km2 = aoi_area_km2(area)
    if area_km2 < MIN_AOI_AREA_KM2:
        raise ValueError(
            f"Area of interest is too small (minimum {MIN_AOI_AREA_KM2} km²)"
        )
    if area_km2 > MAX_AOI_AREA_KM2:
        raise ValueError(
            f"Area of interest is too large "
            f"(maximum {int(MAX_AOI_AREA_KM2):,} km²). "
            "Draw a smaller region or upload a tighter polygon."
        )
    return area
