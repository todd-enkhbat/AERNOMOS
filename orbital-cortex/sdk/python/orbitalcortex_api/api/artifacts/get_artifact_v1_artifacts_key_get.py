from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    key: str,
    *,
    expires: int,
    signature: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["expires"] = expires

    params["signature"] = signature

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/artifacts/{key}".format(
            key=key,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

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
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],
    expires: int,
    signature: str,
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Fetch an artifact via a signed URL (local backend only)

    Args:
        key (str):
        expires (int):
        signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        key=key,
        expires=expires,
        signature=signature,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],
    expires: int,
    signature: str,
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Fetch an artifact via a signed URL (local backend only)

    Args:
        key (str):
        expires (int):
        signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        key=key,
        client=client,
        expires=expires,
        signature=signature,
    ).parsed


async def asyncio_detailed(
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],
    expires: int,
    signature: str,
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Fetch an artifact via a signed URL (local backend only)

    Args:
        key (str):
        expires (int):
        signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        key=key,
        expires=expires,
        signature=signature,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],
    expires: int,
    signature: str,
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Fetch an artifact via a signed URL (local backend only)

    Args:
        key (str):
        expires (int):
        signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            key=key,
            client=client,
            expires=expires,
            signature=signature,
        )
    ).parsed
