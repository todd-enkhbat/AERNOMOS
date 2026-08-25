from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.catalog_candidates_response import CatalogCandidatesResponse
from ...models.discover_request import DiscoverRequest
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    mission_id: str,
    *,
    body: DiscoverRequest | None | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/missions/{mission_id}/discover".format(
            mission_id=quote(str(mission_id), safe=""),
        ),
    }

    if isinstance(body, DiscoverRequest):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CatalogCandidatesResponse | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CatalogCandidatesResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429

    if response.status_code == 502:
        response_502 = ErrorResponse.from_dict(response.json())

        return response_502

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CatalogCandidatesResponse | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DiscoverRequest | None | Unset = UNSET,
) -> Response[CatalogCandidatesResponse | ErrorResponse | HTTPValidationError]:
    """Discover real STAC catalog scenes for a mission AOI

     Searches Microsoft Planetary Computer (Sentinel-1 GRD by default) over the mission area of interest
    and date range, then persists MissionDataCandidate rows with provenance. Never invents catalog
    items; upstream failures return typed catalog_* errors.

    Args:
        mission_id (str):
        body (DiscoverRequest | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogCandidatesResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DiscoverRequest | None | Unset = UNSET,
) -> CatalogCandidatesResponse | ErrorResponse | HTTPValidationError | None:
    """Discover real STAC catalog scenes for a mission AOI

     Searches Microsoft Planetary Computer (Sentinel-1 GRD by default) over the mission area of interest
    and date range, then persists MissionDataCandidate rows with provenance. Never invents catalog
    items; upstream failures return typed catalog_* errors.

    Args:
        mission_id (str):
        body (DiscoverRequest | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogCandidatesResponse | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        mission_id=mission_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DiscoverRequest | None | Unset = UNSET,
) -> Response[CatalogCandidatesResponse | ErrorResponse | HTTPValidationError]:
    """Discover real STAC catalog scenes for a mission AOI

     Searches Microsoft Planetary Computer (Sentinel-1 GRD by default) over the mission area of interest
    and date range, then persists MissionDataCandidate rows with provenance. Never invents catalog
    items; upstream failures return typed catalog_* errors.

    Args:
        mission_id (str):
        body (DiscoverRequest | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogCandidatesResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: DiscoverRequest | None | Unset = UNSET,
) -> CatalogCandidatesResponse | ErrorResponse | HTTPValidationError | None:
    """Discover real STAC catalog scenes for a mission AOI

     Searches Microsoft Planetary Computer (Sentinel-1 GRD by default) over the mission area of interest
    and date range, then persists MissionDataCandidate rows with provenance. Never invents catalog
    items; upstream failures return typed catalog_* errors.

    Args:
        mission_id (str):
        body (DiscoverRequest | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogCandidatesResponse | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            client=client,
            body=body,
        )
    ).parsed
