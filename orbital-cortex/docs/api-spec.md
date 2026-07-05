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
  "schema_version": 1,
  "job_type": "ship_detection",
  "area_of_interest": {
    "type": "bbox",
    "coordinates": [-74.3, 40.3, -73.5, 41.0]
  },
  "sensor": "SAR",
  "priority": "fastest",
  "compute_preference": "orbital_if_available",
  "max_cost_usd": 500,
  "status": "routing",
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

Creates a job and enqueues it for async execution. Returns immediately with
`queued`; the worker drives routing and execution. `routing_decision` is
`null` until the worker routes the job (fetch it later via
`GET /v1/routing/{job_id}`).

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
    "selected_route_id": null
  },
  "routing_decision": null
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
      "payload": {"job_type": "ship_detection", "priority": "fastest"},
      "ts_utc": "2026-01-01T12:00:00Z"
    }
  ]
}
```

The event log is append-only. State-change events carry `status_from` /
`status_to` in `payload`.

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

Returns all simulated compute nodes and ground stations. Orbital nodes carry
a `satellite_id` mapping them to a real satellite in the TLE registry.

Response:

```json
{
  "compute_nodes": [],
  "ground_stations": []
}
```

### `GET /v1/ground-stations`

Returns the real ground-station registry (KSAT, AWS Ground Station, Leaf
Space sites) with coordinates, altitude, provider, and elevation mask.

```json
{
  "ground_stations": [
    {
      "id": "gs_ksat_svalbard",
      "name": "KSAT Svalbard (SvalSat)",
      "provider": "KSAT",
      "latitude": 78.2297,
      "longitude": 15.3975,
      "altitude_m": 450,
      "min_elevation_deg": 10.0
    }
  ]
}
```

### `GET /v1/satellites`

Returns the tracked satellite fleet with pinned TLEs.

```json
{
  "satellites": [
    {
      "id": "sat_sentinel_1a",
      "name": "SENTINEL-1A",
      "norad_id": 39634,
      "tle_line1": "1 39634U ...",
      "tle_line2": "2 39634 ...",
      "tle_epoch": "2026-07-04T13:53:37+00:00",
      "snapshot_id": "celestrak-2026-07-05",
      "downlink_rate_mbps": 520
    }
  ]
}
```

### `GET /v1/contact-windows`

Returns SGP4-propagated passes from the precomputed cache (no propagation on
the request path). Query params: `satellite_id`, `ground_station_id`, `date`
(YYYY-MM-DD), `upcoming` (bool), `limit`.

```json
{
  "contact_windows": [
    {
      "id": "cw_...",
      "satellite_id": "sat_sentinel_1a",
      "ground_station_id": "gs_ksat_svalbard",
      "aos_utc": "2026-07-05T06:43:51+00:00",
      "culminate_utc": "2026-07-05T06:48:35+00:00",
      "los_utc": "2026-07-05T06:53:19+00:00",
      "max_elevation_deg": 64.98,
      "duration_s": 568.2,
      "est_downlink_mb": 36933.0
    }
  ]
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
    "status": "complete"
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
| `queued` | Job accepted and waiting for routing |
| `routing` | Route selected; awaiting execution |
| `executing` | Mock execution is in progress |
| `downlinking` | Result packaged and downlink in progress |
| `complete` | Mock result is available |
| `failed` | Simulation failed due to validation or policy |

Transitions are guarded by a state machine (`queued -> routing -> executing -> downlinking -> complete`, any non-terminal state may move to `failed`). Illegal transitions are rejected with a 409 `illegal_state_transition` error.
