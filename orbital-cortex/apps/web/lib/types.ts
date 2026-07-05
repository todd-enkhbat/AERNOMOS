export type JobStatus =
  | "queued"
  | "routing"
  | "executing"
  | "downlinking"
  | "complete"
  | "failed";

export type JobType = "ship_detection" | "crop_health" | "disaster_response";

export type Sensor = "SAR" | "optical" | "hyperspectral" | "any";

export type Priority = "fastest" | "cheapest" | "most_reliable";

export type ComputePreference =
  | "orbital_if_available"
  | "ground_only"
  | "cheapest"
  | "fastest";

export interface AreaOfInterest {
  type: string;
  coordinates: number[];
}

export interface JobCreatePayload {
  job_type: JobType;
  area_of_interest: AreaOfInterest;
  sensor: Sensor;
  priority: Priority;
  compute_preference: ComputePreference;
  max_cost_usd: number;
}

export interface Job {
  id: string;
  job_type: JobType;
  area_of_interest: AreaOfInterest;
  sensor: Sensor;
  priority: Priority;
  compute_preference: ComputePreference;
  max_cost_usd: number;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  selected_route_id: string | null;
}

export interface ComputeNode {
  id: string;
  name: string;
  type: "orbital" | "ground_cloud" | "ground_station";
  location: string;
  orbit: string | null;
  gpu_class: string;
  supported_models: string[];
  storage_gb: number;
  downlink_mbps: number;
  power_state: string;
  availability: number;
  compliance_tags: string[];
  base_cost_usd: number;
  latency_minutes: number;
  satellite_id: string | null;
}

export interface GroundStation {
  id: string;
  name: string;
  location: string;
  provider: string;
  latitude: number;
  longitude: number;
  altitude_m: number;
  min_elevation_deg: number;
  latency_minutes: number;
  downlink_mbps: number;
  availability: number;
}

export interface NodesResponse {
  compute_nodes: ComputeNode[];
  ground_stations: GroundStation[];
}

export interface HardConstraintFailure {
  constraint: string;
  detail: string;
}

export interface CandidateScore {
  node_id: string;
  score: number;
  eligible: boolean;
  hard_constraint_failures?: HardConstraintFailure[];
  binding_constraint?: string | null;
  weights?: Record<string, number>;
  model_support_score: number;
  latency_score: number;
  cost_score: number;
  availability_score: number;
  contact_score: number;
  preference_score: number;
  compliance_score: number;
  estimated_latency_minutes: number;
  estimated_cost_usd: number;
  available: boolean;
  selected_ground_station_id?: string | null;
  next_contact_minutes?: number | null;
  next_aos_utc?: string | null;
  next_max_elevation_deg?: number | null;
  est_downlink_mb?: number | null;
  reasons: string[];
}

export interface RoutingDecision {
  id: string;
  job_id: string;
  selected_node_id: string;
  selected_ground_station_id: string | null;
  fallback_node_id: string | null;
  estimated_latency_minutes: number;
  estimated_cost_usd: number;
  confidence: number;
  config_version?: string | null;
  input_hash?: string | null;
  decision_hash?: string | null;
  tle_snapshot_id?: string | null;
  seed?: number | null;
  decided_at_utc?: string | null;
  reasons: string[];
  candidate_scores: CandidateScore[];
}

export interface JobEvent {
  id: string;
  job_id: string;
  event_type: string;
  message: string;
  payload: Record<string, unknown>;
  ts_utc: string;
}

export interface Result {
  id: string;
  job_id: string;
  summary: string;
  confidence: number;
  geojson: {
    type: string;
    features: Array<{
      type: string;
      geometry: {
        type: string;
        coordinates?: unknown;
      };
      properties: Record<string, string | number | boolean | null>;
    }>;
  };
  output_files: string[];
}

export interface JobCreateResponse {
  job: Job;
  routing_decision: RoutingDecision | null;
}

export interface JobsListResponse {
  jobs: Job[];
}

export interface JobDetailResponse {
  job: Job;
  routing_decision: RoutingDecision | null;
  result_summary: string | null;
}

export interface RoutingResponse {
  routing_decision: RoutingDecision;
}

export interface EventsResponse {
  events: JobEvent[];
}

export interface ResultResponse {
  result: Result;
}

export interface SimulateRunResponse {
  job: Job;
  events_created: number;
  result: Result;
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

export interface SceneResponse {
  scene: SceneRecord | null;
}

export interface ReplayResponse {
  match: boolean;
  stored_decision_hash: string;
  replay_decision_hash: string;
  config_version: string;
  input_hash: string;
}
