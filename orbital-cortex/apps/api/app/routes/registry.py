"""Ground station, satellite, and contact-window registry routes."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import node_registry
from app.db import get_db
from app.models.node import (
    ContactWindowsResponse,
    GroundStationsResponse,
    SatellitesResponse,
)
from app.services import contact_windows as cw_service

router = APIRouter(prefix="/v1", tags=["registry"])


@router.get("/ground-stations", response_model=GroundStationsResponse)
def list_ground_stations(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {"ground_stations": node_registry.list_ground_stations(session)}


@router.get("/satellites", response_model=SatellitesResponse)
def list_satellites(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {"satellites": node_registry.list_satellites(session)}


@router.get("/contact-windows", response_model=ContactWindowsResponse)
def list_contact_windows(
    satellite_id: Optional[str] = Query(default=None),
    ground_station_id: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None, description="AOS date, YYYY-MM-DD UTC"),
    upcoming: bool = Query(default=False, description="Only windows that have not ended"),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Reads exclusively from the precomputed cache; no propagation here.
    from app.core.storage import utc_now

    return {
        "contact_windows": cw_service.list_windows(
            session,
            satellite_id=satellite_id,
            ground_station_id=ground_station_id,
            date=date,
            after_utc=utc_now() if upcoming else None,
            limit=limit,
        )
    }
