import type {
  ContactWindowsResponse,
  DetectionsGeoJson,
  EventsResponse,
  GroundStationsResponse,
  JobCreatePayload,
  JobCreateResponse,
  JobDetailResponse,
  JobsListResponse,
  NodesResponse,
  ReplayResponse,
  ResultResponse,
  RoutingResponse,
  SatellitesResponse,
  SceneResponse,
  SimulateRunResponse
} from "@/lib/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

/** Same-origin proxy path for cookie-authenticated mission APIs. */
export const MISSION_API_BASE =
  typeof window === "undefined"
    ? API_BASE_URL
    : process.env.NEXT_PUBLIC_MISSION_API_BASE ?? "/api/oc";


export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function apiErrorMessage(
  error: unknown,
  fallback = "The public API is temporarily unavailable. You can still explore the interface and documentation."
): string {
  if (!(error instanceof Error) || error.message === "Failed to fetch") {
    return fallback;
  }
  return error.message;
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  baseUrl: string = API_BASE_URL
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = data?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "request_failed",
      error?.message ?? `Request failed with status ${response.status}`
    );
  }
  return data as T;
}

async function missionRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  return request<T>(
    path,
    {
      ...init,
      credentials: "include"
    },
    MISSION_API_BASE
  );
}


export function getGroundStations(): Promise<GroundStationsResponse> {
  return request<GroundStationsResponse>("/v1/ground-stations");
}

export function getSatellites(): Promise<SatellitesResponse> {
  return request<SatellitesResponse>("/v1/satellites");
}

export function getContactWindows(params?: {
  upcoming?: boolean;
  limit?: number;
}): Promise<ContactWindowsResponse> {
  const search = new URLSearchParams();
  if (params?.upcoming) {
    search.set("upcoming", "true");
  }
  if (params?.limit) {
    search.set("limit", String(params.limit));
  }
  const query = search.toString();
  return request<ContactWindowsResponse>(
    `/v1/contact-windows${query ? `?${query}` : ""}`
  );
}

export function getNodes(): Promise<NodesResponse> {
  return request<NodesResponse>("/v1/nodes");
}

export function listJobs(): Promise<JobsListResponse> {
  return request<JobsListResponse>("/v1/jobs");
}

export function createJob(
  payload: JobCreatePayload,
  apiKey: string
): Promise<JobCreateResponse> {
  return request<JobCreateResponse>("/v1/jobs", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify(payload)
  });
}

export function getJob(jobId: string): Promise<JobDetailResponse> {
  return request<JobDetailResponse>(`/v1/jobs/${jobId}`);
}

export function getEvents(jobId: string): Promise<EventsResponse> {
  return request<EventsResponse>(`/v1/jobs/${jobId}/events`);
}

export function getRouting(jobId: string): Promise<RoutingResponse> {
  return request<RoutingResponse>(`/v1/jobs/${jobId}/routing`);
}

export function replayRouting(jobId: string): Promise<ReplayResponse> {
  return request<ReplayResponse>(`/v1/jobs/${jobId}/replay`, { method: "POST" });
}

export function getDetections(jobId: string): Promise<DetectionsGeoJson> {
  return request<DetectionsGeoJson>(`/v1/jobs/${jobId}/detections`, {
    headers: { Accept: "application/geo+json" }
  });
}

export function getScene(jobId: string): Promise<SceneResponse> {
  return request<SceneResponse>(`/v1/jobs/${jobId}/scene`);
}

export function getResult(jobId: string): Promise<ResultResponse> {
  return request<ResultResponse>(`/v1/jobs/${jobId}/result`);
}

export function runSimulation(jobId: string): Promise<SimulateRunResponse> {
  return request<SimulateRunResponse>(`/v1/simulate/run/${jobId}`, {
    method: "POST"
  });
}

export type MissionSummary =
  import("@/lib/generated/api-types").components["schemas"]["MissionOut"];

