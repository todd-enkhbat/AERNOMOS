"""Ground station, satellite, and contact-window registry routes."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core import node_registry
from app.core.pagination import InvalidCursorError, encode_cursor
from app.db import get_db
from app.models.errors import ErrorResponse
from app.models.node import (
    ContactWindowsResponse,
    GroundStationsResponse,
    SatellitesResponse,
)
from app.services import contact_windows as cw_service

router = APIRouter(prefix="/v1", tags=["registry"])


@router.get(
    "/ground-stations",
    response_model=GroundStationsResponse,
    summary="List ground stations (real public sites)",
)
def list_ground_stations(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {"ground_stations": node_registry.list_ground_stations(session)}


@router.get(
    "/satellites",
    response_model=SatellitesResponse,
    summary="List satellites with their pinned TLEs",
)
def list_satellites(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {"satellites": node_registry.list_satellites(session)}


@router.get(
    "/contact-windows",
    response_model=ContactWindowsResponse,
    summary="List precomputed SGP4 contact windows (cursor-paginated)",
    description=(
        "Reads from the pass cache populated by the worker; no orbital "
        "propagation happens on this request path."
    ),
    responses={400: {"model": ErrorResponse, "description": "Malformed cursor"}},
)
def list_contact_windows(
    satellite_id: Optional[str] = Query(default=None),
    ground_station_id: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None, description="AOS date, YYYY-MM-DD UTC"),
    upcoming: bool = Query(default=False, description="Only windows that have not ended"),
    limit: int = Query(default=100, ge=1, le=500),
    cursor: Optional[str] = Query(
        default=None, description="Opaque cursor from a previous page's next_cursor"
    ),
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    from app.core.storage import utc_now

    try:
        windows = cw_service.list_windows(
            session,
            satellite_id=satellite_id,
            ground_station_id=ground_station_id,
            date=date,
            after_utc=utc_now() if upcoming else None,
            limit=limit,
            cursor=cursor,
        )
    except InvalidCursorError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_cursor",
                    "message": "The provided cursor is malformed.",
                }
            },
        )
    next_cursor = None
    if len(windows) == limit:
        next_cursor = encode_cursor(windows[-1]["aos_utc"], windows[-1]["id"])
    return {"contact_windows": windows, "next_cursor": next_cursor}
