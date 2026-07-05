"""Application settings loaded from the environment via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=API_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Postgres (Neon) connection string, e.g.
    # postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
    # Required: the app raises at engine creation when unset.
    database_url: str = ""

    # Redis connection for the ARQ job queue.
    redis_url: str = "redis://localhost:6379/0"

    # Optional pause between pipeline stages in the worker, so demo UIs can
    # show the job progressing through states. Keep 0 for tests.
    worker_stage_delay_s: float = 0.0

    # When true, refresh TLEs from CelesTrak at seed time instead of using
    # the pinned simulator/tle_snapshot.json (deterministic default).
    live_tle: bool = False

    # Contact-window precompute horizon.
    pass_horizon_hours: int = 48


@lru_cache
def get_settings() -> Settings:
    return Settings()
