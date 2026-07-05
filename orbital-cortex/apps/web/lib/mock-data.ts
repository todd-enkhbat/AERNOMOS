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
  "compute_nodes": [
    {
      "id": "sim_leo_01",
      "name": "Sim LEO 01",
      "type": "orbital",
      "location": "LEO inclination 51.6",
      "orbit": "LEO",
      "gpu_class": "Jetson Orin class",
      "supported_models": [
        "ship_detection",
        "cloud_detection"
      ],
      "storage_gb": 512,
      "downlink_mbps": 120,
      "power_state": "nominal",
      "availability": 0.88,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 140,
      "latency_minutes": 32,
      "satellite_id": "sat_iceye_x2"
    },
    {
      "id": "sim_leo_02",
      "name": "Sim LEO 02",
      "type": "orbital",
      "location": "LEO inclination 53.0",
      "orbit": "LEO",
      "gpu_class": "Vera Rubin class simulated",
      "supported_models": [
        "ship_detection",
        "crop_health",
        "disaster_response"
      ],
      "storage_gb": 2048,
      "downlink_mbps": 450,
      "power_state": "nominal",
      "availability": 0.92,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 180,
      "latency_minutes": 24,
      "satellite_id": "sat_sentinel_1a"
    },
    {
      "id": "sim_kepler_like_node",
      "name": "Sim Kepler-like Node",
      "type": "orbital",
      "location": "LEO sun-synchronous simulated",
      "orbit": "LEO",
      "gpu_class": "Edge inference class",
      "supported_models": [
        "ship_detection"
      ],
      "storage_gb": 768,
      "downlink_mbps": 160,
      "power_state": "nominal",
      "availability": 0.81,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 115,
      "latency_minutes": 38,
      "satellite_id": "sat_capella_15"
    },
    {
      "id": "sim_starcloud_like_node",
      "name": "Sim Starcloud-like Node",
      "type": "orbital",
      "location": "LEO high-capacity simulated",
      "orbit": "LEO",
      "gpu_class": "Orbital data center class",
      "supported_models": [
        "ship_detection",
        "crop_health",
        "disaster_response"
      ],
      "storage_gb": 8192,
      "downlink_mbps": 1000,
      "power_state": "nominal",
      "availability": 0.87,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 420,
      "latency_minutes": 20,
      "satellite_id": "sat_capella_14"
    },
    {
      "id": "aws_us_east_gpu",
      "name": "AWS US East GPU",
      "type": "ground_cloud",
      "location": "us-east-1 simulated",
      "orbit": null,
      "gpu_class": "A10G class simulated",
      "supported_models": [
        "ship_detection",
        "crop_health",
        "disaster_response"
      ],
      "storage_gb": 16384,
      "downlink_mbps": 0,
      "power_state": "nominal",
      "availability": 0.98,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 275,
      "latency_minutes": 18,
      "satellite_id": null
    },
    {
      "id": "coreweave_gpu_cluster",
      "name": "CoreWeave GPU Cluster",
      "type": "ground_cloud",
      "location": "northeast US simulated",
      "orbit": null,
      "gpu_class": "L40S class simulated",
      "supported_models": [
        "ship_detection",
        "crop_health",
        "disaster_response"
      ],
      "storage_gb": 32768,
      "downlink_mbps": 0,
      "power_state": "nominal",
      "availability": 0.96,
      "compliance_tags": [
        "commercial",
        "research",
        "non_defense"
      ],
      "base_cost_usd": 310,
      "latency_minutes": 16,
      "satellite_id": null
    }
  ],
  "ground_stations": [
    {
      "id": "gs_ksat_svalbard",
      "name": "KSAT Svalbard (SvalSat)",
      "location": "Longyearbyen, Svalbard, Norway",
      "provider": "KSAT",
      "latitude": 78.2297,
      "longitude": 15.3975,
      "altitude_m": 450,
      "min_elevation_deg": 10.0,
      "latency_minutes": 5,
      "downlink_mbps": 900,
      "availability": 0.96
    },
    {
      "id": "gs_ksat_tromso",
      "name": "KSAT Tromso",
      "location": "Tromso, Norway",
      "provider": "KSAT",
      "latitude": 69.6625,
      "longitude": 18.9408,
      "altitude_m": 90,
      "min_elevation_deg": 10.0,
      "latency_minutes": 5,
      "downlink_mbps": 850,
      "availability": 0.95
    },
    {
      "id": "gs_ksat_punta_arenas",
      "name": "KSAT Punta Arenas",
      "location": "Punta Arenas, Chile",
      "provider": "KSAT",
      "latitude": -52.9354,
      "longitude": -70.8489,
      "altitude_m": 30,
      "min_elevation_deg": 10.0,
      "latency_minutes": 6,
      "downlink_mbps": 800,
      "availability": 0.94
    },
    {
      "id": "gs_aws_oregon",
      "name": "AWS Ground Station Oregon (us-west-2)",
      "location": "Oregon, United States (approximate)",
      "provider": "AWS Ground Station",
      "latitude": 43.8041,
      "longitude": -120.5542,
      "altitude_m": 1200,
      "min_elevation_deg": 10.0,
      "latency_minutes": 4,
      "downlink_mbps": 800,
      "availability": 0.97
    },
    {
      "id": "gs_aws_ohio",
      "name": "AWS Ground Station Ohio (us-east-2)",
      "location": "Ohio, United States (approximate)",
      "provider": "AWS Ground Station",
      "latitude": 40.4173,
      "longitude": -82.9071,
      "altitude_m": 300,
      "min_elevation_deg": 10.0,
      "latency_minutes": 4,
      "downlink_mbps": 800,
      "availability": 0.97
    },
    {
      "id": "gs_leaf_awarua",
      "name": "Leaf Space Awarua",
      "location": "Awarua, New Zealand",
      "provider": "Leaf Space",
      "latitude": -46.5285,
      "longitude": 168.3811,
      "altitude_m": 10,
      "min_elevation_deg": 10.0,
      "latency_minutes": 7,
      "downlink_mbps": 700,
      "availability": 0.93
    }
  ]
};
