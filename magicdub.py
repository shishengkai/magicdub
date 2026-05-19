"""MagicDub CLI entry module (installed as top-level py-module)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_root = str(_REPO_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)


def run() -> None:
    from cli.main import app

    app()


if __name__ == "__main__":
    run()