export type SessionResponse = {
  session: {
    id: string;
    created_at: string;
    last_seen_at: string;
    expires_at: string;
  };
  created: boolean;
};

export type MissionsListResponse = { missions: MissionSummary[] };
export type MissionResponse = { mission: MissionSummary };
export type ShareLinkResponse = {
  share_link: {
    id: string;
    mission_id: string;
    token?: string;
    expires_at?: string | null;
    revoked_at?: string | null;
    permissions: string[];
  };
};

export function ensureAnonymousSession(): Promise<SessionResponse> {
  return missionRequest<SessionResponse>("/v1/sessions", { method: "POST" });
}

export function listMissions(): Promise<MissionsListResponse> {
  return missionRequest<MissionsListResponse>("/v1/missions");
}

export function listExampleMissions(): Promise<MissionsListResponse> {
  return missionRequest<MissionsListResponse>("/v1/missions/examples");
}

export type MissionCreatePayload = {
  title: string;
  objective_type: string;
  area_of_interest: Record<string, unknown>;
  status?: string;
  start_time?: string;
  end_time?: string;
  deadline?: string;
  max_cost_usd?: number;
  max_data_volume_mb?: number;
  preferred_compute_location?: string;
  allowed_regions?: unknown[];
  data_source_preference?: unknown[];
  customer_systems?: unknown[];
  notes?: string;
  organization_name?: string;
  use_case?: string;
  max_age_days?: number;
  onboard_processing?: string;
  data_residency?: string;
};

