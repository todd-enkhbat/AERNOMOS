import type { JobCreatePayload, NodesResponse } from "@/lib/types";

export const defaultJobPayload: JobCreatePayload = {
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

export const fallbackNodes: NodesResponse = {
  compute_nodes: [
    {
      id: "sim_leo_01",
      name: "Sim LEO 01",
      type: "orbital",
      location: "LEO inclination 51.6",
      orbit: "LEO",
      gpu_class: "Jetson Orin class",
      supported_models: ["ship_detection", "cloud_detection"],
      storage_gb: 512,
      downlink_mbps: 120,
      power_state: "nominal",
      availability: 0.88,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 140,
      latency_minutes: 32,
      next_contact_minutes: 18
    },
    {
      id: "sim_leo_02",
      name: "Sim LEO 02",
      type: "orbital",
      location: "LEO inclination 53.0",
      orbit: "LEO",
      gpu_class: "Vera Rubin class simulated",
      supported_models: ["ship_detection", "crop_health", "disaster_response"],
      storage_gb: 2048,
      downlink_mbps: 450,
      power_state: "nominal",
      availability: 0.92,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 180,
      latency_minutes: 24,
      next_contact_minutes: 11
    },
    {
      id: "sim_kepler_like_node",
      name: "Sim Kepler-like Node",
      type: "orbital",
      location: "LEO sun-synchronous simulated",
      orbit: "LEO",
      gpu_class: "Edge inference class",
      supported_models: ["ship_detection"],
      storage_gb: 768,
      downlink_mbps: 160,
      power_state: "nominal",
      availability: 0.81,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 115,
      latency_minutes: 38,
      next_contact_minutes: 27
    },
    {
      id: "sim_starcloud_like_node",
      name: "Sim Starcloud-like Node",
      type: "orbital",
      location: "LEO high-capacity simulated",
      orbit: "LEO",
      gpu_class: "Orbital data center class",
      supported_models: ["ship_detection", "crop_health", "disaster_response"],
      storage_gb: 8192,
      downlink_mbps: 1000,
      power_state: "nominal",
      availability: 0.87,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 420,
      latency_minutes: 20,
      next_contact_minutes: 43
    },
    {
      id: "aws_us_east_gpu",
      name: "AWS US East GPU",
      type: "ground_cloud",
      location: "us-east-1 simulated",
      orbit: null,
      gpu_class: "A10G class simulated",
      supported_models: ["ship_detection", "crop_health", "disaster_response"],
      storage_gb: 16384,
      downlink_mbps: 0,
      power_state: "nominal",
      availability: 0.98,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 275,
      latency_minutes: 18,
      next_contact_minutes: 0
    },
    {
      id: "coreweave_gpu_cluster",
      name: "CoreWeave GPU Cluster",
      type: "ground_cloud",
      location: "northeast US simulated",
      orbit: null,
      gpu_class: "L40S class simulated",
      supported_models: ["ship_detection", "crop_health", "disaster_response"],
      storage_gb: 32768,
      downlink_mbps: 0,
      power_state: "nominal",
      availability: 0.96,
      compliance_tags: ["commercial", "research", "non_defense"],
      base_cost_usd: 310,
      latency_minutes: 16,
      next_contact_minutes: 0
    }
  ],
  ground_stations: [
    {
      id: "alaska_gs",
      name: "Alaska Ground Station",
      location: "Fairbanks, Alaska",
      latitude: 64.8378,
      longitude: -147.7164,
      latency_minutes: 6,
      downlink_mbps: 800,
      availability: 0.94
    },
    {
      id: "singapore_gs",
      name: "Singapore Ground Station",
      location: "Singapore",
      latitude: 1.3521,
      longitude: 103.8198,
      latency_minutes: 9,
      downlink_mbps: 700,
      availability: 0.93
    },
    {
      id: "svalbard_gs",
      name: "Svalbard Ground Station",
      location: "Svalbard, Norway",
      latitude: 78.2232,
      longitude: 15.6267,
      latency_minutes: 5,
      downlink_mbps: 900,
      availability: 0.96
    },
    {
      id: "hawaii_gs",
      name: "Hawaii Ground Station",
      location: "Hawaii, United States",
      latitude: 19.8968,
      longitude: -155.5828,
      latency_minutes: 7,
      downlink_mbps: 750,
      availability: 0.95
    }
  ]
};
