"""Node API routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import node_registry
from app.db import get_db
from app.models.node import NodesResponse

router = APIRouter(prefix="/v1", tags=["nodes"])


@router.get(
    "/nodes",
    response_model=NodesResponse,
    summary="List compute nodes and ground stations",
)
def list_nodes(
    session: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {
        "compute_nodes": node_registry.list_compute_nodes(session),
        "ground_stations": node_registry.list_ground_stations(session),
    }
