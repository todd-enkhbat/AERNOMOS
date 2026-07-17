import { z } from "zod";

export const OBJECTIVE_OPTIONS = [
  {
    value: "analyze_imagery",
    label: "Analyze existing satellite imagery",
    description: "Work with scenes that already exist in public catalogs."
  },
  {
    value: "plan_data_delivery",
    label: "Plan data delivery from a satellite",
    description: "Figure out how collected data can reach the ground."
  },
  {
    value: "compare_processing",
    label: "Compare onboard, ground, edge, and cloud processing",
    description: "See where processing should happen for this mission."
  },
  {
    value: "remote_sensing_workflow",
    label: "Plan a remote-sensing workflow",
    description: "Outline an end-to-end sensing and analysis path."
  },
  {
    value: "other",
    label: "Other",
    description: "Describe a custom objective in the mission notes."
  }
] as const;

export type ObjectiveType = (typeof OBJECTIVE_OPTIONS)[number]["value"];

export const OBJECTIVE_LABELS: Record<ObjectiveType, string> = Object.fromEntries(
  OBJECTIVE_OPTIONS.map((item) => [item.value, item.label])
) as Record<ObjectiveType, string>;

export const ONBOARD_OPTIONS = [
  { value: "unnecessary", label: "Unnecessary" },
  { value: "preferred", label: "Preferred" },
  { value: "required", label: "Required" }
] as const;

export type OnboardProcessing = (typeof ONBOARD_OPTIONS)[number]["value"];

export const COMPUTE_LOCATION_OPTIONS = [
  { value: "", label: "No preference" },
  { value: "onboard", label: "On the satellite" },
  { value: "ground", label: "On the ground" },
  { value: "edge", label: "At the edge" },
  { value: "cloud", label: "In the cloud" }
] as const;

export const MISSION_MODE_OPTIONS = [
  { value: "exploratory", label: "Exploratory — still figuring out the approach" },
  { value: "active", label: "Active — ready to plan seriously" }
] as const;

export type MissionMode = (typeof MISSION_MODE_OPTIONS)[number]["value"];

/** Mirrors backend MAX_AOI_AREA_KM2 in app/core/mission_geo.py */
export const MAX_AOI_AREA_KM2 = 500_000;
export const MIN_AOI_AREA_KM2 = 0.01;
export const MAX_GEOJSON_CHARS = 200_000;

const EARTH_RADIUS_KM = 6371.0088;

export type BboxAoi = { type: "bbox"; coordinates: [number, number, number, number] };
export type PolygonAoi = {
  type: "Polygon";
  coordinates: number[][][];
};
export type AreaOfInterest = BboxAoi | PolygonAoi;

function asLonLat(pair: unknown): [number, number] {
  if (!Array.isArray(pair) || pair.length < 2) {
    throw new Error("Each coordinate must be [longitude, latitude]");
  }
  const lon = Number(pair[0]);
  const lat = Number(pair[1]);
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) {
    throw new Error("Coordinates must be finite WGS84 numbers");
  }
  if (lon < -180 || lon > 180) throw new Error("Longitude must be between -180 and 180");
  if (lat < -90 || lat > 90) throw new Error("Latitude must be between -90 and 90");
  return [lon, lat];
}

function closeRing(ring: unknown[]): [number, number][] {
  if (ring.length < 3) throw new Error("Polygon ring needs at least 3 positions");
  const points = ring.map(asLonLat);
  if (points[0][0] !== points[points.length - 1][0] || points[0][1] !== points[points.length - 1][1]) {
    points.push([...points[0]]);
  }
  if (points.length < 4) throw new Error("Closed polygon ring needs at least 4 positions");
  return points;
}

function ringAreaKm2(ring: [number, number][]): number {
  let total = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const [lon1, lat1] = ring[i];
    const [lon2, lat2] = ring[i + 1];
    total +=
      ((lon2 - lon1) * Math.PI) / 180 *
      (2 + Math.sin((lat1 * Math.PI) / 180) + Math.sin((lat2 * Math.PI) / 180));
  }
  return Math.abs((total * EARTH_RADIUS_KM * EARTH_RADIUS_KM) / 2);
}

export function aoiAreaKm2(area: AreaOfInterest): number {
  if (area.type === "bbox") {
    const [west, south, east, north] = area.coordinates;
    if (west >= east) throw new Error("West must be less than east");
    if (south >= north) throw new Error("South must be less than north");
    return ringAreaKm2([
      [west, south],
      [east, south],
      [east, north],
      [west, north],
      [west, south]
    ]);
  }
  const rings = area.coordinates;
  if (!rings?.length) throw new Error("Polygon coordinates are required");
  let areaKm2 = ringAreaKm2(closeRing(rings[0]));
  for (let i = 1; i < rings.length; i += 1) {
    areaKm2 -= ringAreaKm2(closeRing(rings[i]));
  }
  return Math.abs(areaKm2);
}

