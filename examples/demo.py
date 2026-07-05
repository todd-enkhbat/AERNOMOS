"""End-to-end MVS demo: submit a job, route it, log it.

Run with:
    python examples/demo.py

This is the script the Week 1 demo video is built around. It uses a
generic SimulatedNode — no specific hardware (T-REX or otherwise) is
assumed. Swap in a real Node subclass once one exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nomos import JobStatus, NomosClient, SimulatedNode  # noqa: E402


def main() -> None:
    node = SimulatedNode(name="sim-node-1", capabilities={"generic-compute"})
    client = NomosClient(nodes=[node])

    print("Submitting job to Nomos Orbital (MVS skeleton)...\n")
    result = client.submit_job(
        job_type="generic-compute",
        payload={"task": "matrix-multiply", "size": 128},
    )

    print(f"\nResult: status={result.status.value} node={result.node_name}")
    if result.status == JobStatus.COMPLETED:
        print(f"Output: {result.output}")
    else:
        print(f"Error: {result.error}")

    print(f"\nFull job log: {client._log.log_path}")


if __name__ == "__main__":
    main()
