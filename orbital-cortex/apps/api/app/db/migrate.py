"""Alembic migration runner shared by the app entrypoint and CLI scripts."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig

API_DIR = Path(__file__).resolve().parents[2]


def run_migrations() -> None:
    alembic_config = AlembicConfig(str(API_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(API_DIR / "migrations"))
    command.upgrade(alembic_config, "head")
