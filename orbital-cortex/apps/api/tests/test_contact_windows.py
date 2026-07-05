"""Contact-window correctness tests.

The independent-verification test recomputes elevation at Skyfield's reported
pass times using the raw sgp4 library plus hand-rolled TEME->ECEF->ENU math
(GMST rotation, WGS84 geodesy) - no Skyfield involved - and requires
agreement. This is the DoD for B4: our passes match an independent ephemeris
computation.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from sgp4.api import Satrec, jday

from app.services.contact_windows import compute_passes, est_downlink_mb

SNAPSHOT = json.loads(
    (Path(__file__).resolve().parents[3] / "simulator" / "tle_snapshot.json").read_text()
)
S1A = next(s for s in SNAPSHOT["satellites"] if s["id"] == "sat_sentinel_1a")

SVALBARD = {"lat": 78.2297, "lon": 15.3975, "alt_m": 450.0}
NY_HARBOR = {"lat": 40.6892, "lon": -74.0445, "alt_m": 10.0}

# Start propagation at the TLE epoch to keep SGP4 error small.
EPOCH = datetime.fromisoformat(S1A["tle_epoch"])


def _independent_elevation_deg(tle1, tle2, lat_deg, lon_deg, alt_m, when):
    """Elevation via raw sgp4 + GMST + WGS84 ENU. No Skyfield."""
    sat = Satrec.twoline2rv(tle1, tle2)
    jd, fr = jday(
        when.year, when.month, when.day,
        when.hour, when.minute, when.second + when.microsecond / 1e6,
    )
    error, r_teme, _v = sat.sgp4(jd, fr)
    assert error == 0, f"sgp4 error code {error}"

    # GMST (IAU 1982 / Vallado) rotates TEME into an Earth-fixed frame;
    # polar motion (~10 m) is ignored, fine for degree-level tolerance.
    t_ut1 = (jd + fr - 2451545.0) / 36525.0
    gmst_s = (
        67310.54841
        + (876600.0 * 3600.0 + 8640184.812866) * t_ut1
        + 0.093104 * t_ut1**2
        - 6.2e-6 * t_ut1**3
    ) % 86400.0
    gmst = gmst_s / 86400.0 * 2.0 * math.pi

    cos_g, sin_g = math.cos(gmst), math.sin(gmst)
    x = cos_g * r_teme[0] + sin_g * r_teme[1]
    y = -sin_g * r_teme[0] + cos_g * r_teme[1]
    z = r_teme[2]

    # Observer ECEF (WGS84 geodetic -> cartesian), km.
    a = 6378.137
    f = 1.0 / 298.257223563
    e2 = f * (2.0 - f)
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    n = a / math.sqrt(1.0 - e2 * math.sin(lat) ** 2)
    ox = (n + alt_m / 1000.0) * math.cos(lat) * math.cos(lon)
    oy = (n + alt_m / 1000.0) * math.cos(lat) * math.sin(lon)
    oz = (n * (1.0 - e2) + alt_m / 1000.0) * math.sin(lat)

    dx, dy, dz = x - ox, y - oy, z - oz
    # ENU components.
    east = -math.sin(lon) * dx + math.cos(lon) * dy
    north = (
        -math.sin(lat) * math.cos(lon) * dx
        - math.sin(lat) * math.sin(lon) * dy
        + math.cos(lat) * dz
    )
    up = (
        math.cos(lat) * math.cos(lon) * dx
        + math.cos(lat) * math.sin(lon) * dy
        + math.sin(lat) * dz
    )
    return math.degrees(math.asin(up / math.sqrt(east**2 + north**2 + up**2)))


def _passes(observer, min_elevation=10.0, hours=24.0):
    return compute_passes(
        S1A["tle_line1"], S1A["tle_line2"], S1A["name"],
        observer["lat"], observer["lon"], observer["alt_m"],
        min_elevation, EPOCH, hours,
    )


def test_passes_match_independent_sgp4_computation():
    passes = _passes(SVALBARD)
    assert passes, "Sentinel-1A must pass over Svalbard within 24h"

    for pass_ in passes[:5]:
        culmination = datetime.fromisoformat(pass_["culminate_utc"]).astimezone(timezone.utc)
        independent = _independent_elevation_deg(
            S1A["tle_line1"], S1A["tle_line2"],
            SVALBARD["lat"], SVALBARD["lon"], SVALBARD["alt_m"],
            culmination,
        )
        assert abs(independent - pass_["max_elevation_deg"]) < 1.0, (
            f"culmination elevation mismatch: skyfield={pass_['max_elevation_deg']}, "
            f"independent sgp4={independent:.2f}"
        )
        # At AOS the satellite must sit at the elevation mask (10 deg).
        aos = datetime.fromisoformat(pass_["aos_utc"]).astimezone(timezone.utc)
        aos_elevation = _independent_elevation_deg(
            S1A["tle_line1"], S1A["tle_line2"],
            SVALBARD["lat"], SVALBARD["lon"], SVALBARD["alt_m"],
            aos,
        )
        assert abs(aos_elevation - 10.0) < 1.0, f"AOS elevation {aos_elevation:.2f} != mask"


def test_known_sat_over_ny_harbor():
    """A polar-orbit SAR sat must pass over NY Harbor with plausible geometry."""
    passes = _passes(NY_HARBOR, hours=48.0)
    assert passes, "Sentinel-1A must pass over NY Harbor within 48h"
    for pass_ in passes:
        assert pass_["max_elevation_deg"] >= 10.0
        # LEO pass above a 10 deg mask lasts roughly 1-12 minutes.
        assert 30.0 <= pass_["duration_s"] <= 780.0
        assert pass_["aos_utc"] < pass_["culminate_utc"] < pass_["los_utc"]

    culmination = datetime.fromisoformat(passes[0]["culminate_utc"]).astimezone(timezone.utc)
    independent = _independent_elevation_deg(
        S1A["tle_line1"], S1A["tle_line2"],
        NY_HARBOR["lat"], NY_HARBOR["lon"], NY_HARBOR["alt_m"],
        culmination,
    )
    assert abs(independent - passes[0]["max_elevation_deg"]) < 1.0


def test_elevation_mask_filters_low_passes():
    low_mask = _passes(SVALBARD, min_elevation=5.0)
    high_mask = _passes(SVALBARD, min_elevation=10.0)

    # A stricter mask can only remove or shorten passes, never add them.
    assert len(high_mask) <= len(low_mask)
    assert all(p["max_elevation_deg"] >= 10.0 for p in high_mask)
    # Some passes peak between 5 and 10 degrees and must be excluded at 10.
    only_low = [p for p in low_mask if p["max_elevation_deg"] < 10.0]
    assert only_low, "expected sub-10-degree passes at a high-latitude station"
    # Same physical pass is shorter above a higher mask.
    high_by_culmination = {p["culminate_utc"]: p for p in high_mask}
    shared = [
        (low, high_by_culmination[low["culminate_utc"]])
        for low in low_mask
        if low["culminate_utc"] in high_by_culmination
    ]
    assert shared
    assert all(high["duration_s"] < low["duration_s"] for low, high in shared)


def test_pinned_snapshot_is_deterministic():
    first = _passes(SVALBARD)
    second = _passes(SVALBARD)
    assert first == second


def test_downlink_volume_estimate():
    # 520 Mbit/s over a 10-minute pass ~= 39 GB.
    assert est_downlink_mb(520, 600) == 39000.0
    passes = _passes(SVALBARD)
    for pass_ in passes:
        volume = est_downlink_mb(S1A["downlink_rate_mbps"], pass_["duration_s"])
        assert 1000.0 < volume < 60000.0, f"implausible downlink estimate {volume} MB"
