"""Result model definitions."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Result(BaseModel):
    id: str
    job_id: str
    summary: str
    confidence: float = Field(ge=0, le=1)
    geojson: Dict[str, Any]
    output_files: List[str]


class ResultResponse(BaseModel):
    result: Result
