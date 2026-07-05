"""Canned NY Harbor SAR scene ingest (Group D1).

Real Sentinel-1 GRD scene processing happens offline once; committed assets
live under simulator/ny_harbor_scene/. Runtime jobs load from that pin — no
SNAP or live SAR dependency.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.storage import new_id, utc_now
from app.db.orm import Detection, Scene
from app.db.session import REPO_ROOT

SCENE_DIR = REPO_ROOT / "simulator" / "ny_harbor_scene"


def _read_json(name: str) -> Dict[str, Any]:
    with (SCENE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _bbox_to_polygon_wkt(bbox: List[float]) -> str:
    west, south, east, north = bbox
    return (
        f"POLYGON(({west} {south},{east} {south},"
        f"{east} {north},{west} {north},{west} {south}))"
    )


def ingest_canned_scene(session: Session, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Attach the pinned NY Harbor scene + detections to a completed job."""
    if job["job_type"] != "ship_detection":
        return None

    meta = _read_json("scene_meta.json")
    stac = _read_json("stac_item.json")
    geojson = _read_json("detections.geojson")

    existing = session.scalars(
        select(Scene).where(Scene.job_id == job["id"])
    ).one_or_none()
    if existing is not None:
        return get_scene(session, job["id"])

    scene_id = new_id("scene")
    bbox = job["area_of_interest"]["coordinates"]
    session.add(
        Scene(
            id=scene_id,
            job_id=job["id"],
            aoi=WKTElement(_bbox_to_polygon_wkt(bbox), srid=4326),
            captured_utc=meta["captured_utc"],
            sensor=meta["sensor"],
            mode=meta["mode"],
            resolution_m=float(meta["resolution_m"]),
            source=meta["source"],
            provenance=meta["provenance"],
            stac_item_id=stac.get("id"),
            cog_url=meta.get("cog_url"),
            created_at=utc_now(),
        )
    )
    session.flush()

    for index, feature in enumerate(geojson.get("features", []), start=1):
        coords = feature["geometry"]["coordinates"]
        lon, lat = float(coords[0]), float(coords[1])
        props = feature.get("properties", {})
        session.add(
            Detection(
                id=new_id("det"),
                scene_id=scene_id,
                geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                confidence=float(props.get("confidence", 0.5)),
                bbox={
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [lon - 0.002, lat - 0.002],
                            [lon + 0.002, lat - 0.002],
                            [lon + 0.002, lat + 0.002],
                            [lon - 0.002, lat + 0.002],
                            [lon - 0.002, lat - 0.002],
                        ]
                    ],
                },
                ais_correlated=bool(props.get("ais_correlated", False)),
                vessel_hint=props.get("vessel_type"),
                properties=props,
                detected_utc=meta["captured_utc"],
            )
        )
    session.flush()
    return get_scene(session, job["id"])


def get_scene(session: Session, job_id: str) -> Optional[Dict[str, Any]]:
    scene = session.scalars(select(Scene).where(Scene.job_id == job_id)).one_or_none()
    if scene is None:
        return None
    aoi_row = session.execute(
        select(func.ST_AsGeoJSON(Scene.aoi)).where(Scene.id == scene.id)
    ).scalar_one()
    return {
        "id": scene.id,
        "job_id": scene.job_id,
        "aoi": json.loads(aoi_row),
        "captured_utc": scene.captured_utc,
        "sensor": scene.sensor,
        "mode": scene.mode,
        "resolution_m": float(scene.resolution_m),
        "source": scene.source,
        "provenance": scene.provenance,
        "stac_item_id": scene.stac_item_id,
        "cog_url": scene.cog_url,
    }


def list_detections_geojson(session: Session, job_id: str) -> Dict[str, Any]:
    scene = session.scalars(select(Scene).where(Scene.job_id == job_id)).one_or_none()
    if scene is None:
        return {"type": "FeatureCollection", "features": []}

    rows = session.execute(
        select(
            Detection.id,
            func.ST_AsGeoJSON(Detection.geom).label("geom"),
            Detection.confidence,
            Detection.bbox,
            Detection.ais_correlated,
            Detection.vessel_hint,
            Detection.properties,
            Detection.detected_utc,
        ).where(Detection.scene_id == scene.id)
    ).all()

    features = []
    for row in rows:
        geometry = json.loads(row.geom)
        props = dict(row.properties or {})
        props.update(
            {
                "detection_id": row.id,
                "confidence": float(row.confidence),
                "ais_correlated": bool(row.ais_correlated),
                "vessel_hint": row.vessel_hint,
                "detected_utc": row.detected_utc,
                "dark_ship": not row.ais_correlated,
            }
        )
        features.append(
            {"type": "Feature", "geometry": geometry, "properties": props}
        )
    return {"type": "FeatureCollection", "features": features}


def bbox_query_detections(
    session: Session,
    job_id: str,
    west: float,
    south: float,
    east: float,
    north: float,
) -> List[str]:
    """Return detection ids within a WGS84 bbox (PostGIS &&)."""
    scene = session.scalars(select(Scene).where(Scene.job_id == job_id)).one_or_none()
    if scene is None:
        return []
    envelope = f"POLYGON(({west} {south},{east} {south},{east} {north},{west} {north},{west} {south}))"
    rows = session.execute(
        select(Detection.id).where(
            Detection.scene_id == scene.id,
            func.ST_Within(
                Detection.geom,
                func.ST_SetSRID(func.ST_GeomFromText(envelope), 4326),
            ),
        )
    ).all()
    return [row[0] for row in rows]
