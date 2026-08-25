from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.mission_pdf_export_response import MissionPdfExportResponse
from ...types import Response


def _get_kwargs(
    mission_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/missions/{mission_id}/exports/pdf".format(
            mission_id=quote(str(mission_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | MissionPdfExportResponse | None:
    if response.status_code == 201:
        response_201 = MissionPdfExportResponse.from_dict(response.json())

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

    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | MissionPdfExportResponse]:
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
) -> Response[ErrorResponse | HTTPValidationError | MissionPdfExportResponse]:
    """Generate a PDF mission brief

     Owner-only. Creates an export job and generates the PDF (sync for MVP). Returns a signed download
    URL when ready. Large jobs may be processed by the ARQ worker via generate_mission_pdf_export.

    Args:
        mission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | MissionPdfExportResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | HTTPValidationError | MissionPdfExportResponse | None:
    """Generate a PDF mission brief

     Owner-only. Creates an export job and generates the PDF (sync for MVP). Returns a signed download
    URL when ready. Large jobs may be processed by the ARQ worker via generate_mission_pdf_export.

    Args:
        mission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | MissionPdfExportResponse
    """

    return sync_detailed(
        mission_id=mission_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | HTTPValidationError | MissionPdfExportResponse]:
    """Generate a PDF mission brief

     Owner-only. Creates an export job and generates the PDF (sync for MVP). Returns a signed download
    URL when ready. Large jobs may be processed by the ARQ worker via generate_mission_pdf_export.

    Args:
        mission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | MissionPdfExportResponse]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | HTTPValidationError | MissionPdfExportResponse | None:
    """Generate a PDF mission brief

     Owner-only. Creates an export job and generates the PDF (sync for MVP). Returns a signed download
    URL when ready. Large jobs may be processed by the ARQ worker via generate_mission_pdf_export.

    Args:
        mission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | MissionPdfExportResponse
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            client=client,
        )
    ).parsed
