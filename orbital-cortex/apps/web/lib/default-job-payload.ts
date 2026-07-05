import type { JobCreatePayload } from "@/lib/types";

export const defaultJobPayload: JobCreatePayload = {
  schema_version: 1,
  job_type: "ship_detection",
  area_of_interest: {
    type: "bbox",
    coordinates: [-74.3, 40.3, -73.5, 41.0]
  },
  sensor: "SAR",
  priority: "fastest",
  compute_preference: "orbital_if_available",
  max_cost_usd: 500
};
