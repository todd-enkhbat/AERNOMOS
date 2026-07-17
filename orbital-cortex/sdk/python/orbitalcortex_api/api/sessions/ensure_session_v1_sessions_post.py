from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.session_response import SessionResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/sessions",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SessionResponse | None:
    if response.status_code == 200:
        response_200 = SessionResponse.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = SessionResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SessionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[SessionResponse]:
    """Create or resume a private anonymous session

     Ensures a private anonymous session cookie. If a valid cookie is already present, resumes it.
    Otherwise mints a new session token, stores only its hash, and sets an HttpOnly cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SessionResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> SessionResponse | None:
    """Create or resume a private anonymous session

     Ensures a private anonymous session cookie. If a valid cookie is already present, resumes it.
    Otherwise mints a new session token, stores only its hash, and sets an HttpOnly cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SessionResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[SessionResponse]:
    """Create or resume a private anonymous session

     Ensures a private anonymous session cookie. If a valid cookie is already present, resumes it.
    Otherwise mints a new session token, stores only its hash, and sets an HttpOnly cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SessionResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> SessionResponse | None:
    """Create or resume a private anonymous session

     Ensures a private anonymous session cookie. If a valid cookie is already present, resumes it.
    Otherwise mints a new session token, stores only its hash, and sets an HttpOnly cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SessionResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
