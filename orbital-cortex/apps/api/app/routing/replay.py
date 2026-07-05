"""Deterministic routing replay.

Every routing decision persists its full input bundle (job spec, node and
station registries, contact windows, decision time), the config version, and
a canonical hash of the decision content. Replay reruns the pure scorer over
the persisted inputs and compares hashes byte-for-byte.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from app.routing.scorer import compute_routing_decision

# No randomness exists in the scorer today; the seed is persisted so future
# stochastic components stay replayable.
DEFAULT_SEED = 0


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def build_inputs_bundle(
    job: Dict[str, Any],
    compute_nodes: Any,
    ground_stations: Any,
    next_windows: Dict[str, Dict[str, Any]],
    now_utc: str,
) -> Dict[str, Any]:
    return {
        "job": job,
        "compute_nodes": compute_nodes,
        "ground_stations": ground_stations,
        "next_windows": next_windows,
        "now_utc": now_utc,
        "seed": DEFAULT_SEED,
    }


def replay_from_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Recompute decision content from a persisted input bundle."""
    return compute_routing_decision(
        inputs["job"],
        inputs["compute_nodes"],
        inputs["ground_stations"],
        next_windows=inputs["next_windows"],
        now_utc=inputs["now_utc"],
    )
