from __future__ import annotations

from pathlib import Path

_MAGICDUB_MARKER = "_MagicDub"


def resolve_magicdub_export_path(input_video: Path) -> Path:
    """Next to input: {stem}_MagicDub{ext}, or {stem}_MagicDub_2{ext}, _3, ... if taken."""
    input_video = input_video.expanduser().resolve()
    ext = input_video.suffix or ".mp4"
    parent = input_video.parent
    base = f"{input_video.stem}{_MAGICDUB_MARKER}"

    candidate = parent / f"{base}{ext}"
    if not candidate.exists():
        return candidate

    n = 2
    while True:
        candidate = parent / f"{base}_{n}{ext}"
        if not candidate.exists():
            return candidate
        n += 1
