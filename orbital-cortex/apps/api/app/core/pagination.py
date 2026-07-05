"""Opaque keyset cursors for list endpoints.

A cursor encodes the sort-key values of the last item on the previous page
(url-safe base64 of "part1|part2"), so pages stay stable while new rows
arrive between requests.
"""

from __future__ import annotations

import base64
import binascii
from typing import List


class InvalidCursorError(ValueError):
    pass


def encode_cursor(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor: str, expected_parts: int) -> List[str]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
        raise InvalidCursorError("cursor is not valid base64") from exc
    parts = raw.split("|")
    if len(parts) != expected_parts:
        raise InvalidCursorError("cursor has the wrong shape")
    return parts
