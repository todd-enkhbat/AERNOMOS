from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.mission_feedback_create import MissionFeedbackCreate
from ...models.mission_feedback_response import MissionFeedbackResponse
from ...types import Response


def _get_kwargs(
    mission_id: str,
    *,
    body: MissionFeedbackCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/missions/{mission_id}/feedback".format(
            mission_id=quote(str(mission_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | MissionFeedbackResponse | None:
    if response.status_code == 201:
        response_201 = MissionFeedbackResponse.from_dict(response.json())

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
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | MissionFeedbackResponse]:
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
    body: MissionFeedbackCreate,
) -> Response[ErrorResponse | MissionFeedbackResponse]:
    """Submit optional mission plan feedback

     Lightweight yes/partly/no feedback after a plan exists. Never required for planning. Comment is
    capped server-side (reject, not truncate).

    Args:
        mission_id (str):
        body (MissionFeedbackCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | MissionFeedbackResponse]
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
    body: MissionFeedbackCreate,
) -> ErrorResponse | MissionFeedbackResponse | None:
    """Submit optional mission plan feedback

     Lightweight yes/partly/no feedback after a plan exists. Never required for planning. Comment is
    capped server-side (reject, not truncate).

    Args:
        mission_id (str):
        body (MissionFeedbackCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | MissionFeedbackResponse
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
    body: MissionFeedbackCreate,
) -> Response[ErrorResponse | MissionFeedbackResponse]:
    """Submit optional mission plan feedback

     Lightweight yes/partly/no feedback after a plan exists. Never required for planning. Comment is
    capped server-side (reject, not truncate).

    Args:
        mission_id (str):
        body (MissionFeedbackCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | MissionFeedbackResponse]
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
    body: MissionFeedbackCreate,
) -> ErrorResponse | MissionFeedbackResponse | None:
    """Submit optional mission plan feedback

     Lightweight yes/partly/no feedback after a plan exists. Never required for planning. Comment is
    capped server-side (reject, not truncate).

    Args:
        mission_id (str):
        body (MissionFeedbackCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | MissionFeedbackResponse
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            client=client,
            body=body,
        )
    ).parsed
