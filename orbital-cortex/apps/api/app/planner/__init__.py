"""Source-backed mission feasibility and planning engine (Phase I).

Deterministic generate → hard-constrain → soft-rank → persist pipeline.
No LLM is used as a source of truth for feasibility.
"""

from app.planner.engine import generate_plans_for_mission
from app.planner.preferences import PLANNER_CONFIG_VERSION

__all__ = ["PLANNER_CONFIG_VERSION", "generate_plans_for_mission"]
