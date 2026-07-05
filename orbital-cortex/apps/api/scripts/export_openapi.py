"""Export the OpenAPI spec to stdout or a file.

Imports the FastAPI app without running lifespan, so no database or Redis
is needed — safe for CI:

    python -m scripts.export_openapi openapi.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "-"
    payload = json.dumps(app.openapi(), indent=2, sort_keys=True)
    if target == "-":
        print(payload)
    else:
        Path(target).write_text(payload + "\n", encoding="utf-8")
        print(f"wrote {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
