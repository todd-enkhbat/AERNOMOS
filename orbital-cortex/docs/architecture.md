# Architecture

## Summary

Nomos Orbital is a monorepo with three main runtime surfaces:

- `apps/api`: FastAPI backend, job pipeline, and routing engine
- `apps/web`: Next.js frontend for job submission and inspection
- `sdk/python`: Python SDK that wraps the API

The backend is the source of truth. The frontend and SDK both call the FastAPI API.

The root repo also contains `src/nomos/`, an in-process MVS skeleton
(submit → route → log). That package is the future in-process node adapter
layer; the HTTP API in `orbital-cortex/` is the production surface.

## System Diagram

```text
User
  |
  | Web UI or Python SDK
  v
FastAPI control plane (API process)
  |
  |-- Postgres + PostGIS (jobs, routing, events, results, registry)
  |-- Redis (ARQ job queue)
  |-- ARQ worker process (async pipeline)
  |-- Node registry + SGP4 contact windows (Skyfield)
  |-- Cost model + policy engine + routing scorer
  |-- Object store (local filesystem or Cloudflare R2)
  v
Lifecycle events, routing decisions, and result artifacts
```

## Repository Layout

```text
orbital-cortex/
  docs/
    product-spec.md
    architecture.md
    api-spec.md
    routing-model.md
    deployment.md
  apps/
    web/
      app/
      components/
      lib/
    api/
      app/
        main.py
        db/
        routes/
        core/
        models/
        routing/
        services/
        workers/
        seed.py
  sdk/
    python/
      orbitalcortex/
      orbitalcortex_api/   # OpenAPI-generated
  simulator/
  examples/
```

## Backend Components

| Component | Responsibility |
| --- | --- |
| `main.py` | FastAPI app, CORS, rate limits, health probes |
| `db/` | SQLAlchemy ORM, Alembic migrations, Postgres sessions |
| `routes/jobs.py` | Job CRUD, events, scene, detections, manual simulate |
| `routes/routing.py` | Routing decision reads and deterministic replay |
| `routes/results.py` | Result manifests and signed artifact URLs |
| `routes/nodes.py` | Compute node registry |
| `routes/registry.py` | Ground stations, satellites, contact windows |
| `routes/artifacts.py` | Local artifact serving (dev backend only) |
| `core/pipeline.py` | Resumable job state machine |
| `core/object_store.py` | Local filesystem or S3-compatible (R2) storage |
| `core/queue.py` | Redis / ARQ enqueue |
| `routing/scorer.py` | Score candidates and select the best route |
| `services/contact_windows.py` | SGP4 pass precompute and cache |
| `workers/executor.py` | ARQ worker driving the pipeline |
| `seed.py` | Load simulator JSON into Postgres |

## Frontend Components

The frontend is API-driven. TypeScript types are generated from the OpenAPI
spec (`npm run generate:api-types`).

| Route | Data source |
| --- | --- |
| `/` | Static content and links |
| `/dashboard` | `/v1/jobs`, `/v1/nodes`, `/v1/jobs/{id}/routing` |
| `/jobs` | `/v1/jobs`, `POST /v1/jobs` |
| `/jobs/[id]` | Job detail, events, routing, scene, result, replay |
| `/network` | `/v1/nodes`, `/v1/satellites`, `/v1/contact-windows` |
| `/docs` | Static examples plus API snippets |

## Data Flow

```text
POST /v1/jobs
  -> validate request
  -> create Job(status="queued")
  -> enqueue to ARQ worker (or stay queued without Redis)
  -> worker: route candidates -> persist RoutingDecision
  -> worker: advance executing -> downlinking -> complete
  -> persist Result + upload artifacts to object store
  -> return job summary

GET /v1/jobs/{id}/result
  -> read result metadata from Postgres
  -> return time-limited signed URLs for artifact bytes
```

## Persistence

Postgres + PostGIS stores jobs, routing decisions, job events, results,
compute nodes, ground stations, satellites, contact windows, and scenes.
Artifact bytes live in object storage; Postgres stores keys only.

The simulator JSON files are deterministic source data. `seed.py` loads them
into Postgres during app startup (after migrations).

## Determinism

The demo avoids random behavior unless a fixed seed is used. Given the same
sample data and job request, the same route and result should be returned.
Routing replay (`POST /v1/jobs/{id}/replay`) verifies decision hashes.

## Production Evolution

In a real system, local modules would be backed by:

- Live ephemeris and contact-window services
- Satellite and orbital compute tasking APIs
- Ground station scheduling providers
- Cloud GPU capacity APIs
- Authentication, authorization, billing, and audit systems
- Observability and incident management

## Security And Safety Boundaries

Civilian/commercial maritime domain awareness only. Simulated and real data
are labeled per record. No defense, targeting, weapons, or classified workflows.