export function validateAreaOfInterest(area: unknown): AreaOfInterest {
  if (!area || typeof area !== "object") {
    throw new Error("Choose an area on the map or enter coordinates");
  }
  const encoded = JSON.stringify(area);
  if (encoded.length > MAX_GEOJSON_CHARS) {
    throw new Error("Uploaded area is too large. Use a simpler polygon.");
  }
  const typed = area as { type?: string; coordinates?: unknown };
  if (typed.type === "bbox") {
    if (!Array.isArray(typed.coordinates) || typed.coordinates.length !== 4) {
      throw new Error("Bounding box must be west, south, east, north");
    }
    const coords = typed.coordinates.map(Number) as [number, number, number, number];
    if (coords.some((n) => !Number.isFinite(n))) {
      throw new Error("Bounding box coordinates must be numbers");
    }
    const result: BboxAoi = { type: "bbox", coordinates: coords };
    const km2 = aoiAreaKm2(result);
    if (km2 < MIN_AOI_AREA_KM2) throw new Error("Area is too small");
    if (km2 > MAX_AOI_AREA_KM2) {
      throw new Error(
        `Area is too large (max ${MAX_AOI_AREA_KM2.toLocaleString()} km²). Draw a smaller region.`
      );
    }
    return result;
  }
  if (typed.type === "Polygon") {
    if (!Array.isArray(typed.coordinates) || !typed.coordinates.length) {
      throw new Error("Polygon coordinates are required");
    }
    const coordinates = (typed.coordinates as unknown[][]).map((ring) =>
      closeRing(ring as unknown[])
    );
    const result: PolygonAoi = { type: "Polygon", coordinates };
    const km2 = aoiAreaKm2(result);
    if (km2 < MIN_AOI_AREA_KM2) throw new Error("Area is too small");
    if (km2 > MAX_AOI_AREA_KM2) {
      throw new Error(
        `Area is too large (max ${MAX_AOI_AREA_KM2.toLocaleString()} km²). Draw a smaller region.`
      );
    }
    return result;
  }
  throw new Error("Area must be a bounding box or a Polygon (WGS84)");
}

export function parseGeoJsonUpload(text: string): AreaOfInterest {
  if (text.length > MAX_GEOJSON_CHARS) {
    throw new Error("File is too large. Upload a simple Polygon GeoJSON.");
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("Could not parse GeoJSON");
  }
  const obj = parsed as {
    type?: string;
    coordinates?: unknown;
    geometry?: { type?: string; coordinates?: unknown };
    features?: Array<{ geometry?: { type?: string; coordinates?: unknown } }>;
  };
  if (obj.type === "Feature" && obj.geometry) {
    return validateAreaOfInterest(obj.geometry);
  }
  if (obj.type === "FeatureCollection" && Array.isArray(obj.features) && obj.features[0]?.geometry) {
    return validateAreaOfInterest(obj.features[0].geometry);
  }
  return validateAreaOfInterest(obj);
}

export function bboxFromPolygon(area: AreaOfInterest): [number, number, number, number] {
  if (area.type === "bbox") return area.coordinates;
  let west = Infinity;
  let south = Infinity;
  let east = -Infinity;
  let north = -Infinity;
  for (const ring of area.coordinates) {
    for (const [lon, lat] of ring) {
      west = Math.min(west, lon);
      south = Math.min(south, lat);
      east = Math.max(east, lon);
      north = Math.max(north, lat);
    }
  }
  return [west, south, east, north];
}

export type MissionBuilderState = {
  step: number;
  objectiveType: ObjectiveType | "";
  areaOfInterest: AreaOfInterest | null;
  west: string;
  south: string;
  east: string;
  north: string;
  startDate: string;
  endDate: string;
  maxAgeDays: string;
  sensorPreference: string;
  deadline: string;
  maxCostUsd: string;
  maxDataVolumeMb: string;
  preferredComputeLocation: string;
  allowedRegions: string;
  dataResidency: string;
  cloudProvider: string;
  onboardProcessing: OnboardProcessing;
  title: string;
  organizationName: string;
  useCase: string;
  notes: string;
  missionMode: MissionMode;
};

export const initialMissionBuilderState: MissionBuilderState = {
  step: 1,
  objectiveType: "",
  areaOfInterest: null,
  west: "-74.3",
  south: "40.3",
  east: "-73.5",
  north: "41.0",
  startDate: "",
  endDate: "",
  maxAgeDays: "",
  sensorPreference: "",
  deadline: "",
  maxCostUsd: "",
  maxDataVolumeMb: "",
  preferredComputeLocation: "",
  allowedRegions: "",
  dataResidency: "",
  cloudProvider: "",
  onboardProcessing: "unnecessary",
  title: "",
  organizationName: "",
  useCase: "",
  notes: "",
  missionMode: "exploratory"
};

