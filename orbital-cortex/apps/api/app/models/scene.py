"""Scene and detection response models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class SceneResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scene": {
                    "id": "scene_6e2a9c4f1b8d",
                    "job_id": "job_9f2c41d3a8b7",
                    "aoi": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-74.3, 40.3],
                                [-73.5, 40.3],
                                [-73.5, 41.0],
                                [-74.3, 41.0],
                                [-74.3, 40.3],
                            ]
                        ],
                    },
                    "captured_utc": "2026-06-15T10:42:00+00:00",
                    "sensor": "Sentinel-1",
                    "mode": "IW GRD",
                    "resolution_m": 10.0,
                    "source": "simulator/ny_harbor_scene",
                    "provenance": (
                        "Canned Sentinel-1 IW GRD chip over New York Harbor. "
                        "Offline SNAP-style processing pin; not live SAR."
                    ),
                    "stac_item_id": "S1A_IW_GRDH_NY_HARBOR_DEMO",
                    "cog_url": "mock://scenes/ny_harbor/backscatter.tif",
                }
            }
        }
    )

    scene: Optional[Dict[str, Any]] = None


class DetectionsGeoJsonResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
