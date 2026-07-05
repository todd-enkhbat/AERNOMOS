# Architecture

## Summary

Orbital Cortex is a local monorepo with three main runtime surfaces:

- `apps/api`: FastAPI backend and deterministic simulation engine
- `apps/web`: Next.js frontend for job submission and inspection
- `sdk/python`: Python SDK that wraps the API

The backend is the source of truth. The frontend and SDK both call the FastAPI API.

## System Diagram

```text
User
  |
  | Web UI or Python SDK
  v
FastAPI control plane
  |
  |-- SQLite local database
  |-- Node registry
  |-- Contact window simulator
  |-- Cost model
  |-- Policy engine
  |-- Router and scheduler
  |-- Mock inference
  v
Simulated result and lifecycle events
```

## Repository Layout

```text
orbital-cortex/
  docs/
    product-spec.md
    architecture.md
    api-spec.md
    routing-model.md
    glossary.md
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
      examples/
  simulator/
    sample_nodes.json
    ground_stations.json
    tle_snapshot.json
    sample_jobs.json
  examples/
    submit_ship_detection.json
    submit_crop_health.json
    submit_disaster_response.json
```

## Backend Components

| Component | Responsibility |
| --- | --- |
| `main.py` | Create the FastAPI app and mount routers |
| `db.py` | Configure local SQLite persistence |
| `routes/jobs.py` | Job creation, listing, detail, events, and simulation entrypoint |
| `routes/nodes.py` | Simulated node and ground station reads |
| `routes/routing.py` | Routing decision and candidate score reads |
| `routes/results.py` | Result reads |
| `core/router.py` | Score candidates and select the best route |
| `core/scheduler.py` | Advance simulated lifecycle states |
| `core/node_registry.py` | Load and expose deterministic infrastructure data |
| `core/contact_windows.py` | Return mocked contact windows |
| `core/cost_model.py` | Estimate job cost by node and priority |
| `core/policy_engine.py` | Enforce local demo constraints |
| `core/mock_inference.py` | Return deterministic fake results |
| `models/` | Database and API data models |
| `seed.py` | Load sample data into SQLite |

## Frontend Components

The frontend should stay API-driven and simple.

| Route | Data source |
| --- | --- |
| `/` | Static content and links |
| `/dashboard` | `/v1/jobs`, `/v1/nodes` |
| `/jobs` | `/v1/jobs`, `POST /v1/jobs` |
| `/jobs/[id]` | `/v1/jobs/{job_id}`, events, routing, result |
| `/network` | `/v1/nodes` |
| `/docs` | Static examples plus API snippets |

## Data Flow

```text
POST /v1/jobs
  -> validate request
  -> create Job(status="queued")
  -> load node registry
  -> route candidates
  -> persist RoutingDecision
  -> append JobEvent("route_selected")
  -> return job summary

POST /v1/simulate/run/{job_id}
  -> read job and route
  -> advance queued -> scheduled -> running -> completed
  -> append events for each transition
  -> run mock inference
  -> persist Result
  -> return updated job
```

## Persistence

SQLite is sufficient for local v0.1 development. The schema should include jobs, routing decisions, job events, results, compute nodes, and ground stations.

The simulator JSON files are deterministic source data. `seed.py` should load them into SQLite during local setup or app startup.

## Determinism

The demo should avoid random behavior unless a fixed seed is used. Given the same sample data and job request, the same route and result should be returned.

## Production Evolution

In a real system, the local modules would be replaced or backed by:

- Ephemeris and contact-window services
- Satellite and orbital compute tasking APIs
- Ground station scheduling providers
- Cloud GPU capacity APIs
- Object storage and provenance tracking
- Authentication, authorization, billing, and audit systems
- Observability and incident management

## Security And Safety Boundaries

The MVP does not include real auth, real classified workflows, real defense integrations, or operational satellite commands. The fake API key field is a local demo affordance, not a security mechanism.
