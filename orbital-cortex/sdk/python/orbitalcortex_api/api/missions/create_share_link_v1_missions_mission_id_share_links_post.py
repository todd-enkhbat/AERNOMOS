from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.share_link_create import ShareLinkCreate
from ...models.share_link_response import ShareLinkResponse
from ...types import Response


def _get_kwargs(
    mission_id: str,
    *,
    body: ShareLinkCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/missions/{mission_id}/share-links".format(
            mission_id=quote(str(mission_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | ShareLinkResponse | None:
    if response.status_code == 201:
        response_201 = ShareLinkResponse.from_dict(response.json())

        return response_201

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
) -> Response[ErrorResponse | HTTPValidationError | ShareLinkResponse]:
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
    body: ShareLinkCreate,
) -> Response[ErrorResponse | HTTPValidationError | ShareLinkResponse]:
    """Create a private share link for a mission you own

     Returns the raw share token once. Only the SHA-256 hash is stored. Pass the token as `X-Nomos-Share-
    Token` or `share_token` query param.

    Args:
        mission_id (str):
        body (ShareLinkCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ShareLinkResponse]
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
    body: ShareLinkCreate,
) -> ErrorResponse | HTTPValidationError | ShareLinkResponse | None:
    """Create a private share link for a mission you own

     Returns the raw share token once. Only the SHA-256 hash is stored. Pass the token as `X-Nomos-Share-
    Token` or `share_token` query param.

    Args:
        mission_id (str):
        body (ShareLinkCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ShareLinkResponse
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
    body: ShareLinkCreate,
) -> Response[ErrorResponse | HTTPValidationError | ShareLinkResponse]:
    """Create a private share link for a mission you own

     Returns the raw share token once. Only the SHA-256 hash is stored. Pass the token as `X-Nomos-Share-
    Token` or `share_token` query param.

    Args:
        mission_id (str):
        body (ShareLinkCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ShareLinkResponse]
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
    body: ShareLinkCreate,
) -> ErrorResponse | HTTPValidationError | ShareLinkResponse | None:
    """Create a private share link for a mission you own

     Returns the raw share token once. Only the SHA-256 hash is stored. Pass the token as `X-Nomos-Share-
    Token` or `share_token` query param.

    Args:
        mission_id (str):
        body (ShareLinkCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ShareLinkResponse
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            client=client,
            body=body,
        )
    ).parsed
