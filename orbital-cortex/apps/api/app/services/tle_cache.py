"""TLE snapshot management with provenance and staleness labels.

Deterministic by default: satellites seed from the pinned
simulator/tle_snapshot.json. A live CelesTrak refresh is available behind the
LIVE_TLE flag, the refresh worker cron, or
`python -m app.services.tle_cache --live` to regenerate the pinned snapshot.

Staleness rule
--------------
If the newest TLE epoch in a snapshot is older than ``STALE_EPOCH_DAYS`` (7),
the snapshot truth status is ``STALE``. Pinned-file fallback after a failed
live fetch is also ``STALE`` (the pinned file is dated real CelesTrak data,
not authored fiction). Use ``SIMULATED`` only for demo-authored fiction — not
for this pinned orbital snapshot.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.db.truth import TruthStatus

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]
SNAPSHOT_PATH = REPO_ROOT / "simulator" / "tle_snapshot.json"

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"
CELESTRAK_SOURCE_URL = "https://celestrak.org/NORAD/elements/gp.php"

# Provider id strings persisted on Satellite.source / snapshot metadata.
SOURCE_CELESTRAK_GP = "celestrak-gp"
SOURCE_PINNED_SNAPSHOT = "pinned-snapshot"

# Epoch age above this threshold → TruthStatus.STALE.
STALE_EPOCH_DAYS = 7
STALE_EPOCH_AGE = timedelta(days=STALE_EPOCH_DAYS)

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


def parse_iso_utc(value: str) -> datetime:
    """Parse an ISO-8601 timestamp into an aware UTC datetime."""
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
    # Unique id per successful live refresh so prior window rows stay auditable.
    snapshot_id = f"celestrak-{fetched.strftime('%Y-%m-%dT%H%M%SZ')}"
    return {
        "snapshot_id": snapshot_id,
        "fetched_utc": fetched.isoformat(),
        "source": CELESTRAK_SOURCE_URL,
        "source_id": SOURCE_CELESTRAK_GP,
        "satellites": satellites,
    }


def _epoch_datetimes(snapshot: Dict[str, Any]) -> List[datetime]:
    epochs: List[datetime] = []
    for sat in snapshot.get("satellites") or []:
        raw = sat.get("tle_epoch")
        if not raw:
            continue
        epochs.append(parse_iso_utc(str(raw)))
    return epochs


def classify_orbital_truth_status(
    *,
    source_id: str,
    epochs: List[datetime],
    now: Optional[datetime] = None,
    used_pinned_fallback: bool = False,
) -> TruthStatus:
    """Label orbital elements for planner/API surfaces.

    - Pinned file or live-fetch fallback → STALE (dated real TLEs).
    - Live CelesTrak with any epoch older than STALE_EPOCH_DAYS → STALE.
    - Fresh live CelesTrak → PROVIDER_REPORTED.
    """
    clock = now or datetime.now(timezone.utc)
    if used_pinned_fallback or source_id == SOURCE_PINNED_SNAPSHOT:
        return TruthStatus.STALE
    if not epochs:
        return TruthStatus.UNAVAILABLE
    oldest = min(epochs)
    if clock - oldest > STALE_EPOCH_AGE:
        return TruthStatus.STALE
    return TruthStatus.PROVIDER_REPORTED


def annotate_snapshot(
    snapshot: Dict[str, Any],
    *,
    source_id: str,
    used_pinned_fallback: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a shallow-copied snapshot with provenance fields filled in."""
    clock = now or datetime.now(timezone.utc)
    annotated = dict(snapshot)
    epochs = _epoch_datetimes(annotated)
    truth = classify_orbital_truth_status(
        source_id=source_id,
        epochs=epochs,
        now=clock,
        used_pinned_fallback=used_pinned_fallback,
    )
    annotated["source_id"] = source_id
    annotated["used_pinned_fallback"] = used_pinned_fallback
    annotated["truth_status"] = truth.value
    annotated["retrieved_at"] = annotated.get("fetched_utc") or clock.replace(
        microsecond=0
    ).isoformat()
    annotated["stale_epoch_days"] = STALE_EPOCH_DAYS
    return annotated


