"""Catalog search + MissionDataCandidate persistence."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog.base import DataCatalogProvider
from app.catalog.planetary_computer import PlanetaryComputerCatalog
from app.catalog.types import (
    DEFAULT_COLLECTIONS,
    DEFAULT_SEARCH_LIMIT,
    CatalogItem,
    CatalogSearchQuery,
)
from app.core.missions import geojson_to_wkt, geometry_to_geojson, utc_now
from app.db.mission_orm import Mission, MissionDataCandidate
from app.db.truth import TruthStatus
from app.models.provenance import (
    EXPLANATION_ESTIMATED,
    EXPLANATION_PROVIDER_STAC,
    provenanced,
)

# Default lookback when a mission has no start/end times.
DEFAULT_LOOKBACK_DAYS = 30


def default_catalog_provider() -> DataCatalogProvider:
    """Return the active catalog provider.

    Phase R: ``CATALOG_MODE=fixture`` (or settings.catalog_mode) serves pinned
    real STAC FeatureCollections so accelerator demos do not depend on live
    Planetary Computer connectivity. Default remains ``live``.
    """
    from app.core.config import get_settings

    mode = (get_settings().catalog_mode or "live").strip().lower()
    if mode in {"fixture", "fixtures", "pinned", "demo"}:
        from app.catalog.fixture_provider import FixtureCatalogProvider

        return FixtureCatalogProvider()
    return PlanetaryComputerCatalog()


def _bbox_from_geojson(area: Dict[str, Any]) -> Optional[tuple[float, float, float, float]]:
    geom_type = area.get("type")
    if geom_type == "bbox":
        coords = area.get("coordinates") or []
        if len(coords) == 4:
            west, south, east, north = (float(c) for c in coords)
            return (west, south, east, north)
        return None
    if geom_type == "Polygon":
        ring = (area.get("coordinates") or [[]])[0]
        if not ring:
            return None
        poly_lons = [float(p[0]) for p in ring]
        poly_lats = [float(p[1]) for p in ring]
        return (min(poly_lons), min(poly_lats), max(poly_lons), max(poly_lats))
    if geom_type == "MultiPolygon":
        polygons = area.get("coordinates") or []
        multi_lons: List[float] = []
        multi_lats: List[float] = []
        for polygon in polygons:
            for ring in polygon:
                for point in ring:
                    multi_lons.append(float(point[0]))
                    multi_lats.append(float(point[1]))
        if not multi_lons:
            return None
        return (min(multi_lons), min(multi_lats), max(multi_lons), max(multi_lats))
    return None


def _intersects_from_geojson(area: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    geom_type = area.get("type")
    if geom_type in {"Polygon", "MultiPolygon"}:
        return {"type": geom_type, "coordinates": area["coordinates"]}
    if geom_type == "bbox":
        bbox = _bbox_from_geojson(area)
        if bbox is None:
            return None
        west, south, east, north = bbox
        return {
            "type": "Polygon",
            "coordinates": [
                [
                    [west, south],
                    [east, south],
                    [east, north],
                    [west, north],
                    [west, south],
                ]
            ],
        }
    return None


def build_search_query_for_mission(
    db: Session,
    mission: Mission,
    *,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    collections: Optional[Sequence[str]] = None,
    limit: Optional[int] = None,
) -> CatalogSearchQuery:
    aoi = geometry_to_geojson(db, mission.area_of_interest)
    intersects = _intersects_from_geojson(aoi)
    bbox = _bbox_from_geojson(aoi) if intersects is None else None

    now = utc_now()
    query_start = start if start is not None else mission.start_time
    query_end = end if end is not None else mission.end_time
    if query_start is None and query_end is None:
        query_end = now
        query_start = now - timedelta(days=DEFAULT_LOOKBACK_DAYS)

    return CatalogSearchQuery(
        collections=list(collections) if collections else list(DEFAULT_COLLECTIONS),
        start=query_start,
        end=query_end,
        bbox=bbox,
        intersects=intersects,
        limit=limit if limit is not None else DEFAULT_SEARCH_LIMIT,
    )


def candidate_to_dict(
    db: Session, row: MissionDataCandidate
) -> Dict[str, Any]:
    assets: List[Any] = []
    meta = row.asset_metadata or {}
    if isinstance(meta, dict):
        assets = meta.get("assets") or []
    source_timestamp = row.source_timestamp.isoformat()
    truth = (
        row.truth_status.value
        if hasattr(row.truth_status, "value")
        else str(row.truth_status)
    )
    provider_label = row.source_provider
    return {
        "id": str(row.id),
        "mission_id": str(row.mission_id),
        "source_provider": row.source_provider,
        "collection": row.collection,
        "external_item_id": row.external_item_id,
        "acquisition_time": provenanced(
            row.acquisition_time.isoformat(),
            TruthStatus.PROVIDER_REPORTED,
            source=provider_label,
            retrieved_at=source_timestamp,
            explanation=EXPLANATION_PROVIDER_STAC,
        ),
        "footprint": geometry_to_geojson(db, row.footprint),
        "asset_metadata": meta,
        "available_assets": [
            {
                "key": asset.get("key"),
                "media_type": asset.get("media_type"),
                "roles": asset.get("roles") or [],
                "title": asset.get("title"),
            }
            for asset in assets
            if isinstance(asset, dict)
        ],
        "estimated_size_bytes": provenanced(
            row.estimated_size_bytes,
            TruthStatus.ESTIMATED,
            source=provider_label,
            retrieved_at=source_timestamp,
            method="STAC asset size heuristic",
            explanation=EXPLANATION_ESTIMATED,
        )
        if row.estimated_size_bytes is not None
        else None,
        "source_url": row.source_url,
        "source_timestamp": source_timestamp,
        "truth_status": truth,
        "created_at": row.created_at.isoformat(),
    }


def upsert_candidates(
    db: Session,
    mission_id: uuid.UUID,
    items: Sequence[CatalogItem],
    *,
    retrieved_at: Optional[datetime] = None,
) -> List[MissionDataCandidate]:
    """Insert catalog items; skip duplicates for (mission, provider, item id)."""
    if not items:
        return []

    now = retrieved_at or utc_now()
    existing = list(
        db.scalars(
            select(MissionDataCandidate).where(
                MissionDataCandidate.mission_id == mission_id
            )
        ).all()
    )
    seen = {(row.source_provider, row.external_item_id) for row in existing}

    for item in items:
        key = (item.source_provider, item.external_item_id)
        if key in seen:
            continue
        wkt = geojson_to_wkt(item.footprint)
        db.add(
            MissionDataCandidate(
                id=uuid.uuid4(),
                mission_id=mission_id,
                source_provider=item.source_provider,
                collection=item.collection,
                external_item_id=item.external_item_id,
                acquisition_time=item.acquisition_time,
                footprint=WKTElement(wkt, srid=4326),
                asset_metadata=item.asset_metadata_payload(),
                estimated_size_bytes=item.estimated_size_bytes,
                source_url=item.source_url,
                source_timestamp=now,
                # Catalog metadata is provider-reported from STAC.
                truth_status=TruthStatus.PROVIDER_REPORTED,
                created_at=now,
            )
        )
        seen.add(key)

    db.flush()

    provider_ids = {(item.source_provider, item.external_item_id) for item in items}
    refreshed = list(
        db.scalars(
            select(MissionDataCandidate).where(
                MissionDataCandidate.mission_id == mission_id
            )
        ).all()
    )
    matched = [
        row
        for row in refreshed
        if (row.source_provider, row.external_item_id) in provider_ids
    ]
    matched.sort(key=lambda row: row.acquisition_time, reverse=True)
    return matched


def list_candidates(db: Session, mission_id: uuid.UUID) -> List[MissionDataCandidate]:
    return list(
        db.scalars(
            select(MissionDataCandidate)
            .where(MissionDataCandidate.mission_id == mission_id)
            .order_by(MissionDataCandidate.acquisition_time.desc())
        ).all()
    )


def discover_for_mission(
    db: Session,
    mission: Mission,
    *,
    provider: Optional[DataCatalogProvider] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    collections: Optional[Sequence[str]] = None,
    limit: Optional[int] = None,
) -> List[MissionDataCandidate]:
    """Search the catalog and persist candidates for a mission."""
    catalog = provider or default_catalog_provider()
    query = build_search_query_for_mission(
        db,
        mission,
        start=start,
        end=end,
        collections=collections,
        limit=limit,
    )
    items = catalog.search(query)
    return upsert_candidates(db, mission.id, items)
