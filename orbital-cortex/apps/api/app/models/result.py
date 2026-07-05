"""Result model definitions."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field
from pydantic.config import JsonDict

# Canonical NY Harbor demo result, reused by the OpenAPI examples here and
# in app.models.job.
EXAMPLE_RESULT: JsonDict = {
    "id": "res_3c7d91e5b2a4",
    "job_id": "job_9f2c41d3a8b7",
    "summary": "Detected 17 vessels in New York Harbor.",
    "confidence": 0.91,
    "geojson": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-74.045, 40.63]},
                "properties": {"class": "cargo", "confidence": 0.94, "simulated": True},
            }
        ],
    },
    "output_files": [
        "results/job_9f2c41d3a8b7/detections.geojson",
        "results/job_9f2c41d3a8b7/summary.json",
    ],
}


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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": EXAMPLE_RESULT,
                "artifacts": [
                    {
                        "key": "results/job_9f2c41d3a8b7/detections.geojson",
                        "url": (
                            "https://api.orbital-cortex.example/v1/artifacts/"
                            "results/job_9f2c41d3a8b7/detections.geojson"
                            "?expires=1783700000&signature=8c1f2ab90d374e6c"
                        ),
                    }
                ],
            }
        }
    )

    result: Result
    artifacts: List[ArtifactRef] = Field(default_factory=list)
