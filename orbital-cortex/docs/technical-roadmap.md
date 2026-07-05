# Orbital Cortex Technical Roadmap

This document consolidates the current Orbital Cortex MVP, the external research response, and the practical engineering path from local demo to credible orbital compute orchestration prototype.

## 1. Current State

Orbital Cortex is currently a local MVP demo of an orbital compute orchestration control plane.

It lets a user:

- submit a space-data AI job
- score simulated orbital compute nodes, ground stations, and cloud fallback nodes
- inspect why a route was selected
- simulate execution
- view lifecycle logs
- view mock vessel detection results
- use a Python SDK against the same API

Current stack:

- Frontend: Next.js, TypeScript, Tailwind
- Backend: FastAPI, Python
- Database: SQLite
- SDK: local Python package
- Data: deterministic simulator JSON
- Current use case: SAR ship detection over New York Harbor
- Deployment target: frontend on Vercel, backend on Render/Railway/Fly

Current non-goals:

- no real satellite control
- no live satellite tasking
- no real ground station integration
- no payments
- no defense, targeting, weapons, or classified workflows
- no real SAR inference yet

## 2. What Orbital Cortex Is

Orbital Cortex sits between several existing categories:

- Cloud orchestration: decides where compute should run
- Satellite tasking: adjacent, but not the same; tasking decides where a satellite looks
- Ground station scheduling: treats downlink sites as constrained network nodes
- Edge computing: assumes intermittent, resource-constrained execution environments
- Geospatial AI: produces spatial outputs such as GeoJSON, raster tiles, and detections
- MLOps control planes: manages models, inference jobs, logs, artifacts, and results

The technical concept is:

> A control plane that routes space-data AI jobs across orbital, ground, and cloud compute paths based on physics, cost, latency, model availability, compliance, and operator policy.

The current MVP simulates this well enough for product storytelling. The next step is adding enough real physics and geospatial infrastructure that technical users believe the architecture.

## 3. Main Research Conclusion

The most important next credibility jump is:

1. Replace fake contact windows with real orbital propagation.
2. Replace local SQLite with Postgres/PostGIS.
3. Replace the fake result map with a real map viewer.
4. Add async job execution.
5. Improve routing from weighted scoring toward constraint-based scheduling.

Do not jump directly to real satellite APIs. That adds legal, cost, operational, and compliance complexity too early.

## 4. System Layers And Complexity

| Layer | Current MVP | Real Version | Complexity | Recommended Next Step |
| --- | --- | --- | ---: | --- |
| User/API | REST endpoints and SDK | Auth, async jobs, webhooks, quotas | 2 | Add API versioning and polling helpers |
| Job spec | simple JSON payload | strict schema, GeoJSON AOI, model requirements | 2 | Formalize request/response schemas |
| Geospatial data | mock bbox and GeoJSON | GeoTIFF, COG, STAC, PostGIS | 4 | Add PostGIS and MapLibre viewer |
| Satellite tasking | not implemented | provider APIs, capture scheduling | 5 | Keep simulated |
| Contact windows | fake `next_contact_minutes` | TLE + SGP4 + ground station visibility | 4 | Integrate Skyfield |
| Ground stations | JSON records | availability windows, antenna constraints | 3 | Add real coordinates and visibility windows |
| Orbital compute | JSON node profiles | hardware limits, power, thermal, storage | 5 | Keep simulated but model constraints better |
| Cloud fallback | mocked cloud nodes | GPU availability, queueing, costs | 3 | Add deterministic cost model |
| Routing | weighted scoring | hard constraints + optimization | 4 | Add hard filters and route manifest |
| Model registry | supported model strings | model versions, hardware compatibility | 3 | Add model registry table |
| Results | mock GeoJSON | object storage, provenance, STAC metadata | 4 | Add result artifacts and map visualization |
| Billing | mock cost | compute + downlink + storage pricing | 3 | Expand cost calculator |
| Observability | lifecycle events | structured logs, traces, replay | 3 | Add route audit snapshot |
| Security | fake API key | auth, tenants, data access controls | 4 | Keep simple for demo, design boundary |
| Deployment | local only | Vercel + managed backend + Postgres | 3 | Add production env config |

## 5. Orbital Compute Reality Check

Orbital compute is real, but constrained.

What exists now:

- satellite edge compute payloads
- hosted payload compute environments
- radiation-tolerant processors
- AI inference demos in orbit
- commercial ground station services
- cloud ground station services

What is still early or speculative:

- large orbital data centers
- heavy AI training in orbit
- general-purpose cloud-style compute in orbit
- cheap, flexible, high-power GPU clusters in space

Major constraints:

- Power: satellites have limited generation and battery capacity
- Thermal: no convective cooling in vacuum
- Radiation: bit flips and hardware degradation
- Bandwidth: raw imagery downlink is expensive and slow
- Contact windows: LEO satellites only see a ground station for minutes
- Hardware lifecycle: repair is usually impossible
- Launch cost: mass and volume matter
- Reliability: fault tolerance must be designed upfront

The strongest product thesis:

> Downlinking raw imagery can be expensive and slow; downlinking AI-derived insights can be smaller, faster, and operationally valuable.

## 6. Contact Windows And Scheduling

Real contact windows are based on orbital mechanics.

Key concepts:

- TLE: Two-Line Element set describing a satellite orbit
- SGP4: propagation model used to predict satellite position
- AOS: acquisition of signal, when a pass begins
- LOS: loss of signal, when a pass ends
- elevation mask: minimum angle above horizon, often 5 to 15 degrees
- pass duration: often 5 to 12 minutes for LEO
- ground station visibility: depends on satellite orbit and station coordinates

Recommended libraries:

- Skyfield: best next Python choice for this repo
- sgp4: lower-level propagation library
- Orekit: powerful Java astrodynamics toolkit
- Cesium: 3D/temporal visualization
- MapLibre/deck.gl: practical web map visualization

Near-term implementation:

- add TLE fields to orbital nodes
- add latitude/longitude to ground stations
- create `core/contact_windows.py` functions using Skyfield
- compute next pass windows for the next 24 to 48 hours
- replace fake `next_contact_minutes` with computed values
- keep deterministic seed TLEs for demo repeatability

## 7. Routing Engine Evolution

Current router:

- filters model support
- scores latency
- scores cost
- scores availability
- scores contact window
- scores compute preference
- scores compliance

This is good for an MVP, but real scheduling needs hard constraints and time-aware routes.

Next router architecture:

1. Path Generator
   - Generates physically possible paths:
   - target/satellite -> orbital node -> ground station -> cloud fallback/result

2. Constraint Builder
   - Applies hard constraints:
   - model support
   - compliance
   - max budget
   - max latency
   - node availability
   - contact availability

3. Solver/Scorer
   - For now: deterministic weighted scoring plus hard filters
   - Later: OR-Tools or PuLP

4. Route Manifest
   - Selected path
   - top alternatives
   - rejected candidates
   - exact scoring inputs
   - policy checks
   - replay metadata

5. Execution Router
   - Schedules simulation or real execution
   - Emits events
   - Stores result artifact metadata

Recommended progression:

| Stage | Approach | Why |
| --- | --- | --- |
| MVP | weighted scoring | simple and explainable |
| Serious demo | hard constraints + weighted scoring | credible and deterministic |
| Prototype | OR-Tools CP-SAT or PuLP | real scheduling behavior |
| Production | constraint optimization + queueing + audit replay | defensible infrastructure |

Avoid reinforcement learning for now. It is hard to explain, hard to audit, and unnecessary for this stage.

## 8. Routing Manifest Shape

Add a richer response later:

```json
{
  "route_id": "route_123",
  "selected_path": {
    "node_id": "sim_leo_02",
    "ground_station_id": "svalbard_gs",
    "fallback_node_id": "aws_us_east_gpu",
    "estimated_latency_minutes": 35,
    "estimated_cost_usd": 214
  },
  "hard_constraints": {
    "model_supported": true,
    "compliance_allowed": true,
    "budget_allowed": true,
    "contact_available": true
  },
  "soft_scores": {
    "latency": 21.4,
    "cost": 8.2,
    "availability": 13.8,
    "preference": 10
  },
  "rejected_candidates": [
    {
      "node_id": "sim_leo_01",
      "reason": "Model unsupported for disaster_response"
    }
  ],
  "replay": {
    "router_version": "0.2.0",
    "input_hash": "sha256...",
    "seed_data_version": "2026-07-05"
  }
}
```

## 9. Geospatial And SAR Pipeline

The current result is fake GeoJSON. That is acceptable for demo v0.1.

A credible SAR maritime pipeline would include:

1. Ingest
   - Sentinel-1 or other SAR source
   - GeoTIFF or SAFE format
   - cloud/object storage

2. Preprocess
   - calibration
   - speckle filtering
   - orthorectification
   - clipping to AOI

3. Tile
   - chip large raster into model-sized tiles
   - preserve georeferencing

4. Infer
   - ship detection model
   - bounding boxes or masks
   - confidence scores

5. Postprocess
   - merge tile results
   - remove false positives
   - convert to GeoJSON
   - optionally correlate with AIS

6. Publish
   - GeoJSON detections
   - COG preview
   - STAC metadata
   - map tiles

Recommended libraries:

