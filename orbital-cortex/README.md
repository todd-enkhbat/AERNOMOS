# Orbital Cortex

Orbital Cortex is an MVP demo of an orbital compute orchestration control plane. It lets a user submit a simulated space-data AI job, evaluates a mocked network of orbital compute nodes, ground stations, and cloud fallback nodes, then explains the selected route before simulating execution and returning logs and results.

The v0.1 demo use case is maritime ship detection over New York Harbor using simulated SAR data.

## Phase 1 Status

This phase creates the monorepo skeleton and project documentation. Runtime implementation will follow in later phases.

Included now:

- Monorepo directory layout for frontend, backend, SDK, simulator data, and examples
- Product specification
- Architecture notes
- API contract
- Routing model
- Glossary
- Seed-style simulator and example request JSON files

## What The MVP Demonstrates

- A user submits a local AI job through a web UI, API request, or Python SDK.
- The backend evaluates deterministic simulated infrastructure.
- The router scores candidate nodes by model support, latency, cost, availability, contact windows, compute preference, and compliance tags.
- The selected route is explained in human-readable terms.
- A manual simulation endpoint advances the job lifecycle.
- Mock inference returns realistic-looking results, including fake ship detections around New York Harbor.

## Monorepo Layout

```text
orbital-cortex/
  README.md
  docs/
  apps/
    web/
    api/
  sdk/
    python/
  simulator/
  examples/
```

## Planned Local Development

Backend, once implemented:

```bash
cd orbital-cortex/apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend, once implemented:

```bash
cd orbital-cortex/apps/web
npm install
npm run dev
```

Python SDK, once implemented:

```bash
cd orbital-cortex/sdk/python
pip install -e .
python examples/submit_ship_detection.py
```

## Example SDK Usage

```python
from orbitalcortex import Client

client = Client(api_key="oc_test_123", base_url="http://localhost:8000")

job = client.jobs.create(
    job_type="ship_detection",
    area_of_interest={
        "type": "bbox",
        "coordinates": [-74.3, 40.3, -73.5, 41.0],
    },
    sensor="SAR",
    priority="fastest",
    compute_preference="orbital_if_available",
    max_cost_usd=500,
)

print(job)
```

## What Is Simulated

- Satellite and orbital compute node availability
- Ground station contact windows
- Model availability and node capabilities
- Routing decisions, cost, latency, confidence, and explanations
- Job lifecycle events
- Inference output for ship detection, crop health, and disaster response

## What Would Be Real In Production

- Satellite tasking, ephemeris, and contact-window calculations
- Ground station reservation and telemetry systems
- Real model execution on orbital, edge, or cloud infrastructure
- Data ingest, validation, storage, and provenance
- Authentication, authorization, billing, audit logs, and compliance controls
- Operational monitoring, retries, failure handling, and incident response

## Constraints

Orbital Cortex v0.1 is local-only and deterministic. It does not integrate with real satellites, real ground stations, real payment providers, real defense systems, or classified workflows.
