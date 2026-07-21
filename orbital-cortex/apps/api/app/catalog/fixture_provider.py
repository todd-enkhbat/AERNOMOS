"""Pinned STAC fixture catalog provider (Phase R).

Loads real Planetary Computer STAC items that were captured once and checked
into ``app/catalog/fixtures/``. Never invents scene IDs or acquisition times —
items must correspond to actual acquisitions. Used by default for accelerator
demos so a live pitch does not depend on third-party network availability.

``CATALOG_MODE=live`` / ``--live`` re-enables PlanetaryComputerCatalog.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from app.catalog.errors import CatalogNotFoundError
from app.catalog.planetary_computer import PROVIDER_ID, STAC_API_URL
from app.catalog.types import CatalogAsset, CatalogItem, CatalogSearchQuery

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _bbox_of_geometry(geometry: Dict[str, Any]) -> Optional[tuple[float, float, float, float]]:
    coords: List[float] = []

    def walk(node: Any) -> None:
        if isinstance(node, (list, tuple)) and len(node) >= 2 and isinstance(node[0], (int, float)):
            coords.extend([float(node[0]), float(node[1])])
            return
        if isinstance(node, (list, tuple)):
            for child in node:
                walk(child)

    walk(geometry.get("coordinates"))
    if len(coords) < 4:
        return None
    lons = coords[0::2]
    lats = coords[1::2]
    return (min(lons), min(lats), max(lons), max(lats))


def _bboxes_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def _query_bbox(query: CatalogSearchQuery) -> Optional[tuple[float, float, float, float]]:
    if query.bbox is not None:
        west, south, east, north = query.bbox
        return (float(west), float(south), float(east), float(north))
    if query.intersects is not None:
        return _bbox_of_geometry(query.intersects)
    return None


def feature_to_catalog_item(
    feature: Dict[str, Any],
    *,
    source_provider: str = PROVIDER_ID,
    fixture_meta: Optional[Dict[str, Any]] = None,
) -> CatalogItem:
    """Map a GeoJSON STAC Feature dict to CatalogItem."""
    props = dict(feature.get("properties") or {})
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict) or not geometry.get("type"):
        raise ValueError(f"Fixture feature {feature.get('id')} missing geometry")

    acquisition = _parse_datetime(props.get("datetime") or props.get("start_datetime"))
    collection = str(feature.get("collection") or props.get("collection") or "")
    item_id = str(feature.get("id") or "")

    assets_out: List[CatalogAsset] = []
    reported_sizes: List[int] = []
    for key, asset in (feature.get("assets") or {}).items():
        if not isinstance(asset, dict):
            continue
        size = asset.get("file:size")
        size_int: Optional[int] = None
        if size is not None:
            try:
                size_int = int(size)
                if size_int > 0:
                    reported_sizes.append(size_int)
            except (TypeError, ValueError):
                size_int = None
        assets_out.append(
            CatalogAsset(
                key=str(key),
                href=asset.get("href"),
                media_type=asset.get("type") or asset.get("media_type"),
                roles=list(asset.get("roles") or []),
                title=asset.get("title"),
                size_bytes=size_int,
            )
        )

    self_href = None
    for link in feature.get("links") or []:
        if isinstance(link, dict) and link.get("rel") == "self" and link.get("href"):
            self_href = str(link["href"])
            break
    if not self_href and collection and item_id:
        self_href = f"{STAC_API_URL}/collections/{collection}/items/{item_id}"

    properties = {
        k: v
        for k, v in props.items()
        if k
        in {
            "platform",
            "constellation",
            "instruments",
            "sar:instrument_mode",
            "sar:product_type",
            "sat:orbit_state",
            "eo:cloud_cover",
            "s2:product_type",
            "s2:mgrs_tile",
        }
    }
    if fixture_meta:
        properties["nomos_fixture"] = {
            "pinned": True,
            "captured_at": fixture_meta.get("captured_at"),
            "source": fixture_meta.get("source") or source_provider,
            "note": fixture_meta.get("note"),
        }

    return CatalogItem(
        source_provider=source_provider,
        collection=collection,
        external_item_id=item_id,
        acquisition_time=acquisition,
        footprint=geometry,
        assets=assets_out,
        estimated_size_bytes=sum(reported_sizes) if reported_sizes else None,
        size_is_estimated=False,
        source_url=self_href,
        properties=properties,
    )


def load_fixture_file(path: Path) -> tuple[List[CatalogItem], Dict[str, Any]]:
    """Load a FeatureCollection fixture file into CatalogItems + meta."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = dict(payload.get("nomos_fixture_meta") or {})
    meta.setdefault("fixture_file", path.name)
    items = [
        feature_to_catalog_item(feat, fixture_meta=meta)
        for feat in payload.get("features") or []
        if isinstance(feat, dict)
    ]
    return items, meta


def load_all_fixtures(directory: Optional[Path] = None) -> List[CatalogItem]:
    root = directory or FIXTURES_DIR
    items: List[CatalogItem] = []
    for path in sorted(root.glob("demo*.json")):
        file_items, _ = load_fixture_file(path)
        items.extend(file_items)
    return items


class FixtureCatalogProvider:
    """Offline catalog provider backed by pinned real STAC FeatureCollections."""

    provider_id = PROVIDER_ID

    def __init__(
        self,
        *,
        fixtures_dir: Optional[Path] = None,
        items: Optional[Sequence[CatalogItem]] = None,
    ) -> None:
        self.fixtures_dir = fixtures_dir or FIXTURES_DIR
        self._items: List[CatalogItem] = (
            list(items) if items is not None else load_all_fixtures(self.fixtures_dir)
        )

    def search(self, query: CatalogSearchQuery) -> List[CatalogItem]:
        collections = {c.lower() for c in query.collections}
        qbbox = _query_bbox(query)
        matched: List[CatalogItem] = []
        for item in self._items:
            if collections and item.collection.lower() not in collections:
                continue
            if query.start is not None and item.acquisition_time < query.start:
                continue
            if query.end is not None and item.acquisition_time > query.end:
                continue
            if qbbox is not None:
                ibox = _bbox_of_geometry(item.footprint)
                if ibox is None or not _bboxes_overlap(qbbox, ibox):
                    continue
            matched.append(item)
        return matched[: query.limit]

    def get_item(self, collection: str, external_item_id: str) -> CatalogItem:
        for item in self._items:
            if (
                item.collection == collection
                and item.external_item_id == external_item_id
            ):
                return item
        raise CatalogNotFoundError(
            f"Fixture catalog has no item {collection}/{external_item_id}."
        )

    def get_assets(self, collection: str, external_item_id: str) -> List[CatalogAsset]:
        return list(self.get_item(collection, external_item_id).assets)


def fixture_path_for_name(name: str) -> Path:
    path = FIXTURES_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Catalog fixture not found: {path}")
    return path


def items_from_fixture_name(name: str) -> List[CatalogItem]:
    items, _ = load_fixture_file(fixture_path_for_name(name))
    return items


# Keep Iterable imported for type clarity in callers.
_ = Iterable
