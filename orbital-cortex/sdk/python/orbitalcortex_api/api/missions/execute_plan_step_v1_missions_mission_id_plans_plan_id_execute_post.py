from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.execute_step_request import ExecuteStepRequest
from ...types import Response


def _get_kwargs(
    mission_id: str,
    plan_id: str,
    *,
    body: ExecuteStepRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/missions/{mission_id}/plans/{plan_id}/execute".format(
            mission_id=quote(str(mission_id), safe=""),
            plan_id=quote(str(plan_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | None:
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
) -> Response[ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mission_id: str,
    plan_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ExecuteStepRequest,
) -> Response[ErrorResponse]:
    """Execute a plan step on the local CPU provider (real, no GPUs)

     Owner-only. Runs a real CPU task (crop_geotiff or thumbnail) for an executable plan step on the
    existing ARQ worker. Durations and byte counts are measured and persisted as OBSERVED; the step
    flips from planned to executed/failed. Submits are idempotent per idempotency_key — replays return
    the existing job unchanged.

    Args:
        mission_id (str):
        plan_id (str):
        body (ExecuteStepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        plan_id=plan_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_id: str,
    plan_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ExecuteStepRequest,
) -> ErrorResponse | None:
    """Execute a plan step on the local CPU provider (real, no GPUs)

     Owner-only. Runs a real CPU task (crop_geotiff or thumbnail) for an executable plan step on the
    existing ARQ worker. Durations and byte counts are measured and persisted as OBSERVED; the step
    flips from planned to executed/failed. Submits are idempotent per idempotency_key — replays return
    the existing job unchanged.

    Args:
        mission_id (str):
        plan_id (str):
        body (ExecuteStepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse
    """

    return sync_detailed(
        mission_id=mission_id,
        plan_id=plan_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    mission_id: str,
    plan_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ExecuteStepRequest,
) -> Response[ErrorResponse]:
    """Execute a plan step on the local CPU provider (real, no GPUs)

     Owner-only. Runs a real CPU task (crop_geotiff or thumbnail) for an executable plan step on the
    existing ARQ worker. Durations and byte counts are measured and persisted as OBSERVED; the step
    flips from planned to executed/failed. Submits are idempotent per idempotency_key — replays return
    the existing job unchanged.

    Args:
        mission_id (str):
        plan_id (str):
        body (ExecuteStepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        plan_id=plan_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_id: str,
    plan_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ExecuteStepRequest,
) -> ErrorResponse | None:
    """Execute a plan step on the local CPU provider (real, no GPUs)

     Owner-only. Runs a real CPU task (crop_geotiff or thumbnail) for an executable plan step on the
    existing ARQ worker. Durations and byte counts are measured and persisted as OBSERVED; the step
    flips from planned to executed/failed. Submits are idempotent per idempotency_key — replays return
    the existing job unchanged.

    Args:
        mission_id (str):
        plan_id (str):
        body (ExecuteStepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            plan_id=plan_id,
            client=client,
            body=body,
        )
    ).parsed
