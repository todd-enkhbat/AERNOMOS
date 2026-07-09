import type { NodesResponse } from "@/lib/types";

export const EMPTY_NODES: NodesResponse = {
  compute_nodes: [],
  ground_stations: []
};

/**
 * Shared demo credential for the open public demo. The API does not enforce
 * auth yet (Phase C); job creation is protected by per-IP rate limiting
 * server-side instead.
 */
export const DEMO_API_KEY = "oc_demo_public";
