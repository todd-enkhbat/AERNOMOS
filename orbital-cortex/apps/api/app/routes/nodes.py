"""Node API routes."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.core import node_registry
from app.db import get_db
from app.models.node import NodesResponse


router = APIRouter(prefix="/v1", tags=["nodes"])


@router.get("/nodes", response_model=NodesResponse)
def list_nodes(
    connection: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    return {
        "compute_nodes": node_registry.list_compute_nodes(connection),
        "ground_stations": node_registry.list_ground_stations(connection),
    }