export function createMission(payload: MissionCreatePayload): Promise<MissionResponse> {
  return missionRequest<MissionResponse>("/v1/missions", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMission(
  missionId: string,
  shareToken?: string
): Promise<MissionResponse> {
  const headers: HeadersInit = {};
  if (shareToken) {
    headers["X-Nomos-Share-Token"] = shareToken;
  }
  return missionRequest<MissionResponse>(`/v1/missions/${missionId}`, { headers });
}

export function createShareLink(missionId: string): Promise<ShareLinkResponse> {
  return missionRequest<ShareLinkResponse>(`/v1/missions/${missionId}/share-links`, {
    method: "POST",
    body: JSON.stringify({ permissions: ["read"] })
  });
}

export type CatalogCandidate = {
  id: string;
  mission_id: string;
  source_provider: string;
  collection: string;
  external_item_id: string;
  acquisition_time: ProvenancedField<string>;
  footprint: Record<string, unknown>;
  available_assets: Array<{
    key?: string | null;
    media_type?: string | null;
    roles: string[];
    title?: string | null;
  }>;
  estimated_size_bytes?: ProvenancedField<number> | null;
  source_url?: string | null;
  source_timestamp: string;
  truth_status: string;
  created_at: string;
};

export type ProvenancedField<T = unknown> = {
  value: T;
  truth_status: string;
  source?: string | null;
  retrieved_at?: string | null;
  effective_at?: string | null;
  method?: string | null;
  explanation?: string | null;
  freshness?: string | null;
};

export type MissionInfrastructureResponse = import("@/lib/generated/api-types").components["schemas"]["MissionInfrastructureResponse"];

export type CatalogCandidatesResponse = { candidates: CatalogCandidate[] };

export function discoverMissionCatalog(
  missionId: string,
  payload: {
    start_time?: string;
    end_time?: string;
    collections?: string[];
    limit?: number;
  } = {}
): Promise<CatalogCandidatesResponse> {
  return missionRequest<CatalogCandidatesResponse>(
    `/v1/missions/${missionId}/discover`,
    {
      method: "POST",
      body: JSON.stringify(payload)
    }
  );
}

export function listMissionCandidates(
  missionId: string,
  shareToken?: string
): Promise<CatalogCandidatesResponse> {
  const headers: HeadersInit = {};
  if (shareToken) {
    headers["X-Nomos-Share-Token"] = shareToken;
  }
  return missionRequest<CatalogCandidatesResponse>(
    `/v1/missions/${missionId}/candidates`,
    { headers }
  );
}

export function getMissionInfrastructure(
  missionId: string,
  shareToken?: string
): Promise<MissionInfrastructureResponse> {
  const headers: HeadersInit = {};
  if (shareToken) {
    headers["X-Nomos-Share-Token"] = shareToken;
  }
  return missionRequest<MissionInfrastructureResponse>(
    `/v1/missions/${missionId}/infrastructure`,
    { headers }
  );
}

export type MissionPlanStep = {
  id: string;
  mission_plan_id: string;
  sequence: number;
  step_type: string;
  provider_name: string;
  resource_id?: string | null;
  title: string;
  description: string;
  start_time?: string | null;
  end_time?: string | null;
  duration_seconds?: number | null;
  estimated_cost_usd?: number | null;
  input_artifact?: string | null;
  output_artifact?: string | null;
  truth_status: string;
  source_metadata?: Record<string, unknown>;
  feasibility_status: string;
  rejection_reason?: string | null;
};

export type SourceEvidence = {
  id: string;
  mission_id: string;
  mission_plan_id?: string | null;
  mission_plan_step_id?: string | null;
  source_name: string;
  source_type: string;
  source_url?: string | null;
  retrieved_at?: string | null;
  effective_at?: string | null;
  raw_value?: Record<string, unknown>;
  transformed_value?: Record<string, unknown>;
  transformation_method?: string | null;
  truth_status: string;
};

export type PlanEstimate = {
  value?: number | null;
  truth_status?: string;
  method?: string | null;
};

export type MissionPlan = {
  id: string;
  mission_id: string;
  version: number;
  recommended: boolean;
  status: string;
  summary: string;
  estimated_total_time_seconds?: number | null;
  estimated_total_cost_usd?: number | null;
  confidence?: number | null;
  assumptions?: unknown[];
  created_at?: string | null;
  pattern?: string | null;
  plan_hash?: string | null;
  feasibility_status?: string | null;
  explanation?: {
    why_recommended?: string;
    executable_now?: string[];
    needs_provider?: string[];
    top_assumptions?: string[];
    missing_integrations?: string[];
    rejection_reasons?: Array<{ code?: string; message?: string }>;
  } | null;
  estimates?: {
    duration?: PlanEstimate;
    data_movement_mb?: PlanEstimate;
    cost_usd?: PlanEstimate;
  } | null;
  score?: number | null;
  planner_config_version?: string | null;
  input_hash?: string | null;
  steps?: MissionPlanStep[] | null;
  evidence?: SourceEvidence[] | null;
};

export type MissionPlansGenerateResponse = {
  plans: MissionPlan[];
  recommended_plan_id?: string | null;
  planner_config_version: string;
  generation_strategy: string;
};

export function generateMissionPlans(
  missionId: string
): Promise<MissionPlansGenerateResponse> {
  return missionRequest<MissionPlansGenerateResponse>(
    `/v1/missions/${missionId}/plans`,
    { method: "POST", body: "{}" }
  );
}

export function listMissionPlans(
  missionId: string,
  shareToken?: string
): Promise<{ plans: MissionPlan[]; generation_strategy: string }> {
  const headers: HeadersInit = {};
  if (shareToken) {
    headers["X-Nomos-Share-Token"] = shareToken;
  }
  return missionRequest(`/v1/missions/${missionId}/plans`, { headers });
}

export function getMissionPlan(
  missionId: string,
  planId: string,
  shareToken?: string
): Promise<{ plan: MissionPlan }> {
  const headers: HeadersInit = {};
  if (shareToken) {
    headers["X-Nomos-Share-Token"] = shareToken;
  }
  return missionRequest<{ plan: MissionPlan }>(
    `/v1/missions/${missionId}/plans/${planId}`,
    { headers }
  );
}

