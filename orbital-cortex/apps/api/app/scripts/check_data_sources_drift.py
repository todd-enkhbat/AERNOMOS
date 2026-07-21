"""Phase Q doc-drift check.

Compares the provider list in ``orbital-cortex/docs/data-sources.md`` against the
Phase N registry config (``orbital-cortex/config/providers/*.yaml``). Exits
non-zero if a provider exists in one place but not the other, so the doc and the
registry can never silently drift apart.

Usage:
    cd orbital-cortex/apps/api && python -m app.scripts.check_data_sources_drift
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Set

# .../orbital-cortex/apps/api/app/scripts/check_data_sources_drift.py
#   parents[0]=scripts [1]=app [2]=api [3]=apps [4]=orbital-cortex
_ORBITAL_CORTEX = Path(__file__).resolve().parents[4]
PROVIDERS_DIR = _ORBITAL_CORTEX / "config" / "providers"
DATA_SOURCES_DOC = _ORBITAL_CORTEX / "docs" / "data-sources.md"

_PROVIDER_NAME_RE = re.compile(r"^provider_name:\s*(.+?)\s*$")


def provider_names_from_config() -> Set[str]:
    names: Set[str] = set()
    for path in sorted(PROVIDERS_DIR.glob("*.yaml")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = _PROVIDER_NAME_RE.match(line)
            if match:
                names.add(match.group(1).strip().strip('"').strip("'"))
                break
    return names


def doc_text() -> str:
    return DATA_SOURCES_DOC.read_text(encoding="utf-8")


def main() -> int:
    if not PROVIDERS_DIR.is_dir():
        print(f"ERROR: providers dir not found: {PROVIDERS_DIR}")
        return 2
    if not DATA_SOURCES_DOC.is_file():
        print(f"ERROR: data-sources.md not found: {DATA_SOURCES_DOC}")
        return 2

    config_names = provider_names_from_config()
    text = doc_text()

    missing_from_doc: List[str] = sorted(
        name for name in config_names if name not in text
    )

    # Flag doc rows that are not backed by a config file. We look at the
    # "Infrastructure provider registry" table rows (leading "| <name> |").
    documented: Set[str] = set()
    in_registry_section = False
    for line in text.splitlines():
        if line.strip().startswith("## Infrastructure provider registry"):
            in_registry_section = True
            continue
        if in_registry_section and line.startswith("## "):
            break
        if in_registry_section and line.startswith("|"):
            cell = line.split("|")[1].strip()
            if cell and cell not in ("Provider name", "---") and not set(cell) <= {"-"}:
                documented.add(cell)

    missing_from_config: List[str] = sorted(
        name for name in documented if name not in config_names
    )

    print("Data-sources doc-drift check")
    print("=" * 60)
    print(f"config providers ({len(config_names)}): {sorted(config_names)}")
    print(f"documented providers ({len(documented)}): {sorted(documented)}")

    ok = True
    if missing_from_doc:
        ok = False
        print("\nFAIL: in config but NOT in data-sources.md:")
        for name in missing_from_doc:
            print(f"  - {name}")
    if missing_from_config:
        ok = False
        print("\nFAIL: in data-sources.md registry table but NOT in config:")
        for name in missing_from_config:
            print(f"  - {name}")

    if ok:
        print("\nOK: data-sources.md and the provider registry are in sync.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
