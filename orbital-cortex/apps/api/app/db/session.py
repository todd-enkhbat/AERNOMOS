"""SQLAlchemy engine and session management for Postgres (Neon)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[4]

_engine: Optional[Engine] = None


def _normalize_url(url: str) -> str:
    # Force the psycopg3 driver; bare postgresql:// defaults to psycopg2.
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set. Copy apps/api/.env.example to .env."
            )
        _engine = create_engine(
            _normalize_url(settings.database_url),
            pool_pre_ping=True,
        )
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    session = SessionLocal(bind=get_engine())
    try:
        yield session
    finally:
        session.close()