export type MissionBuilderAction =
  | { type: "set"; field: keyof MissionBuilderState; value: MissionBuilderState[keyof MissionBuilderState] }
  | { type: "patch"; patch: Partial<MissionBuilderState> }
  | { type: "setStep"; step: number }
  | { type: "setArea"; area: AreaOfInterest | null };

export function missionBuilderReducer(
  state: MissionBuilderState,
  action: MissionBuilderAction
): MissionBuilderState {
  switch (action.type) {
    case "set":
      return { ...state, [action.field]: action.value };
    case "patch":
      return { ...state, ...action.patch };
    case "setStep":
      return { ...state, step: action.step };
    case "setArea":
      return { ...state, areaOfInterest: action.area };
    default:
      return state;
  }
}

const objectiveSchema = z.enum([
  "analyze_imagery",
  "plan_data_delivery",
  "compare_processing",
  "remote_sensing_workflow",
  "other"
]);

export function validateStep(step: number, state: MissionBuilderState): string | null {
  if (step === 1) {
    const parsed = objectiveSchema.safeParse(state.objectiveType);
    if (!parsed.success) return "Choose an objective to continue.";
    return null;
  }
  if (step === 2) {
    try {
      const area = state.areaOfInterest ?? areaFromBboxFields(state);
      validateAreaOfInterest(area);
    } catch (error) {
      return error instanceof Error ? error.message : "Area of interest is invalid.";
    }
    if (state.startDate && state.endDate && state.startDate > state.endDate) {
      return "Start date must be on or before the end date.";
    }
    if (state.maxAgeDays) {
      const days = Number(state.maxAgeDays);
      if (!Number.isInteger(days) || days < 1 || days > 3650) {
        return "Data freshness must be between 1 and 3650 days.";
      }
    }
    return null;
  }
  if (step === 3) {
    if (state.maxCostUsd) {
      const cost = Number(state.maxCostUsd);
      if (!Number.isFinite(cost) || cost < 0) return "Max cost must be a non-negative number.";
    }
    if (state.maxDataVolumeMb) {
      const volume = Number(state.maxDataVolumeMb);
      if (!Number.isFinite(volume) || volume < 0) {
        return "Max data volume must be a non-negative number.";
      }
    }
    return null;
  }
  if (step === 4) {
    if (!state.title.trim()) return "Give this mission a title.";
    if (state.title.trim().length > 256) return "Title must be 256 characters or fewer.";
    return null;
  }
  return null;
}

export function areaFromBboxFields(state: MissionBuilderState): BboxAoi {
  return {
    type: "bbox",
    coordinates: [
      Number(state.west),
      Number(state.south),
      Number(state.east),
      Number(state.north)
    ]
  };
}

function toIsoDateStart(date: string): string | undefined {
  if (!date) return undefined;
  return `${date}T00:00:00.000Z`;
}

function toIsoDateEnd(date: string): string | undefined {
  if (!date) return undefined;
  return `${date}T23:59:59.000Z`;
}

function splitCsv(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function buildMissionCreatePayload(state: MissionBuilderState) {
  const area = validateAreaOfInterest(state.areaOfInterest ?? areaFromBboxFields(state));
  const customerSystems: Array<Record<string, unknown>> = [];
  if (state.cloudProvider.trim()) {
    customerSystems.push({
      kind: "cloud_provider",
      provider: state.cloudProvider.trim()
    });
  }

  return {
    title: state.title.trim(),
    objective_type: state.objectiveType as ObjectiveType,
    area_of_interest: area,
    status: state.missionMode,
    start_time: toIsoDateStart(state.startDate),
    end_time: toIsoDateEnd(state.endDate),
    deadline: state.deadline ? `${state.deadline}T23:59:59.000Z` : undefined,
    max_cost_usd: state.maxCostUsd ? Number(state.maxCostUsd) : undefined,
    max_data_volume_mb: state.maxDataVolumeMb ? Number(state.maxDataVolumeMb) : undefined,
    preferred_compute_location: state.preferredComputeLocation || undefined,
    allowed_regions: splitCsv(state.allowedRegions),
    data_source_preference: state.sensorPreference.trim()
      ? [state.sensorPreference.trim()]
      : [],
    customer_systems: customerSystems,
    notes: state.notes.trim() || undefined,
    organization_name: state.organizationName.trim() || undefined,
    use_case: state.useCase.trim() || undefined,
    max_age_days: state.maxAgeDays ? Number(state.maxAgeDays) : undefined,
    onboard_processing: state.onboardProcessing,
    data_residency: state.dataResidency.trim() || undefined
  };
}
