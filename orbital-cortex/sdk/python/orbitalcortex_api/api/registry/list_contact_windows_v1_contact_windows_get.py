from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.contact_windows_response import ContactWindowsResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    satellite_id: None | str | Unset = UNSET,
    ground_station_id: None | str | Unset = UNSET,
    date: None | str | Unset = UNSET,
    upcoming: bool | Unset = False,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_satellite_id: None | str | Unset
    if isinstance(satellite_id, Unset):
        json_satellite_id = UNSET
    else:
        json_satellite_id = satellite_id
    params["satellite_id"] = json_satellite_id

    json_ground_station_id: None | str | Unset
    if isinstance(ground_station_id, Unset):
        json_ground_station_id = UNSET
    else:
        json_ground_station_id = ground_station_id
    params["ground_station_id"] = json_ground_station_id

    json_date: None | str | Unset
    if isinstance(date, Unset):
        json_date = UNSET
    else:
        json_date = date
    params["date"] = json_date

    params["upcoming"] = upcoming

    params["limit"] = limit

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/contact-windows",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContactWindowsResponse | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ContactWindowsResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ContactWindowsResponse | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    satellite_id: None | str | Unset = UNSET,
    ground_station_id: None | str | Unset = UNSET,
    date: None | str | Unset = UNSET,
    upcoming: bool | Unset = False,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
) -> Response[ContactWindowsResponse | ErrorResponse | HTTPValidationError]:
    """List precomputed SGP4 contact windows (cursor-paginated)

     Reads from the pass cache populated by the worker; no orbital propagation happens on this request
    path.

    Args:
        satellite_id (None | str | Unset):
        ground_station_id (None | str | Unset):
        date (None | str | Unset): AOS date, YYYY-MM-DD UTC
        upcoming (bool | Unset): Only windows that have not ended Default: False.
        limit (int | Unset):  Default: 100.
        cursor (None | str | Unset): Opaque cursor from a previous page's next_cursor

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContactWindowsResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        satellite_id=satellite_id,
        ground_station_id=ground_station_id,
        date=date,
        upcoming=upcoming,
        limit=limit,
        cursor=cursor,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    satellite_id: None | str | Unset = UNSET,
    ground_station_id: None | str | Unset = UNSET,
    date: None | str | Unset = UNSET,
    upcoming: bool | Unset = False,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
) -> ContactWindowsResponse | ErrorResponse | HTTPValidationError | None:
    """List precomputed SGP4 contact windows (cursor-paginated)

     Reads from the pass cache populated by the worker; no orbital propagation happens on this request
    path.

    Args:
        satellite_id (None | str | Unset):
        ground_station_id (None | str | Unset):
        date (None | str | Unset): AOS date, YYYY-MM-DD UTC
        upcoming (bool | Unset): Only windows that have not ended Default: False.
        limit (int | Unset):  Default: 100.
        cursor (None | str | Unset): Opaque cursor from a previous page's next_cursor

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContactWindowsResponse | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        satellite_id=satellite_id,
        ground_station_id=ground_station_id,
        date=date,
        upcoming=upcoming,
        limit=limit,
        cursor=cursor,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    satellite_id: None | str | Unset = UNSET,
    ground_station_id: None | str | Unset = UNSET,
    date: None | str | Unset = UNSET,
    upcoming: bool | Unset = False,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
) -> Response[ContactWindowsResponse | ErrorResponse | HTTPValidationError]:
    """List precomputed SGP4 contact windows (cursor-paginated)

     Reads from the pass cache populated by the worker; no orbital propagation happens on this request
    path.

    Args:
        satellite_id (None | str | Unset):
        ground_station_id (None | str | Unset):
        date (None | str | Unset): AOS date, YYYY-MM-DD UTC
        upcoming (bool | Unset): Only windows that have not ended Default: False.
        limit (int | Unset):  Default: 100.
        cursor (None | str | Unset): Opaque cursor from a previous page's next_cursor

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContactWindowsResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        satellite_id=satellite_id,
        ground_station_id=ground_station_id,
        date=date,
        upcoming=upcoming,
        limit=limit,
        cursor=cursor,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    satellite_id: None | str | Unset = UNSET,
    ground_station_id: None | str | Unset = UNSET,
    date: None | str | Unset = UNSET,
    upcoming: bool | Unset = False,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
) -> ContactWindowsResponse | ErrorResponse | HTTPValidationError | None:
    """List precomputed SGP4 contact windows (cursor-paginated)

     Reads from the pass cache populated by the worker; no orbital propagation happens on this request
    path.

    Args:
        satellite_id (None | str | Unset):
        ground_station_id (None | str | Unset):
        date (None | str | Unset): AOS date, YYYY-MM-DD UTC
        upcoming (bool | Unset): Only windows that have not ended Default: False.
        limit (int | Unset):  Default: 100.
        cursor (None | str | Unset): Opaque cursor from a previous page's next_cursor

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContactWindowsResponse | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            satellite_id=satellite_id,
            ground_station_id=ground_station_id,
            date=date,
            upcoming=upcoming,
            limit=limit,
            cursor=cursor,
        )
    ).parsed