def get_orbital_snapshot_metadata(
    snapshot: Optional[Dict[str, Any]] = None,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Internal helper: snapshot provenance for mission plans / APIs.

    Returns ``{snapshot_id, source, epochs, truth_status, retrieved_at}`` plus
    ``source_url`` and ``stale_epoch_days`` for audit trails.
    """
    raw = snapshot if snapshot is not None else load_snapshot()
    if "source_id" in raw and "truth_status" in raw:
        snap = raw
    else:
        source_id = str(raw.get("source_id") or SOURCE_PINNED_SNAPSHOT)
        if source_id not in (SOURCE_CELESTRAK_GP, SOURCE_PINNED_SNAPSHOT):
            source_url = str(raw.get("source") or "")
            source_id = (
                SOURCE_CELESTRAK_GP
                if "celestrak" in source_url.lower()
                else SOURCE_PINNED_SNAPSHOT
            )
        snap = annotate_snapshot(
            raw,
            source_id=source_id,
            used_pinned_fallback=bool(raw.get("used_pinned_fallback", False)),
            now=now,
        )
    epochs = [
        sat.get("tle_epoch") for sat in snap.get("satellites") or [] if sat.get("tle_epoch")
    ]
    return {
        "snapshot_id": snap["snapshot_id"],
        "source": snap.get("source_id") or SOURCE_PINNED_SNAPSHOT,
        "source_url": snap.get("source") or CELESTRAK_SOURCE_URL,
        "epochs": epochs,
        "truth_status": snap["truth_status"],
        "retrieved_at": snap.get("retrieved_at") or snap.get("fetched_utc"),
        "stale_epoch_days": STALE_EPOCH_DAYS,
        "used_pinned_fallback": bool(snap.get("used_pinned_fallback", False)),
    }


def resolve_orbital_snapshot(
    *,
    prefer_live: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Choose live CelesTrak or pinned fallback with truth labels applied.

    On live failure, returns the pinned simulator snapshot marked STALE.
    """
    if prefer_live:
        try:
            live = fetch_live_snapshot()
            return annotate_snapshot(
                live,
                source_id=SOURCE_CELESTRAK_GP,
                used_pinned_fallback=False,
                now=now,
            )
        except Exception as exc:  # noqa: BLE001 — network/parse failures are expected
            logger.warning("live TLE fetch failed; using pinned snapshot: %s", exc)
            pinned = load_snapshot()
            return annotate_snapshot(
                pinned,
                source_id=SOURCE_PINNED_SNAPSHOT,
                used_pinned_fallback=True,
                now=now,
            )
    pinned = load_snapshot()
    return annotate_snapshot(
        pinned,
        source_id=SOURCE_PINNED_SNAPSHOT,
        used_pinned_fallback=False,
        now=now,
    )


def get_snapshot(live: bool = False) -> Dict[str, Any]:
    """Backward-compatible entry: annotated live or pinned snapshot."""
    return resolve_orbital_snapshot(prefer_live=live)


def write_snapshot(snapshot: Dict[str, Any]) -> None:
    # Persist only the durable fields; runtime truth annotations are recomputed.
    durable = {
        "snapshot_id": snapshot["snapshot_id"],
        "fetched_utc": snapshot.get("fetched_utc") or snapshot.get("retrieved_at"),
        "source": snapshot.get("source") or CELESTRAK_SOURCE_URL,
        "satellites": snapshot["satellites"],
    }
    with SNAPSHOT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(durable, handle, indent=2)
        handle.write("\n")


def metadata_from_db_satellites(
    satellites: List[Any],
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Build snapshot metadata from persisted Satellite ORM rows."""
    if not satellites:
        return {
            "snapshot_id": "",
            "source": SOURCE_PINNED_SNAPSHOT,
            "source_url": CELESTRAK_SOURCE_URL,
            "epochs": [],
            "truth_status": TruthStatus.UNAVAILABLE.value,
            "retrieved_at": None,
            "stale_epoch_days": STALE_EPOCH_DAYS,
            "used_pinned_fallback": False,
        }
    first = satellites[0]
    source_raw = getattr(first, "source", "") or ""
    if source_raw in (SOURCE_CELESTRAK_GP, SOURCE_PINNED_SNAPSHOT):
        source_id = source_raw
        source_url = CELESTRAK_SOURCE_URL
    elif "celestrak" in source_raw.lower():
        # Legacy rows stored the CelesTrak URL in ``source``.
        source_id = SOURCE_CELESTRAK_GP
        source_url = source_raw
    else:
        source_id = SOURCE_PINNED_SNAPSHOT
        source_url = source_raw or CELESTRAK_SOURCE_URL

    # Pinned seed writes source_id=pinned-snapshot; live refresh writes celestrak-gp.
    used_fallback = source_id == SOURCE_PINNED_SNAPSHOT
    epochs = [
        parse_iso_utc(str(sat.tle_epoch))
        for sat in satellites
        if getattr(sat, "tle_epoch", None)
    ]
    truth = classify_orbital_truth_status(
        source_id=source_id,
        epochs=epochs,
        now=now,
        used_pinned_fallback=used_fallback,
    )
    retrieved = getattr(first, "retrieved_at", None)
    return {
        "snapshot_id": getattr(first, "snapshot_id", "") or "",
        "source": source_id,
        "source_url": source_url,
        "epochs": [sat.tle_epoch for sat in satellites if sat.tle_epoch],
        "truth_status": truth.value,
        "retrieved_at": retrieved,
        "stale_epoch_days": STALE_EPOCH_DAYS,
        "used_pinned_fallback": used_fallback,
    }


if __name__ == "__main__":
    import sys

    if "--live" in sys.argv:
        snapshot = fetch_live_snapshot()
        write_snapshot(snapshot)
        print(
            f"Wrote {SNAPSHOT_PATH} ({snapshot['snapshot_id']}, "
            f"{len(snapshot['satellites'])} satellites)"
        )
    else:
        snapshot = resolve_orbital_snapshot(prefer_live=False)
        meta = get_orbital_snapshot_metadata(snapshot)
        print(
            f"Pinned snapshot {meta['snapshot_id']} with "
            f"{len(snapshot['satellites'])} satellites "
            f"(truth_status={meta['truth_status']})"
        )
