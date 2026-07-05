# Orbital Cortex Python SDK

Python SDK for the Orbital Cortex simulated orbital compute control plane.

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
pip install -e .            # sync client only
pip install -e ".[async]"   # + httpx-backed AsyncClient
```

## Usage

```python
from orbitalcortex import Client

client = Client(api_key="oc_test_123", base_url="http://127.0.0.1:8000")

response = client.jobs.create(
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

# Block until the async worker finishes (or JobTimeoutError).
detail = client.wait_for_job(response["job"]["id"], timeout=120)

result = client.jobs.result(detail["job"]["id"])
print(result["result"]["summary"])
for artifact in result["artifacts"]:
    print(artifact["key"], "->", artifact["url"])  # signed URL

# Routing explanation + deterministic replay
explanation = client.jobs.routing(detail["job"]["id"])
replay = client.jobs.replay(detail["job"]["id"])
assert replay["match"]

# Registry (cursor-paginated where applicable)
page = client.jobs.list(limit=20)
while page["next_cursor"]:
    page = client.jobs.list(limit=20, cursor=page["next_cursor"])
windows = client.registry.contact_windows(upcoming=True, limit=10)
```

### Async

```python
import asyncio
from orbitalcortex import AsyncClient

async def main() -> None:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        created = await client.create_job(
            job_type="ship_detection",
            area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
            sensor="SAR",
            priority="fastest",
            compute_preference="orbital_if_available",
            max_cost_usd=500,
        )
        detail = await client.wait_for_job(created["job"]["id"])
        print(detail["job"]["status"])

asyncio.run(main())
```

### Retries

GET requests retry up to `max_retries` times (default 2) on transport
errors and 5xx responses, with exponential backoff + jitter. POSTs never
retry unless you pass `retry=True` to `_request`. Configure per client:

```python
Client(max_retries=4, retry_backoff_s=0.5, timeout=10.0)
```

The sync client uses Python's standard-library HTTP client and can be unit
tested with an injected transport — no live server needed.
