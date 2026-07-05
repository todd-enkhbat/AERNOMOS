"""Async Nomos Orbital client (httpx-backed).

Install with the async extra: pip install orbitalcortex[async]

Exposes the primary job workflow as flat async methods; use the sync
Client for the full resource surface.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict, Optional

from orbitalcortex._retry import build_async_retrying
from orbitalcortex.client import TERMINAL_STATUSES
from orbitalcortex.exceptions import APIError, JobTimeoutError, TransportError
from orbitalcortex.types import (
    JobCreateResponse,
    JobDetailResponse,
    JobsListResponse,
    ResultResponse,
    RoutingResponse,
)


class AsyncClient:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_backoff_s: float = 0.25,
        http_transport: Optional[Any] = None,
    ) -> None:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "AsyncClient requires httpx; install orbitalcortex[async]."
            ) from exc

        self.api_key = api_key or os.environ.get("ORBITAL_CORTEX_API_KEY") or "oc_test_123"
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.retry_backoff_s = retry_backoff_s
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            transport=http_transport,
            headers={
                "Accept": "application/json",
                "User-Agent": "orbitalcortex-python/0.2.0",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()

    async def health(self) -> Dict[str, Any]:
        return await self._request("GET", "/healthz")

    async def create_job(self, **payload: Any) -> JobCreateResponse:
        return await self._request("POST", "/v1/jobs", json_body=payload)  # type: ignore[return-value]

    async def get_job(self, job_id: str) -> JobDetailResponse:
        return await self._request("GET", f"/v1/jobs/{job_id}")  # type: ignore[return-value]

    async def list_jobs(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> JobsListResponse:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        return await self._request("GET", "/v1/jobs", params=params)  # type: ignore[return-value]

    async def get_result(self, job_id: str) -> ResultResponse:
        return await self._request("GET", f"/v1/jobs/{job_id}/result")  # type: ignore[return-value]

    async def get_routing(self, job_id: str) -> RoutingResponse:
        return await self._request("GET", f"/v1/jobs/{job_id}/routing")  # type: ignore[return-value]

    async def wait_for_job(
        self,
        job_id: str,
        *,
        timeout: float = 120.0,
        poll_interval: float = 1.0,
    ) -> JobDetailResponse:
        deadline = time.monotonic() + timeout
        detail = await self.get_job(job_id)
        while detail["job"]["status"] not in TERMINAL_STATUSES:
            if time.monotonic() >= deadline:
                raise JobTimeoutError(
                    f"Job {job_id} still {detail['job']['status']} "
                    f"after {timeout:.0f}s.",
                    job_id=job_id,
                    last_status=detail["job"]["status"],
                )
            await asyncio.sleep(poll_interval)
            detail = await self.get_job(job_id)
        return detail

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        should_retry = retry if retry is not None else method.upper() == "GET"
        if not should_retry:
            return await self._send(method, path, json_body=json_body, params=params)
        async for attempt in build_async_retrying(self.max_retries, self.retry_backoff_s):
            with attempt:
                return await self._send(
                    method, path, json_body=json_body, params=params
                )
        raise AssertionError("unreachable")  # tenacity reraises on failure

    async def _send(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        import httpx

        try:
            response = await self._http.request(
                method.upper(), path, json=json_body, params=params or None
            )
        except httpx.TimeoutException as exc:
            raise TransportError("Timed out while calling Nomos Orbital API") from exc
        except httpx.HTTPError as exc:
            raise TransportError(f"Could not reach Nomos Orbital API: {exc}") from exc

        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            raise APIError(
                error.get("message")
                or f"Nomos Orbital API returned {response.status_code}",
                status_code=response.status_code,
                code=error.get("code") or "api_error",
                response=payload if isinstance(payload, dict) else {},
            )
        if not response.content:
            return {}
        value = response.json()
        if not isinstance(value, dict):
            raise TransportError("Nomos Orbital API returned a non-object JSON payload")
        return value
