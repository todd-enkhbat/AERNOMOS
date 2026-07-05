"""Append-only job event log.

Every state transition in a job's life gets one JSON line. This is the
seed of the audit log the ConOps docs call out as "part of the product,
not an afterthought" — right now it just writes to a local file.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Job, JobResult, JobStatus

_console = logging.getLogger("nomos")
if not _console.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    _console.addHandler(_handler)
    _console.setLevel(logging.INFO)


class JobLogger:
    def __init__(self, log_path: str | Path = "logs/jobs.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, record: dict[str, Any]) -> None:
        record["logged_at"] = datetime.now(timezone.utc).isoformat()
        with self.log_path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def log_submitted(self, job: Job) -> None:
        _console.info("job %s submitted (type=%s)", job.job_id, job.job_type)
        self._write(
            {
                "event": JobStatus.SUBMITTED.value,
                "job_id": job.job_id,
                "job_type": job.job_type,
                "payload": job.payload,
            }
        )

    def log_routed(self, job: Job, node_name: str) -> None:
        _console.info("job %s routed to node=%s", job.job_id, node_name)
        self._write(
            {
                "event": JobStatus.ROUTED.value,
                "job_id": job.job_id,
                "node_name": node_name,
            }
        )

    def log_result(self, result: JobResult) -> None:
        _console.info(
            "job %s finished status=%s node=%s duration=%.3fs",
            result.job_id,
            result.status.value,
            result.node_name,
            result.duration_s or 0.0,
        )
        self._write({"event": result.status.value, **asdict(result)})

    def read_all(self) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        with self.log_path.open() as f:
            return [json.loads(line) for line in f if line.strip()]