- GDAL
- Rasterio
- GeoPandas
- Shapely
- PostGIS
- STAC
- TiTiler
- MapLibre
- deck.gl

Near-term practical version:

- do not train a model yet
- use one archived/open SAR image
- create precomputed detections
- render the detections on a real map
- store output as GeoJSON artifact

## 10. Backend Roadmap

### v0.2: Deployable Demo

Goal: make the app public-demo ready.

Build:

- env-based CORS
- Render/Railway/Fly backend config
- production env variables
- SQLite reset strategy or move to Postgres
- health checks
- Dockerfile optional

Acceptance criteria:

- frontend deployed on Vercel
- backend deployed publicly
- frontend can submit a job to backend
- demo can be reset safely

### v0.3: Geospatial Credibility

Goal: make the system spatially credible.

Build:

- Postgres/PostGIS
- real `geometry` columns for AOI, nodes, ground stations
- MapLibre result viewer
- GeoJSON result artifacts
- route map overlays

Acceptance criteria:

- job AOI is stored as spatial geometry
- detections render on a real basemap
- query jobs/results by AOI

### v0.4: Physics-Aware Routing

Goal: replace fake contact windows.

Build:

- Skyfield integration
- TLE seed data
- pass prediction for ground stations
- computed contact windows
- route timeline from capture to result

Acceptance criteria:

- orbital node next-contact values are computed
- route reasons include AOS/LOS times
- frontend shows contact window timeline

### v0.5: Async Execution

Goal: make job execution realistic.

Build:

- Redis + RQ/Arq/Celery
- background job worker
- status polling
- SDK `wait_for_completion`
- job cancellation

Acceptance criteria:

- `POST /v1/jobs` returns quickly
- worker advances job lifecycle
- frontend polls or subscribes
- SDK can wait with timeout

### v0.6: Optimization Router

Goal: make routing mathematically credible.

Build:

- hard constraints
- route manifest
- runner-up candidates
- rejection log
- OR-Tools or PuLP prototype
- deterministic replay/audit table

Acceptance criteria:

- no candidate is selected if it violates hard constraints
- route can be replayed from saved inputs
- frontend explains why alternatives lost

## 11. Frontend Roadmap

Current frontend is good for an MVP.

Next components:

- real MapLibre result map
- orbital network map
- contact-window timeline
- route comparison table
- route rejection log
- job submit wizard
- API/SDK docs with real examples
- demo reset button for hosted environment

Important UI principle:

> The product should feel like an operations console, not a marketing site.

Keep:

- calm typography
- dense but readable panels
- strong route explanations
- map/table/result surfaces

Avoid:

- flashy cyberpunk visuals
- vague space decoration
- animations before the core data is credible

## 12. SDK Roadmap

Current SDK:

- synchronous client
- standard-library HTTP transport
- typed request/response shapes
- jobs/nodes/routing resources
- example script

Next SDK features:

- `client.jobs.wait(job_id, timeout=...)`
- retries and backoff
- typed models with Pydantic or dataclasses
- async client
- pagination helpers
- artifact download helpers
- streaming/polling logs
- SDK examples for all job types
- generated clients from OpenAPI later

Do not overbuild the SDK before the API stabilizes.

## 13. Deployment Roadmap

Recommended deployment:

- frontend: Vercel
- backend: Render, Railway, or Fly
- database: Neon, Supabase, Railway Postgres, or Render Postgres
- object storage later: S3, R2, or MinIO for local dev

Before public deployment:

- add env-based CORS
- add production API URL to Vercel env vars
- add backend env vars
- decide SQLite reset vs Postgres
- ensure `node_modules` and `.next` are ignored
- add deployment README
- add health check endpoint
- add demo reset script if public

Recommended Vercel settings:

- root directory: `orbital-cortex/apps/web`
- framework: Next.js
- env var: `NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com`

Recommended backend start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 14. Security, Compliance, And Safety

This is dual-use-adjacent because it combines space systems, geospatial data, and AI.

Keep these boundaries explicit:

- no targeting
- no weapons
- no classified data
- no military operational workflows
- no real satellite control until legal/commercial review
- no high-resolution restricted imagery without licensing review

Near-term safety features:

- compliance tags on nodes
- audit logs for routing decisions
- explicit `non_defense` demo policy
- fake API key only for local demo
- no user-uploaded sensitive data

Later production features:

- real auth
- tenants
- role-based access control
- immutable audit log
- data retention policy
- geospatial licensing metadata
- export-control review workflow

## 15. Competitive Landscape

Adjacent categories:

| Category | Examples | What They Do | Orbital Cortex Difference |
| --- | --- | --- | --- |
| Satellite imagery APIs | Planet, SkyWatch, Umbra | provide imagery and tasking access | Orbital Cortex focuses on compute routing after/during capture |
| Ground station services | AWS Ground Station, Azure Orbital, KSAT | provide antenna/downlink services | Orbital Cortex treats them as route candidates |
| Geospatial AI platforms | UP42, Descartes Labs style platforms | run analytics on geospatial data | Orbital Cortex emphasizes orbital/cloud routing logic |
| Space edge compute | Loft Orbital, Unibap, Ramon.Space | provide physical or abstraction-layer compute | Orbital Cortex could sit above multiple providers |
| MLOps platforms | generic model deployment systems | manage model execution | Orbital Cortex adds intermittent connectivity and orbital constraints |

Positioning:

> Orbital Cortex is not trying to be a satellite company. It is the control plane that decides where space-data compute should happen.

## 16. 30-Day Engineering Plan

### Week 1: Deployability And Schema Cleanup

Build:

- env-based CORS
- deployment docs
- backend production config
- `render.yaml` or equivalent
- formal GeoJSON AOI validation
- route manifest draft schema

Tests:

- CORS test
- job validation test
- route manifest shape test

Outcome:

- can deploy demo without architecture embarrassment

### Week 2: Real Map Result Viewer

Build:

- MapLibre integration
- NY Harbor basemap
- render detections on map
- detection table with filters
- output artifact section

Tests:

- frontend build
- result parsing unit helper tests if added

Outcome:

- results look like a real geospatial product

### Week 3: Postgres/PostGIS Migration

Build:

- SQLAlchemy or SQLModel persistence layer
- Postgres connection config
- PostGIS extension migration
- AOI geometry
- ground station geometry
- result geometry

Tests:

- database integration test
- spatial insert/read test

Outcome:

- credible geospatial backend foundation

### Week 4: Physics-Aware Contact Windows

Build:

- Skyfield integration
- TLE fields on orbital nodes
- next-pass calculation
- computed `next_contact_minutes`
- contact window API payload
- frontend timeline card

Tests:

- deterministic TLE calculation test
- known-pass fixture test

Outcome:

- system crosses from mock web app to aerospace software prototype

## 17. What Not To Build Yet

Do not build these yet:

- real satellite tasking
- live ground station reservation
- Stripe billing
- multi-tenant enterprise admin
- real defense workflows
- reinforcement learning scheduler
- full orbital data center simulation
- model training platform
- real SAR inference pipeline from scratch

These are too expensive or distracting before the demo is deployed and technically credible.

## 18. Immediate Recommendation

The next best build order is:

1. Make the app deployable.
2. Add a real MapLibre result map.
3. Move to Postgres/PostGIS.
4. Add Skyfield contact windows.
5. Add async job execution.
6. Add route manifest and replay/audit logs.

If the goal is investor/demo impact, do:

- hosted deployment
- map viewer
- polished route explanation
- screenshots/GIF for README

If the goal is technical credibility, do:

- PostGIS
- Skyfield
- route manifest
- deterministic replay

If the goal is product direction, do:

- focus on archived geospatial data processing first
- do not integrate real satellites yet
- prove that orchestration saves latency, cost, or bandwidth

## 19. Personal Learning Plan

### Module 1: Orbital Mechanics

Learn:

- TLEs
- SGP4
- ground tracks
- AOS/LOS
- elevation masks

Mini-project:

- write a Python script that prints the next 5 passes of a satellite over a ground station using Skyfield

### Module 2: Geospatial Engineering

Learn:

- GeoJSON
- GeoTIFF
- COG
- STAC
- PostGIS
- MapLibre

Mini-project:

- load a public Sentinel scene, clip to an AOI, and display detections on a web map

### Module 3: Routing And Optimization

Learn:

- hard vs soft constraints
- multi-objective optimization
- OR-Tools
- route explainability

Mini-project:

- build a route solver that chooses between cost, latency, and compliance constraints

### Module 4: Backend Infrastructure

Learn:

- FastAPI production patterns
- Postgres migrations
- Redis workers
- object storage
- OpenTelemetry

Mini-project:

- convert one endpoint to async background execution with polling

### Module 5: Product And Compliance

Learn:

- geospatial data licensing
- export-control basics
- dual-use risk boundaries
- audit logging

Mini-project:

- design a compliance policy engine that rejects jobs based on data/node tags

## 20. Final Product Thesis

Orbital Cortex should evolve into:

> A physics-aware, geospatial AI orchestration control plane that decides whether a space-data workload should run on orbital edge compute, through a ground station path, or in cloud fallback, with transparent cost, latency, compliance, and confidence tradeoffs.

The shortest path to credibility is not adding more pages. It is making the routing decision depend on real spatial and orbital constraints.
