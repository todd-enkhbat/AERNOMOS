"""Deterministic mock inference results."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.storage import new_id


SHIP_DETECTIONS: List[Tuple[float, float, float]] = [
    (-74.0451, 40.6892, 0.94),
    (-74.0203, 40.7001, 0.89),
    (-74.0042, 40.7128, 0.91),
    (-73.9857, 40.7045, 0.87),
    (-74.0724, 40.6413, 0.9),
    (-74.1016, 40.6072, 0.86),
    (-73.9609, 40.7421, 0.83),
    (-74.1588, 40.5468, 0.85),
    (-74.0133, 40.6554, 0.92),
    (-73.9345, 40.7831, 0.8),
    (-74.1852, 40.512, 0.78),
    (-73.8891, 40.8043, 0.82),
    (-74.0368, 40.5798, 0.88),
    (-73.9754, 40.633, 0.84),
    (-74.2261, 40.5008, 0.79),
    (-73.9442, 40.6795, 0.81),
    (-74.0698, 40.7293, 0.86),
]


def generate_mock_result(job: Dict[str, Any]) -> Dict[str, Any]:
    if job["job_type"] == "ship_detection":
        return _ship_detection_result(job)
    if job["job_type"] == "crop_health":
        return _crop_health_result(job)
    if job["job_type"] == "disaster_response":
        return _disaster_response_result(job)
    raise ValueError(f"Unsupported job type {job['job_type']}")


def _ship_detection_result(job: Dict[str, Any]) -> Dict[str, Any]:
    features = []
    for index, (longitude, latitude, confidence) in enumerate(SHIP_DETECTIONS, start=1):
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "properties": {
                    "detection_id": f"vessel_{index:02d}",
                    "class": "vessel",
                    "confidence": confidence,
                    "length_m_estimate": 35 + (index % 7) * 12,
                },
            }
        )
    return {
        "id": new_id("res"),
        "job_id": job["id"],
        "summary": "Detected 17 likely vessels in New York Harbor.",
        "confidence": 0.91,
        "geojson": {
            "type": "FeatureCollection",
            "features": features,
        },
        "output_files": [
            f"mock://results/{job['id']}/ship_detections.geojson",
            f"mock://results/{job['id']}/summary.json",
        ],
    }


def _crop_health_result(job: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": new_id("res"),
        "job_id": job["id"],
        "summary": (
            "Simulated crop analysis found moderate stress across 14% of "
            "the requested area, concentrated near the western edge."
        ),
        "confidence": 0.84,
        "geojson": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-120.9, 36.4],
                                [-120.6, 36.4],
                                [-120.6, 36.8],
                                [-120.9, 36.8],
                                [-120.9, 36.4],
                            ]
                        ],
                    },
                    "properties": {
                        "class": "moderate_crop_stress",
                        "confidence": 0.84,
                    },
                }
            ],
        },
        "output_files": [
            f"mock://results/{job['id']}/crop_health.geojson",
            f"mock://results/{job['id']}/stress_summary.json",
        ],
    }


def _disaster_response_result(job: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": new_id("res"),
        "job_id": job["id"],
        "summary": (
            "Simulated disaster response pass identified likely flood extent "
            "in low-lying zones with three priority review areas."
        ),
        "confidence": 0.88,
        "geojson": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-89.94, 30.03],
                    },
                    "properties": {
                        "class": "priority_review_area",
                        "confidence": 0.88,
                    },
                }
            ],
        },
        "output_files": [
            f"mock://results/{job['id']}/flood_extent.geojson",
            f"mock://results/{job['id']}/response_summary.json",
        ],
    }
