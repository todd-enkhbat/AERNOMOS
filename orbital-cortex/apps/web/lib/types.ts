import type { components } from "@/lib/generated/api-types";

type Schemas = components["schemas"];

export type JobStatus = Schemas["Job"]["status"];
export type JobType = Schemas["Job"]["job_type"];
export type Sensor = Schemas["Job"]["sensor"];
export type Priority = Schemas["Job"]["priority"];
export type ComputePreference = Schemas["Job"]["compute_preference"];

export type AreaOfInterest = Schemas["AreaOfInterest"];
export type JobCreatePayload = Schemas["JobCreate"];
export type Job = Schemas["Job"];
export type ComputeNode = Schemas["ComputeNode"];
export type GroundStation = Schemas["GroundStation"];
export type Satellite = Schemas["Satellite"];
export type ContactWindow = Schemas["ContactWindow"];
export type HardConstraintFailure = Schemas["HardConstraintFailure"];
export type CandidateScore = Schemas["CandidateScore"];
export type RoutingDecision = Schemas["RoutingDecision"];
export type JobEvent = Schemas["JobEvent"];
export type Result = Omit<Schemas["Result"], "geojson"> & {
  geojson: {
    type: string;
    features: GeoJsonFeature[];
  };
};
export type ArtifactRef = Schemas["ArtifactRef"];
export type JobCreateResponse = Schemas["JobCreateResponse"];
export type JobsListResponse = Schemas["JobsListResponse"];
export type JobDetailResponse = Schemas["JobDetailResponse"];
export type RoutingResponse = Schemas["RoutingResponse"];
export type EventsResponse = Schemas["JobEventsResponse"];
export type ResultResponse = Omit<Schemas["ResultResponse"], "result"> & {
  result: Result;
};
export type SimulateRunResponse = Omit<Schemas["SimulateRunResponse"], "result"> & {
  result?: Result | null;
};
export type ReplayResponse = Schemas["ReplayResponse"];
export type NodesResponse = Schemas["NodesResponse"];
export type GroundStationsResponse = Schemas["GroundStationsResponse"];
export type SatellitesResponse = Schemas["SatellitesResponse"];
export type ContactWindowsResponse = Schemas["ContactWindowsResponse"];
export type SceneResponse = Schemas["SceneResponse"];

export interface SceneRecord {
  id: string;
  job_id: string;
  sensor: string;
  mode: string;
  resolution_m: number;
  captured_utc: string;
  stac_item_id: string | null;
  provenance: string;
}

export interface GeoJsonFeature {
  type: "Feature";
  geometry: {
    type: "Point";
    coordinates: number[];
  };
  properties: Record<string, string | number | boolean | null>;
}

export interface DetectionsGeoJson {
  type: string;
  features: GeoJsonFeature[];
}
