"""Node registry resource methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orbitalcortex.types import NodesResponse

if TYPE_CHECKING:
    from orbitalcortex.client import Client


class NodesResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    def list(self) -> NodesResponse:
        return self._client._request("GET", "/v1/nodes")  # type: ignore[return-value]
