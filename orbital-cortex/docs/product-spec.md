# Product Spec

## Product

Nomos Orbital is an orbital compute orchestration platform. It gives developers one control plane for submitting space-data AI jobs, comparing execution routes, and inspecting deterministic results.

## MVP Goal

Demonstrate the end-to-end control-plane experience for routing a space-data AI job across simulated satellites, orbital compute, ground stations, and cloud fallback nodes.

The MVP should feel credible without depending on real external infrastructure.

## v0.1 Use Case

Maritime ship detection over New York Harbor using simulated SAR data.

Default area of interest:

```json
{
  "type": "bbox",
  "coordinates": [-74.3, 40.3, -73.5, 41.0]
}
```

## Target User

- A developer evaluating an orbital compute API concept
- A platform engineer comparing routing, latency, and cost tradeoffs
- A product or investor audience viewing a credible technical demo

## Core Workflow

1. User submits a job with job type, area of interest, sensor, priority, compute preference, and max cost.
2. Backend persists the job locally.
3. Router evaluates simulated compute nodes and ground stations.
4. Backend creates a routing decision with candidate scores and reasons.
5. User inspects the selected route and scoring rationale.
6. User manually advances the simulation.
7. Backend records lifecycle events and returns a mock result.

## Job Types

| Job type | Sensor fit | Result shape |
| --- | --- | --- |
| `ship_detection` | SAR preferred | GeoJSON vessel detections |
| `crop_health` | Hyperspectral or optical | Crop stress summary |
| `disaster_response` | SAR or optical | Flood or damage summary |

## Inputs

| Field | Required | Notes |
| --- | --- | --- |
| `job_type` | Yes | `ship_detection`, `crop_health`, or `disaster_response` |
| `area_of_interest` | Yes | GeoJSON-like object or bbox object |
| `sensor` | Yes | `SAR`, `optical`, `hyperspectral`, or `any` |
| `priority` | Yes | `fastest`, `cheapest`, or `most_reliable` |
| `compute_preference` | Yes | `orbital_if_available`, `ground_only`, `cheapest`, or `fastest` |
| `max_cost_usd` | Yes | Soft upper bound used by the router |

## Key Screens

| Route | Purpose |
| --- | --- |
| `/` | Product landing and primary actions |
| `/dashboard` | System overview and recent jobs |
| `/jobs` | Submit jobs and view the job table |
| `/jobs/[id]` | Inspect route, scores, events, result, and API preview |
| `/network` | View simulated orbital, ground, and cloud infrastructure |
| `/docs` | API and SDK examples |

## User Stories

- As a developer, I can submit a ship detection job from the frontend.
- As a developer, I can submit the same job through the API or SDK.
- As an operator, I can see why a route was selected.
- As an operator, I can compare candidate node scores.
- As an evaluator, I can run the simulation locally with no external services.
- As an evaluator, I can inspect mock logs and mock results.

## Non-Goals

- Real satellite tasking
- Real ground station scheduling
- Real payments or billing integration
- Real authentication beyond a fake API key field
- Defense, classified, targeting, or weapon-system functionality
- Non-deterministic external API calls

## Acceptance Criteria For The Full MVP

1. User can run the FastAPI backend locally.
2. User can run the Next.js frontend locally.
3. User can submit a `ship_detection` job from the frontend.
4. Backend creates a routing decision.
5. User can view route, logs, candidate scores, and result on the job detail page.
6. Python SDK example can submit a job.
7. README and docs explain the concept clearly.

## Phase Plan

| Phase | Scope |
| --- | --- |
| 1 | Docs, repository skeleton, sample data, and examples |
| 2 | FastAPI data models, seed data, routing, persistence, and endpoints |
| 3 | Python SDK and example scripts |
| 4 | Next.js frontend and route visualizations |
| 5 | Polish, deterministic demo data, and local verification |
