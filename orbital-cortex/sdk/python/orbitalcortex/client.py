"""Orbital Cortex SDK client."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from orbitalcortex.jobs import JobsResource
from orbitalcortex.nodes import NodesResource
from orbitalcortex.routing import RoutingResource
from orbitalcortex.transport import Transport, UrllibTransport


class Client:
    """Client for the local Orbital Cortex control plane."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        transport: Optional[Transport] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ORBITAL_CORTEX_API_KEY") or "oc_test_123"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._transport = transport or UrllibTransport()
        self.jobs = JobsResource(self)
        self.nodes = NodesResource(self)
        self.routing = RoutingResource(self)

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "orbitalcortex-python/0.1.0",
            "Authorization": f"Bearer {self.api_key}",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        return self._transport.request(
            method.upper(),
            url,
            headers=headers,
            timeout=self.timeout,
            json_body=json_body,
        )
