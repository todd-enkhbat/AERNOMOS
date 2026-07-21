"""Upsert versioned provider YAML into InfrastructureResource rows."""

from __future__ import annotations

import argparse
import sys

from app.db.session import SessionLocal, get_engine
from app.services.provider_registry import ingest_providers_from_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest checked-in provider YAML into infrastructure_resources."
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default=None,
        help="Override provider config directory (default: orbital-cortex/config/providers)",
    )
    args = parser.parse_args(argv)

    config_dir = None
    if args.config_dir:
        from pathlib import Path

        config_dir = Path(args.config_dir)

    session = SessionLocal(bind=get_engine())
    try:
        result = ingest_providers_from_config(session, config_dir=config_dir)
        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"ingest_providers: FAILED — {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()

    print(
        f"ingest_providers: upserted {result['ingested']} provider file(s) "
        f"from {result['files']} config path(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
