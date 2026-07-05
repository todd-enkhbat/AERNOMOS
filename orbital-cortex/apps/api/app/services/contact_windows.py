"""SGP4-propagated contact windows via Skyfield.

Computes real AOS / culminate / LOS passes for (satellite, ground station)
pairs, applies the station elevation mask, and estimates downlink volume
from the satellite's X-band rate and the pass duration.

Propagation is CPU-bound: never call compute_passes() on the request path.
The ARQ task in app/workers/passes.py precomputes into the contact_windows
table, which requests read from.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from skyfield.api import EarthSatellite, load, wgs84
from sqlalchemy import delete, select, tuple_
from sqlalchemy.orm import Session

from app.core.pagination import decode_cursor
from app.core.storage import new_id, utc_now
from app.db.orm import ContactWindow, GroundStation, Satellite

_timescale = load.timescale()  # builtin data; no network


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def est_downlink_mb(rate_mbps: float, duration_s: float) -> float:
    """Megabytes downlinked over a pass: rate (megabits/s) x seconds / 8."""
    return round(rate_mbps * duration_s / 8.0, 1)


def compute_passes(
    tle_line1: str,
    tle_line2: str,
    satellite_name: str,
    latitude: float,
    longitude: float,
    altitude_m: float,
    min_elevation_deg: float,
    start_utc: datetime,
    horizon_hours: float,
) -> List[Dict[str, Any]]:
    """All complete passes (AOS -> LOS) above the elevation mask in the horizon."""
    satellite = EarthSatellite(tle_line1, tle_line2, satellite_name, _timescale)
    observer = wgs84.latlon(latitude, longitude, elevation_m=altitude_m)
    t0 = _timescale.from_datetime(start_utc.astimezone(timezone.utc))
    t1 = _timescale.from_datetime(
        (start_utc + timedelta(hours=horizon_hours)).astimezone(timezone.utc)
    )
    times, events = satellite.find_events(
        observer, t0, t1, altitude_degrees=min_elevation_deg
    )

    passes: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    for time, event in zip(times, events):
        if event == 0:  # AOS (rise above mask)
            current = {"aos": time}
        elif event == 1 and "aos" in current:  # culmination
            current["culminate"] = time
        elif event == 2 and "aos" in current and "culminate" in current:  # LOS
            aos_dt = current["aos"].utc_datetime()
            cul_dt = current["culminate"].utc_datetime()
            los_dt = time.utc_datetime()
            alt, _az, _distance = (satellite - observer).at(current["culminate"]).altaz()
            passes.append(
                {
                    "aos_utc": _iso(aos_dt),
                    "culminate_utc": _iso(cul_dt),
                    "los_utc": _iso(los_dt),
                    "max_elevation_deg": round(float(alt.degrees), 2),
                    "duration_s": round((los_dt - aos_dt).total_seconds(), 1),
                }
            )
            current = {}
    return passes


def precompute_windows(
    session: Session,
    start_utc: Optional[datetime] = None,
    horizon_hours: float = 48.0,
) -> int:
    """Compute and cache passes for every (satellite, ground station) pair.

    Replaces any previously cached rows in the covered date range so the
    cache stays deterministic for a given TLE snapshot and horizon.
    """
    start = start_utc or datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )
    satellites = session.scalars(select(Satellite)).all()
    stations = session.scalars(select(GroundStation)).all()

    dates_covered = {
        (start + timedelta(hours=h)).date().isoformat()
        for h in range(0, int(horizon_hours) + 1)
    }

    created = 0
    for satellite in satellites:
        for station in stations:
            session.execute(
                delete(ContactWindow).where(
                    ContactWindow.satellite_id == satellite.id,
                    ContactWindow.ground_station_id == station.id,
                    ContactWindow.date.in_(dates_covered),
                )
            )
            for pass_ in compute_passes(
                satellite.tle_line1,
                satellite.tle_line2,
                satellite.name,
                station.latitude,
                station.longitude,
                station.altitude_m,
                station.min_elevation_deg,
                start,
                horizon_hours,
            ):
                session.add(
                    ContactWindow(
                        id=new_id("cw"),
                        satellite_id=satellite.id,
                        ground_station_id=station.id,
                        date=pass_["aos_utc"][:10],
                        aos_utc=pass_["aos_utc"],
                        culminate_utc=pass_["culminate_utc"],
                        los_utc=pass_["los_utc"],
                        max_elevation_deg=pass_["max_elevation_deg"],
                        duration_s=pass_["duration_s"],
                        est_downlink_mb=est_downlink_mb(
                            satellite.downlink_rate_mbps, pass_["duration_s"]
                        ),
                        created_at=utc_now(),
                    )
                )
                created += 1
    session.flush()
    return created


def _window_to_dict(window: ContactWindow) -> Dict[str, Any]:
    return {
        "id": window.id,
        "satellite_id": window.satellite_id,
        "ground_station_id": window.ground_station_id,
        "date": window.date,
        "aos_utc": window.aos_utc,
        "culminate_utc": window.culminate_utc,
        "los_utc": window.los_utc,
        "max_elevation_deg": float(window.max_elevation_deg),
        "duration_s": float(window.duration_s),
        "est_downlink_mb": float(window.est_downlink_mb),
    }


def list_windows(
    session: Session,
    satellite_id: Optional[str] = None,
    ground_station_id: Optional[str] = None,
    date: Optional[str] = None,
    after_utc: Optional[str] = None,
    limit: int = 100,
    cursor: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = select(ContactWindow).order_by(
        ContactWindow.aos_utc.asc(), ContactWindow.id.asc()
    )
    if satellite_id:
        query = query.where(ContactWindow.satellite_id == satellite_id)
    if ground_station_id:
        query = query.where(ContactWindow.ground_station_id == ground_station_id)
    if date:
        query = query.where(ContactWindow.date == date)
    if after_utc:
        query = query.where(ContactWindow.los_utc > after_utc)
    if cursor:
        aos_utc, window_id = decode_cursor(cursor, 2)
        query = query.where(
            tuple_(ContactWindow.aos_utc, ContactWindow.id) > (aos_utc, window_id)
        )
    windows = session.scalars(query.limit(limit)).all()
    return [_window_to_dict(window) for window in windows]


def next_window_for_satellite(
    session: Session,
    satellite_id: str,
    now_utc: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Earliest cached window that has not ended yet (may be in progress)."""
    now = now_utc or utc_now()
    window = session.scalars(
        select(ContactWindow)
        .where(
            ContactWindow.satellite_id == satellite_id,
            ContactWindow.los_utc > now,
        )
        .order_by(ContactWindow.aos_utc.asc())
        .limit(1)
    ).one_or_none()
    if window is None:
        return None
    return _window_to_dict(window)
