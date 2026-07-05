# Orbital Cortex Python SDK

Local Python SDK for the Orbital Cortex simulated orbital compute control plane.

## Install

```bash
cd orbital-cortex/sdk/python
pip install -e .
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

job_id = response["job"]["id"]
client.jobs.run(job_id)
result = client.jobs.result(job_id)
print(result["result"]["summary"])
```

The SDK is dependency-light and uses Python's standard library HTTP client by default. It can be tested with an injected transport and does not require a live server for unit tests.
