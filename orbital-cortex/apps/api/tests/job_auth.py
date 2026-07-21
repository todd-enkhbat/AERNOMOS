"""Shared helpers for job access-token tests."""

from __future__ import annotations

from typing import Any, Dict, Tuple


def create_private_job(client, payload: Dict[str, Any]) -> Tuple[str, Dict[str, str]]:
    """POST /v1/jobs and return (job_id, auth headers with X-Nomos-Job-Token)."""
    created = client.post("/v1/jobs", json=payload)
    assert created.status_code == 201, created.text
    body = created.json()
    token = body["access_token"]
    assert token, "create response must include one-time access_token"
    return body["job"]["id"], {"X-Nomos-Job-Token": token}
