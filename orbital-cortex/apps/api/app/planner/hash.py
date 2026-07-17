"""Deterministic hashing for planner inputs and plan content.

Mirrors app/routing/replay.py so the same mission inputs + source snapshot
produce identical plan hashes and ranking order.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def plan_content_hash(
    *,
    pattern: str,
    steps: Any,
    feasibility_status: str,
    rejection_codes: Any,
    estimates: Dict[str, Any],
    config_version: str,
) -> str:
    return canonical_hash(
        {
            "pattern": pattern,
            "steps": steps,
            "feasibility_status": feasibility_status,
            "rejection_codes": rejection_codes,
            "estimates": estimates,
            "config_version": config_version,
        }
    )
