"""Shared catalog search / item types."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from pydantic import BaseModel, Field, field_validator

# Default Microsoft Planetary Computer collection for Sentinel-1 GRD.
DEFAULT_COLLECTIONS: tuple[str, ...] = ("sentinel-1-grd",)
MAX_SEARCH_LIMIT = 50
DEFAULT_SEARCH_LIMIT = 20

BBox = Tuple[float, float, float, float]
GeoJSONGeometry = Dict[str, Any]


class CatalogAsset(BaseModel):
    key: str
    href: Optional[str] = None
    media_type: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    size_bytes: Optional[int] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class CatalogItem(BaseModel):
    source_provider: str
    collection: str
    external_item_id: str
    acquisition_time: datetime
    footprint: GeoJSONGeometry
    assets: List[CatalogAsset] = Field(default_factory=list)
    estimated_size_bytes: Optional[int] = None
    size_is_estimated: bool = False
    source_url: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    def asset_metadata_payload(self) -> Dict[str, Any]:
        return {
            "assets": [
                {
                    "key": asset.key,
                    "href": asset.href,
                    "media_type": asset.media_type,
                    "roles": asset.roles,
                    "title": asset.title,
                    "size_bytes": asset.size_bytes,
                    **({"extra": asset.extra} if asset.extra else {}),
                }
                for asset in self.assets
            ],
            "properties": self.properties,
            "size_is_estimated": self.size_is_estimated,
        }


class CatalogSearchQuery(BaseModel):
    """STAC search inputs: AOI + datetime + collections + limit."""

    collections: List[str] = Field(default_factory=lambda: list(DEFAULT_COLLECTIONS))
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    bbox: Optional[BBox] = None
    intersects: Optional[GeoJSONGeometry] = None
    limit: int = DEFAULT_SEARCH_LIMIT

    @field_validator("limit")
    @classmethod
    def _cap_limit(cls, value: int) -> int:
        if value < 1:
            raise ValueError("limit must be at least 1")
        return min(value, MAX_SEARCH_LIMIT)

    @field_validator("collections")
    @classmethod
    def _require_collections(cls, value: Sequence[str]) -> List[str]:
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if not cleaned:
            return list(DEFAULT_COLLECTIONS)
        return cleaned

    def datetime_interval(self) -> Optional[str]:
        """STAC datetime string (ISO start/end or open-ended)."""
        if self.start is None and self.end is None:
            return None
        start = self.start.isoformat().replace("+00:00", "Z") if self.start else ".."
        end = self.end.isoformat().replace("+00:00", "Z") if self.end else ".."
        if self.start and self.end:
            return f"{start}/{end}"
        if self.start:
            return f"{start}/.."
        return f"../{end}"
