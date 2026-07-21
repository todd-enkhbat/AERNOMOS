# Nomos Orbital Python SDK

Python SDK for the Nomos Orbital orbital compute control plane.

Two layers:

- **`orbitalcortex`** — the hand-written ergonomic wrapper (this package):
  sync + async clients, `wait_for_job` polling, automatic retries with
  exponential backoff (tenacity) on GET 5xx/transport failures.
- **`orbitalcortex_api`** — the low-level client generated from the live
  OpenAPI spec by `openapi-python-client`. CI regenerates it on merge
  (`.github/workflows/sdk.yml`); never edit it by hand.

## Install

```bash
cd orbital-cortex/sdk/python
pip install -e .
```

With async support:

```bash
pip install -e ".[async]"
```

## Quick start

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

## Mission planner

The `missions` resource wraps the private mission workflow with customer
terminology (mission, plan, candidate, share link). A private anonymous session
is created automatically — no login and no API key required.

```python
from orbitalcortex import Client

client = Client(base_url="http://localhost:8000")

mission = client.missions.create(
    title="Harbor monitoring",
    objective_type="analyze_imagery",
    area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
)
plan = client.missions.generate_plan(mission["id"])
report = client.missions.export_pdf(mission["id"])
```

Typed errors let you branch on customer-meaningful conditions instead of a
generic HTTP error. See `orbital-cortex/docs/provider-integrations.md` for the
full status-code + error-code mapping table.

```python
from orbitalcortex import (
    NoCatalogData, NoFeasiblePlan, UpstreamProviderUnavailable,
    UnauthorizedMission, ExpiredShareLink, StaleOrbitalData,
    InvalidGeographicInput,
)
```

A runnable example lives in `examples/plan_mission.py`.

## Async client

```python
from orbitalcortex import AsyncClient

async with AsyncClient(api_key="oc_test_123", base_url="http://localhost:8000") as client:
    job = await client.jobs.create(
        job_type="ship_detection",
        area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
        sensor="SAR",
        priority="fastest",
        compute_preference="orbital_if_available",
        max_cost_usd=500,
    )
    print(job)
```

## Resources

| Resource | Methods |
| --- | --- |
| `client.missions` | `create`, `retrieve`, `list`, `list_examples`, `discover`, `candidates`, `infrastructure`, `generate_plan`, `list_plans`, `get_plan`, `export_pdf`, `latest_pdf`, `export_json`, `create_share_link` |
| `client.jobs` | `create`, `list`, `retrieve`, `events`, `scene`, `detections`, `result`, `simulate_run`, `wait_for_job` |
| `client.routing` | `retrieve`, `replay` |
| `client.nodes` | `list` |
| `client.registry` | `ground_stations`, `satellites`, `contact_windows` |

## Error handling

```python
from orbitalcortex import APIError, Client, TransportError

try:
    client.jobs.retrieve("missing")
except APIError as exc:
    print(exc.status, exc.code, exc.message)
except TransportError:
    print("Network failure")
```

## Development

```bash
pip install -e ".[async,generated]" pytest
pytest tests -q
```

Regenerate the low-level client after API changes (from repo root):

```bash
cd orbital-cortex/apps/api
python -m scripts.export_openapi ../../openapi.json
cd ../..
openapi-python-client generate --path openapi.json --output-path sdk/python/orbitalcortex_api --overwrite --meta none
```
