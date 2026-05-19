from __future__ import annotations

from datetime import datetime


def local_iso_timestamp() -> str:
    """Local wall-clock time in ISO 8601 (includes UTC offset), e.g. 2026-05-19T14:30:00+08:00."""
    return datetime.now().astimezone().isoformat(timespec="seconds")
