"""Policy checks for the local non-defense demo."""

from __future__ import annotations

from typing import Any, Dict, List

REQUIRED_TAG = "non_defense"
BLOCKED_TAGS = {"classified", "defense_only", "weapons", "targeting"}


def node_is_allowed(node: Dict[str, Any]) -> bool:
    tags = set(node.get("compliance_tags", []))
    return REQUIRED_TAG in tags and tags.isdisjoint(BLOCKED_TAGS)


def compliance_reasons(node: Dict[str, Any]) -> List[str]:
    tags = set(node.get("compliance_tags", []))
    reasons: List[str] = []
    if REQUIRED_TAG in tags:
        reasons.append("Allowed for non-defense demo use")
    else:
        reasons.append("Missing non_defense compliance tag")
    blocked = sorted(tags.intersection(BLOCKED_TAGS))
    if blocked:
        reasons.append(f"Blocked compliance tags present: {', '.join(blocked)}")
    return reasons
