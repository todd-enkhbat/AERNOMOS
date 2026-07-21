from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.scene_response import SceneResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    job_id: str,
    *,
    x_nomos_job_token: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_nomos_job_token, Unset):
        headers["x-nomos-job-token"] = x_nomos_job_token

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs/{job_id}/scene".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | SceneResponse | None:
    if response.status_code == 200:
        response_200 = SceneResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | HTTPValidationError | SceneResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_nomos_job_token: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | SceneResponse]:
    """Get the SAR scene provenance for a job

    Args:
        job_id (str):
        x_nomos_job_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | SceneResponse]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        x_nomos_job_token=x_nomos_job_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_nomos_job_token: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | SceneResponse | None:
    """Get the SAR scene provenance for a job

    Args:
        job_id (str):
        x_nomos_job_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | SceneResponse
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        x_nomos_job_token=x_nomos_job_token,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_nomos_job_token: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | SceneResponse]:
    """Get the SAR scene provenance for a job

    Args:
        job_id (str):
        x_nomos_job_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | SceneResponse]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        x_nomos_job_token=x_nomos_job_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_nomos_job_token: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | SceneResponse | None:
    """Get the SAR scene provenance for a job

    Args:
        job_id (str):
        x_nomos_job_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | SceneResponse
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            x_nomos_job_token=x_nomos_job_token,
        )
    ).parsed
