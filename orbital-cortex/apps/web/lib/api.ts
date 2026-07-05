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

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
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
