"""HTTP transport for the Nomos Orbital SDK.

The default transport keeps a cookie jar so the private anonymous session
cookie minted by ``POST /v1/sessions`` is stored and resent automatically on
subsequent mission requests.
"""

from __future__ import annotations

import http.cookiejar
import json
from typing import Any, Dict, Optional, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, OpenerDirector, Request, build_opener

from orbitalcortex.exceptions import TransportError, error_from_response


class Transport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        timeout: float,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...


class UrllibTransport:
    """Small standard-library JSON transport with an in-memory cookie jar."""

    def __init__(self) -> None:
        self._cookie_jar = http.cookiejar.CookieJar()
        self._opener: OpenerDirector = build_opener(
            HTTPCookieProcessor(self._cookie_jar)
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        timeout: float,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        body = None
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")

        request = Request(url=url, data=body, headers=headers, method=method)

        try:
            with self._opener.open(request, timeout=timeout) as response:
                raw = response.read()
                if not raw:
                    return {}
                return _decode_json(raw)
        except HTTPError as exc:
            raw_error = exc.read()
            payload = _decode_json(raw_error) if raw_error else {}
            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            message = error.get("message") or f"Nomos Orbital API returned {exc.code}"
            code = error.get("code") or "api_error"
            raise error_from_response(
                status_code=exc.code,
                code=code,
                message=message,
                response=payload if isinstance(payload, dict) else {},
            ) from exc
        except URLError as exc:
            raise TransportError(
                f"Could not reach Nomos Orbital API: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise TransportError("Timed out while calling Nomos Orbital API") from exc


def _decode_json(raw: bytes) -> Dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise TransportError("Nomos Orbital API returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise TransportError("Nomos Orbital API returned a non-object JSON payload")
    return value
