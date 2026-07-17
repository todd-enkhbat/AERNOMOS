"""Application settings loaded from the environment via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=API_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # "development" | "production". Gates demo resets and default CORS.
    app_env: str = "development"

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

    # Catalog discovery mode (Phase R). "live" hits Microsoft Planetary Computer;
    # "fixture" serves pinned real STAC FeatureCollections from
    # app/catalog/fixtures/ so accelerator demos work offline. Production
    # defaults to live; demos pass --demo / CATALOG_MODE=fixture.
    catalog_mode: str = "live"

    # Contact-window precompute horizon.
    pass_horizon_hours: int = 48

    # Comma-separated list of allowed browser origins. Never "*".
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # slowapi rate limit applied to POST /v1/jobs (per client IP).
    rate_limit_jobs: str = "10/minute"
    # Feedback + design-partner submissions (per client IP).
    rate_limit_leads: str = "5/hour"
    rate_limit_enabled: bool = True

    # Sentry error reporting; disabled when the DSN is empty.
    sentry_dsn: str = ""

    # --- Object storage (F1) ---------------------------------------------
    # When s3_bucket is set, artifacts go to S3/R2 via boto3; otherwise the
    # local filesystem backend under artifact_dir serves signed URLs itself.
    s3_bucket: str = ""
    # R2: https://<account_id>.r2.cloudflarestorage.com  (leave empty for AWS)
    s3_endpoint_url: str = ""
    s3_region: str = "auto"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    signed_url_expiry_s: int = 3600
    # Local-backend artifact directory (gitignored) and HMAC signing secret.
    artifact_dir: str = str(API_DIR / "var" / "artifacts")
    artifact_signing_secret: str = "dev-only-artifact-secret"
    # Public base URL of this API, used to build local signed URLs.
    public_base_url: str = "http://127.0.0.1:8000"

    # --- Real CPU execution (Phase M) --------------------------------------
    # Allowlisted directory for fixture inputs (fixture:<name> input_refs).
    execution_fixture_dir: str = str(API_DIR / "var" / "execution_fixtures")
    # Resource guards: reject larger inputs before processing; kill runs that
    # exceed the timeout instead of hanging.
    execution_max_input_bytes: int = 100 * 1024 * 1024
    execution_max_seconds: int = 120

    # --- Anonymous private sessions (Phase C) -----------------------------
    session_cookie_name: str = "nomos_session"
    # Empty locally (host-only cookie). Production: ".nomosorbital.com".
    session_cookie_domain: str = ""
    session_ttl_days: int = 30
    share_link_default_ttl_days: int = 7

    # --- Privacy-safe analytics (Phase O) ----------------------------------
    # Dedicated salt for HMAC-SHA256 session/share hashes in analytics payloads.
    # Separate from artifact signing and auth secrets.
    analytics_hash_salt: str = "dev-only-analytics-hash-salt"
    # Shared token for GET /v1/admin/analytics/summary (constant-time compare).
    admin_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def cors_origin_list(settings: Settings) -> List[str]:
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
