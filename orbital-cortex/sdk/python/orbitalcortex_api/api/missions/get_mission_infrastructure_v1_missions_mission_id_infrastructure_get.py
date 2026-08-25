from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.mission_infrastructure_response import MissionInfrastructureResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    mission_id: str,
    *,
    share_token: None | str | Unset = UNSET,
    x_nomos_share_token: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_nomos_share_token, Unset):
        headers["x-nomos-share-token"] = x_nomos_share_token

    params: dict[str, Any] = {}

    json_share_token: None | str | Unset
    if isinstance(share_token, Unset):
        json_share_token = UNSET
    else:
        json_share_token = share_token
    params["share_token"] = json_share_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/missions/{mission_id}/infrastructure".format(
            mission_id=quote(str(mission_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | MissionInfrastructureResponse | None:
    if response.status_code == 200:
        response_200 = MissionInfrastructureResponse.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | MissionInfrastructureResponse]:
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
    share_token: None | str | Unset = UNSET,
    x_nomos_share_token: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | MissionInfrastructureResponse]:
    """Mission-relevant satellites, ground stations, and orbital snapshot provenance

     Returns only fleet satellites matching the mission's catalog candidates or data-source preferences
    (never the full tracked catalog), plus public ground stations and the TLE snapshot metadata used for
    contact windows.

    Args:
        mission_id (str):
        share_token (None | str | Unset): Deprecated: prefer X-Nomos-Share-Token header to avoid
            token leakage via Referer and access logs.
        x_nomos_share_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | MissionInfrastructureResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        share_token=share_token,
        x_nomos_share_token=x_nomos_share_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    share_token: None | str | Unset = UNSET,
    x_nomos_share_token: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | MissionInfrastructureResponse | None:
    """Mission-relevant satellites, ground stations, and orbital snapshot provenance

     Returns only fleet satellites matching the mission's catalog candidates or data-source preferences
    (never the full tracked catalog), plus public ground stations and the TLE snapshot metadata used for
    contact windows.

    Args:
        mission_id (str):
        share_token (None | str | Unset): Deprecated: prefer X-Nomos-Share-Token header to avoid
            token leakage via Referer and access logs.
        x_nomos_share_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | MissionInfrastructureResponse
    """

    return sync_detailed(
        mission_id=mission_id,
        client=client,
        share_token=share_token,
        x_nomos_share_token=x_nomos_share_token,
    ).parsed


async def asyncio_detailed(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    share_token: None | str | Unset = UNSET,
    x_nomos_share_token: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | MissionInfrastructureResponse]:
    """Mission-relevant satellites, ground stations, and orbital snapshot provenance

     Returns only fleet satellites matching the mission's catalog candidates or data-source preferences
    (never the full tracked catalog), plus public ground stations and the TLE snapshot metadata used for
    contact windows.

    Args:
        mission_id (str):
        share_token (None | str | Unset): Deprecated: prefer X-Nomos-Share-Token header to avoid
            token leakage via Referer and access logs.
        x_nomos_share_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | MissionInfrastructureResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        share_token=share_token,
        x_nomos_share_token=x_nomos_share_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
    share_token: None | str | Unset = UNSET,
    x_nomos_share_token: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | MissionInfrastructureResponse | None:
    """Mission-relevant satellites, ground stations, and orbital snapshot provenance

     Returns only fleet satellites matching the mission's catalog candidates or data-source preferences
    (never the full tracked catalog), plus public ground stations and the TLE snapshot metadata used for
    contact windows.

    Args:
        mission_id (str):
        share_token (None | str | Unset): Deprecated: prefer X-Nomos-Share-Token header to avoid
            token leakage via Referer and access logs.
        x_nomos_share_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | MissionInfrastructureResponse
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            client=client,
            share_token=share_token,
            x_nomos_share_token=x_nomos_share_token,
        )
    ).parsed
