"""TLE snapshot management.

Deterministic by default: satellites seed from the pinned
simulator/tle_snapshot.json. A live CelesTrak refresh is available behind the
LIVE_TLE flag (or `python -m app.services.tle_cache --live` to regenerate the
pinned snapshot).
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[4]
SNAPSHOT_PATH = REPO_ROOT / "simulator" / "tle_snapshot.json"

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"

# The tracked fleet: real LEO EO satellites with public NORAD IDs.
# Downlink rates are public X-band figures (ICEYE ~140 Mbit/s,
# Sentinel-1 2x260 Mbit/s, Capella ~1.2 Gbit/s).
FLEET: List[Dict[str, Any]] = [
    {"id": "sat_sentinel_1a", "name": "SENTINEL-1A", "norad_id": 39634, "downlink_rate_mbps": 520},
    {"id": "sat_sentinel_1c", "name": "SENTINEL-1C", "norad_id": 62261, "downlink_rate_mbps": 520},
    {"id": "sat_iceye_x2", "name": "ICEYE-X2", "norad_id": 43800, "downlink_rate_mbps": 140},
    {"id": "sat_capella_14", "name": "CAPELLA-14 (ACADIA-4)", "norad_id": 59444, "downlink_rate_mbps": 1200},
    {"id": "sat_capella_15", "name": "CAPELLA-15 (ACADIA-5)", "norad_id": 60544, "downlink_rate_mbps": 1200},
]


def tle_epoch_utc(tle_line1: str) -> str:
    """Parse the epoch from TLE line 1 (columns 19-32, YYDDD.DDDDDDDD)."""
    field = tle_line1[18:32]
    year_two = int(field[:2])
    year = 2000 + year_two if year_two < 57 else 1900 + year_two
    day_of_year = float(field[2:])
    epoch = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    return epoch.replace(microsecond=0).isoformat()


def load_snapshot() -> Dict[str, Any]:
    with SNAPSHOT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fetch_live_snapshot() -> Dict[str, Any]:
    """Fetch fresh TLEs from CelesTrak for the tracked fleet."""
    satellites: List[Dict[str, Any]] = []
    for entry in FLEET:
        url = CELESTRAK_URL.format(norad_id=entry["norad_id"])
        with urllib.request.urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8")
        lines = [line.rstrip() for line in text.strip().splitlines()]
        if len(lines) < 3 or not lines[1].startswith("1 "):
            raise ValueError(f"Unexpected TLE response for NORAD {entry['norad_id']}: {text[:100]}")
        satellites.append(
            {
                **entry,
                "tle_line1": lines[1],
                "tle_line2": lines[2],
                "tle_epoch": tle_epoch_utc(lines[1]),
            }
        )
    fetched = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "snapshot_id": f"celestrak-{fetched.date().isoformat()}",
        "fetched_utc": fetched.isoformat(),
        "source": "https://celestrak.org/NORAD/elements/gp.php",
        "satellites": satellites,
    }


def get_snapshot(live: bool = False) -> Dict[str, Any]:
    if live:
        return fetch_live_snapshot()
    return load_snapshot()


def write_snapshot(snapshot: Dict[str, Any]) -> None:
    with SNAPSHOT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    import sys

    if "--live" in sys.argv:
        snapshot = fetch_live_snapshot()
        write_snapshot(snapshot)
        print(f"Wrote {SNAPSHOT_PATH} ({snapshot['snapshot_id']}, {len(snapshot['satellites'])} satellites)")
    else:
        snapshot = load_snapshot()
        print(f"Pinned snapshot {snapshot['snapshot_id']} with {len(snapshot['satellites'])} satellites")
