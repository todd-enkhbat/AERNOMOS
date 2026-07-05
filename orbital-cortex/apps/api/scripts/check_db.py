"""A1 definition-of-done check: PostGIS is reachable on the configured database.

Usage (from apps/api):
    python -m scripts.check_db

Enables the PostGIS extension if missing, then prints postgis_version().
"""

from __future__ import annotations

import sys

import psycopg

from app.core.config import get_settings


def main() -> int:
    settings = get_settings()
    if not settings.database_url:
        print("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
        return 1

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            conn.commit()
            cur.execute("SELECT postgis_version();")
            row = cur.fetchone()
            cur.execute("SELECT current_database(), version();")
            db, pg_version = cur.fetchone()

    print(f"database:        {db}")
    print(f"postgres:        {pg_version.split(',')[0]}")
    print(f"postgis_version: {row[0]}")
    print("A1 DoD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
