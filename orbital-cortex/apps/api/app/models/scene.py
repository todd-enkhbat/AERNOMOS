"""Scene and detection response models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SceneResponse(BaseModel):
    scene: Optional[Dict[str, Any]] = None


class DetectionsGeoJsonResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
