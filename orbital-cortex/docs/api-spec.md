# API Spec

## Base URL

```text
http://localhost:8000
```

## Authentication

The MVP accepts a fake API key field or header for demo consistency. It is not real authentication.

Recommended local header shape:

```text
Authorization: Bearer oc_test_123
```

## Common Types

### Job

```json
{
  "id": "job_01HOC...",
  "job_type": "ship_detection",
  "area_of_interest": {
    "type": "bbox",
    "coordinates": [-74.3, 40.3, -73.5, 41.0]
  },
  "sensor": "SAR",
  "priority": "fastest",
  "compute_preference": "orbital_if_available",
  "max_cost_usd": 500,
  "status": "queued",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "selected_route_id": "route_01HOC..."
}
```

### ComputeNode

```json
{
  "id": "sim_leo_02",
  "name": "Sim LEO 02",
  "type": "orbital",
  "location": "LEO inclination 53",
  "orbit": "LEO",
  "gpu_class": "Vera Rubin class simulated",
  "supported_models": ["ship_detection", "crop_health", "disaster_response"],
  "storage_gb": 2048,
  "downlink_mbps": 450,
  "power_state": "nominal",
  "availability": 0.92,
  "compliance_tags": ["commercial", "research", "non_defense"],
  "base_cost_usd": 180,
  "latency_minutes": 24
}
```

### RoutingDecision

```json
{
  "id": "route_01HOC...",
  "job_id": "job_01HOC...",
  "selected_node_id": "sim_leo_02",
  "selected_ground_station_id": "svalbard_gs",
  "fallback_node_id": "aws_us_east_gpu",
  "estimated_latency_minutes": 35,
  "estimated_cost_usd": 214,
  "confidence": 0.86,
  "reasons": [
    "Supports ship_detection",
    "Next contact window in 11 minutes",
    "Meets fastest priority",
    "Costs less than the cloud-only route"
  ],
  "candidate_scores": [
    {
      "node_id": "sim_leo_02",
      "score": 89.4,
      "estimated_latency_minutes": 35,
      "estimated_cost_usd": 214,
      "available": true,
      "reasons": ["model_supported", "good_contact_window"]
    }
  ]
}
```

## Endpoints

### `POST /v1/jobs`

Creates a job and routing decision.

Request:

```json
{
  "job_type": "ship_detection",
  "area_of_interest": {
    "type": "bbox",
    "coordinates": [-74.3, 40.3, -73.5, 41.0]
  },
  "sensor": "SAR",
  "priority": "fastest",
  "compute_preference": "orbital_if_available",
  "max_cost_usd": 500
}
```

Response:

```json
{
  "job": {
    "id": "job_01HOC...",
    "status": "queued",
    "selected_route_id": "route_01HOC..."
  },
  "routing_decision": {
    "selected_node_id": "sim_leo_02",
    "estimated_latency_minutes": 35,
    "estimated_cost_usd": 214
  }
}
```

### `GET /v1/jobs`

Lists jobs.

Response:

```json
{
  "jobs": []
}
```

### `GET /v1/jobs/{job_id}`

Returns job details, status, routing decision, and result summary when present.

Response:

```json
{
  "job": {},
  "routing_decision": {},
  "result_summary": null
}
```

### `GET /v1/jobs/{job_id}/events`

Returns lifecycle events.

Response:

```json
{
  "events": [
    {
      "id": "evt_01HOC...",
      "job_id": "job_01HOC...",
      "event_type": "job_created",
      "message": "Job accepted by control plane.",
      "timestamp": "2026-01-01T12:00:00Z"
    }
  ]
}
```

### `GET /v1/jobs/{job_id}/result`

Returns a mock result after completion.

Response for `ship_detection`:

```json
{
  "result": {
    "id": "res_01HOC...",
    "job_id": "job_01HOC...",
    "summary": "Detected 17 likely vessels in New York Harbor.",
    "confidence": 0.91,
    "geojson": {
      "type": "FeatureCollection",
      "features": []
    },
    "output_files": []
  }
}
```

### `GET /v1/nodes`

Returns all simulated compute nodes and ground stations.

Response:

```json
{
  "compute_nodes": [],
  "ground_stations": []
}
```

### `GET /v1/routing/{job_id}`

Returns selected routing decision and candidate node scores.

Response:

```json
{
  "routing_decision": {}
}
```

### `POST /v1/simulate/run/{job_id}`

Manually advances a job through simulated execution.

Response:

```json
{
  "job": {
    "id": "job_01HOC...",
    "status": "completed"
  },
  "events_created": 4,
  "result": {}
}
```

## Error Shape

Use a consistent local error format:

```json
{
  "error": {
    "code": "job_not_found",
    "message": "No job exists for id job_missing."
  }
}
```

## Status Values

| Status | Meaning |
| --- | --- |
| `queued` | Job accepted and waiting for simulation |
| `scheduled` | Route selected and execution scheduled |
| `running` | Mock execution is in progress |
| `completed` | Mock result is available |
| `failed` | Simulation failed due to validation or policy |
