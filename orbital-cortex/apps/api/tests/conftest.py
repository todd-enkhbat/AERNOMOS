"""Shared test environment: applied before any app module is imported."""

import os

# Local docker-compose Postgres (see orbital-cortex/docker-compose.yml).
os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
# Unreachable Redis: job creation falls back to the manual synchronous path.
# Force-set so CI job-level REDIS_URL (pointing at the Redis service) does not
# change the intended enqueue-failure path covered by the suite.
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
# The suite posts more jobs per minute than the production limit allows.
os.environ["RATE_LIMIT_ENABLED"] = "false"
