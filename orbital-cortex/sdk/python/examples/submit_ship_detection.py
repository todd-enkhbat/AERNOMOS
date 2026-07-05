"""Submit and run a simulated ship detection job."""

from __future__ import annotations

import json

from orbitalcortex import APIError, Client, TransportError


def main() -> None:
    client = Client(api_key="oc_test_123", base_url="http://127.0.0.1:8000")

    try:
        created = client.jobs.create(
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
        job_id = created["job"]["id"]

        print("Created job")
        print(json.dumps(created, indent=2))

        simulated = client.jobs.run(job_id)
        print("\nSimulation complete")
        print(json.dumps(simulated, indent=2))

        events = client.jobs.events(job_id)
        print("\nEvents")
        print(json.dumps(events, indent=2))

        result = client.jobs.result(job_id)
        print("\nResult summary")
        print(result["result"]["summary"])
    except APIError as exc:
        print(f"API error [{exc.status_code} {exc.code}]: {exc}")
        raise
    except TransportError as exc:
        print(f"Transport error: {exc}")
        raise


if __name__ == "__main__":
    main()
