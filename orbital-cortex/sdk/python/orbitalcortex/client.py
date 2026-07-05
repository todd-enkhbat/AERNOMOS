"""Orbital Cortex SDK client."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from orbitalcortex._retry import build_retrying
from orbitalcortex.exceptions import JobTimeoutError
from orbitalcortex.jobs import JobsResource
from orbitalcortex.nodes import NodesResource
from orbitalcortex.registry import RegistryResource
from orbitalcortex.routing import RoutingResource
from orbitalcortex.transport import Transport, UrllibTransport

TERMINAL_STATUSES = frozenset({"complete", "failed"})


class Client:
    """Client for the Orbital Cortex control plane.

    GET requests retry on transport errors and 5xx responses with
    exponential backoff; POSTs never retry unless retry=True is passed.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_backoff_s: float = 0.25,
        transport: Optional[Transport] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ORBITAL_CORTEX_API_KEY") or "oc_test_123"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_s = retry_backoff_s
        self._transport = transport or UrllibTransport()
        self.jobs = JobsResource(self)
        self.nodes = NodesResource(self)
        self.registry = RegistryResource(self)
        self.routing = RoutingResource(self)

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/healthz")

    def ready(self) -> Dict[str, Any]:
        return self._request("GET", "/readyz")

    def wait_for_job(
        self,
        job_id: str,
        *,
        timeout: float = 120.0,
        poll_interval: float = 1.0,
    ) -> Dict[str, Any]:
        """Poll until the job reaches a terminal state (complete | failed).

        Returns the final job-detail payload; raises JobTimeoutError if the
        deadline passes first.
        """
        deadline = time.monotonic() + timeout
        detail = self.jobs.retrieve(job_id)
        while detail["job"]["status"] not in TERMINAL_STATUSES:
            if time.monotonic() >= deadline:
                raise JobTimeoutError(
                    f"Job {job_id} still {detail['job']['status']} "
                    f"after {timeout:.0f}s.",
                    job_id=job_id,
                    last_status=detail["job"]["status"],
                )
            time.sleep(poll_interval)
            detail = self.jobs.retrieve(job_id)
        return detail

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        retry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "orbitalcortex-python/0.2.0",
            "Authorization": f"Bearer {self.api_key}",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        should_retry = retry if retry is not None else method.upper() == "GET"
        if not should_retry:
            return self._transport.request(
                method.upper(),
                url,
                headers=headers,
                timeout=self.timeout,
                json_body=json_body,
            )

        for attempt in build_retrying(self.max_retries, self.retry_backoff_s):
            with attempt:
                return self._transport.request(
                    method.upper(),
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    json_body=json_body,
                )
        raise AssertionError("unreachable")  # tenacity reraises on failure
