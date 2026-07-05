"""Job lifecycle state machine.

The jobs.status column is the single source of truth. All status writes go
through validate_transition(); illegal transitions raise and are rejected.

    queued -> routing -> executing -> downlinking -> complete
    (any non-terminal state) -> failed
"""

from __future__ import annotations

from typing import Dict, FrozenSet

JOB_STATES = (
    "queued",
    "routing",
    "executing",
    "downlinking",
    "complete",
    "failed",
)

TERMINAL_STATES: FrozenSet[str] = frozenset({"complete", "failed"})

_ALLOWED: Dict[str, FrozenSet[str]] = {
    "queued": frozenset({"routing", "failed"}),
    "routing": frozenset({"executing", "failed"}),
    "executing": frozenset({"downlinking", "failed"}),
    "downlinking": frozenset({"complete", "failed"}),
    "complete": frozenset(),
    "failed": frozenset(),
}


class IllegalTransitionError(Exception):
    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Illegal job state transition: {current!r} -> {target!r}. "
            f"Allowed from {current!r}: {sorted(_ALLOWED.get(current, frozenset())) or 'none'}."
        )


def validate_transition(current: str, target: str) -> None:
    if current not in _ALLOWED:
        raise IllegalTransitionError(current, target)
    if target not in _ALLOWED[current]:
        raise IllegalTransitionError(current, target)
