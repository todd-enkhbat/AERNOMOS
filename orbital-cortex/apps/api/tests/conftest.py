"""Shared test environment: applied before any app module is imported."""

import os

# Unreachable Redis: job creation falls back to the manual synchronous path.
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
# The suite posts more jobs per minute than the production limit allows.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
