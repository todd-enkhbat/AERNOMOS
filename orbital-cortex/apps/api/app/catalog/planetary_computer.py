"""Microsoft Planetary Computer STAC catalog provider.

Keyless search via pystac-client against:
https://planetarycomputer.microsoft.com/api/stac/v1

Primary collection: sentinel-1-grd. Optional: sentinel-2-l2a.
Never fabricates catalog items — upstream failures raise typed errors.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.catalog import cache as catalog_cache
from app.catalog.errors import (
    CatalogNotFoundError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.catalog.types import CatalogAsset, CatalogItem, CatalogSearchQuery

PROVIDER_ID = "microsoft-planetary-computer"
STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
DEFAULT_TIMEOUT_SECONDS = 30.0


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if not value:
        raise CatalogUnavailableError("STAC item missing acquisition datetime.")
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _asset_size_bytes(asset_extra: Dict[str, Any]) -> Optional[int]:
    for key in ("file:size", "raster:size", "size", "sozip:filesize"):
        raw = asset_extra.get(key)
        if raw is None:
            continue
        try:
            size = int(raw)
        except (TypeError, ValueError):
            continue
        if size > 0:
            return size
    return None


def _item_self_href(item: Any) -> Optional[str]:
    links = getattr(item, "links", None) or []
    for link in links:
        rel = getattr(link, "rel", None)
        href = getattr(link, "href", None)
        if rel == "self" and href:
            return str(href)
    collection = getattr(item, "collection", None) or ""
    item_id = getattr(item, "id", None) or ""
    if collection and item_id:
        return f"{STAC_API_URL}/collections/{collection}/items/{item_id}"
    return None


def stac_item_to_catalog_item(item: Any, *, source_provider: str = PROVIDER_ID) -> CatalogItem:
    """Map a pystac Item (or duck-typed object) to CatalogItem."""
    geometry = getattr(item, "geometry", None)
    if not isinstance(geometry, dict) or not geometry.get("type"):
        raise CatalogUnavailableError(
            f"STAC item {getattr(item, 'id', '?')} missing footprint geometry."
        )

    props = dict(getattr(item, "properties", None) or {})
    acquisition = _parse_datetime(props.get("datetime") or props.get("start_datetime"))

    assets_out: List[CatalogAsset] = []
    reported_sizes: List[int] = []
    raw_assets = getattr(item, "assets", None) or {}
    for key, asset in raw_assets.items():
        extra = dict(getattr(asset, "extra_fields", None) or {})
        # pystac Asset also exposes to_dict() fields beyond href/media_type/roles.
        to_dict = getattr(asset, "to_dict", None)
        if callable(to_dict):
            payload = to_dict()
            for skip in ("href", "type", "roles", "title"):
                payload.pop(skip, None)
            extra.update(payload)
        size = _asset_size_bytes(extra)
        if size is not None:
            reported_sizes.append(size)
        roles = list(getattr(asset, "roles", None) or [])
        assets_out.append(
            CatalogAsset(
                key=str(key),
                href=getattr(asset, "href", None),
                media_type=getattr(asset, "media_type", None),
                roles=roles,
                title=getattr(asset, "title", None),
                size_bytes=size,
                extra={
                    k: v
                    for k, v in extra.items()
                    if k not in {"href", "type", "roles", "title"}
                },
            )
        )

    estimated_size: Optional[int] = None
    size_is_estimated = False
    if reported_sizes:
        estimated_size = sum(reported_sizes)
    else:
        # No provider size — leave null rather than inventing megabytes.
        estimated_size = None

    collection = getattr(item, "collection", None) or props.get("collection") or ""
    return CatalogItem(
        source_provider=source_provider,
        collection=str(collection),
        external_item_id=str(item.id),
        acquisition_time=acquisition,
        footprint=geometry,
        assets=assets_out,
        estimated_size_bytes=estimated_size,
        size_is_estimated=size_is_estimated,
        source_url=_item_self_href(item),
        properties={
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
            }
        },
    )


class PlanetaryComputerCatalog:
    """Live Microsoft Planetary Computer STAC search."""

    provider_id = PROVIDER_ID

    def __init__(
        self,
        *,
        api_url: str = STAC_API_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        use_cache: bool = True,
    ) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
        self.use_cache = use_cache

    def _open_client(self) -> Any:
        try:
            from pystac_client import Client
        except ImportError as exc:
            raise CatalogUnavailableError(
                "pystac-client is not installed; cannot search Planetary Computer."
            ) from exc
        try:
            return Client.open(
                self.api_url,
                timeout=self.timeout_seconds,
            )
        except Exception as exc:
            raise CatalogUnavailableError(
                f"Could not open Planetary Computer STAC API: {exc}"
            ) from exc

    def _search_kwargs(self, query: CatalogSearchQuery) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "collections": query.collections,
            "max_items": query.limit,
        }
        interval = query.datetime_interval()
        if interval:
            kwargs["datetime"] = interval
        if query.intersects is not None:
            kwargs["intersects"] = query.intersects
        elif query.bbox is not None:
            kwargs["bbox"] = list(query.bbox)
        return kwargs

    def _cache_payload(self, query: CatalogSearchQuery) -> Dict[str, Any]:
        return {
            "provider": self.provider_id,
            "api_url": self.api_url,
            "collections": query.collections,
            "datetime": query.datetime_interval(),
            "bbox": list(query.bbox) if query.bbox else None,
            "intersects": query.intersects,
            "limit": query.limit,
        }

    def search(self, query: CatalogSearchQuery) -> List[CatalogItem]:
        cache_key = catalog_cache.cache_key("pc-search", self._cache_payload(query))
        if self.use_cache:
            cached = catalog_cache.cache_get(cache_key)
            if cached:
                try:
                    payload = json.loads(cached)
                    return [CatalogItem.model_validate(row) for row in payload]
                except Exception:
                    pass

        client = self._open_client()
        kwargs = self._search_kwargs(query)
        try:
            search = client.search(**kwargs)
            raw_items = list(search.items())
        except Exception as exc:
            message = str(exc).lower()
            if "429" in message or "rate" in message:
                raise CatalogRateLimitedError(
                    "Planetary Computer STAC rate-limited the search."
                ) from exc
            if "404" in message or "not found" in message:
                raise CatalogNotFoundError(
                    f"Planetary Computer collection or search not found: {exc}"
                ) from exc
            raise CatalogUnavailableError(
                f"Planetary Computer STAC search failed: {exc}"
            ) from exc

        items = [stac_item_to_catalog_item(item) for item in raw_items]
        if self.use_cache and items:
            catalog_cache.cache_set(
                cache_key,
                json.dumps([item.model_dump(mode="json") for item in items]),
            )
        return items

    def get_item(self, collection: str, external_item_id: str) -> CatalogItem:
        client = self._open_client()
        try:
            item = client.get_collection(collection).get_item(external_item_id)
        except Exception as exc:
            message = str(exc).lower()
            if "404" in message or "not found" in message:
                raise CatalogNotFoundError(
                    f"STAC item not found: {collection}/{external_item_id}"
                ) from exc
            raise CatalogUnavailableError(
                f"Failed to fetch STAC item {collection}/{external_item_id}: {exc}"
            ) from exc
        if item is None:
            raise CatalogNotFoundError(
                f"STAC item not found: {collection}/{external_item_id}"
            )
        return stac_item_to_catalog_item(item)

    def get_assets(
        self, collection: str, external_item_id: str
    ) -> List[CatalogAsset]:
        return self.get_item(collection, external_item_id).assets
