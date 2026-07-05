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
    # Object-store keys (bytes live in R2/S3 or the local artifact dir).
    output_files: List[str]


class ArtifactRef(BaseModel):
    key: str
    # Time-limited signed URL, generated at read time.
    url: str


class ResultResponse(BaseModel):
    result: Result
    artifacts: List[ArtifactRef] = Field(default_factory=list)
