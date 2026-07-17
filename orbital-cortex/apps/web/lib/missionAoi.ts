/** Crop bounds for the CPU demo fixture (sample.tif covers NY harbor). */

export const DEMO_FIXTURE_CROP_BOUNDS: [number, number, number, number] = [
  -74.1, 40.5, -73.7, 40.8,
];

/**
 * Derive geographic bounds for crop_geotiff from a mission AOI.
 * Uses bbox coordinates when present; otherwise falls back to a stable inner
 * crop that intersects the shipped fixture raster (not the mission STAC scene).
 */
export function cropBoundsFromMissionAoi(
  areaOfInterest: Record<string, unknown> | undefined
): [number, number, number, number] {
  if (!areaOfInterest || typeof areaOfInterest !== "object") {
    return DEMO_FIXTURE_CROP_BOUNDS;
  }
  if (areaOfInterest.type === "bbox" && Array.isArray(areaOfInterest.coordinates)) {
    const coords = areaOfInterest.coordinates;
    if (
      coords.length === 4 &&
      coords.every((value) => typeof value === "number" && Number.isFinite(value))
    ) {
      const [minx, miny, maxx, maxy] = coords as [number, number, number, number];
      if (minx < maxx && miny < maxy) {
        return [minx, miny, maxx, maxy];
      }
    }
  }
  return DEMO_FIXTURE_CROP_BOUNDS;
}
