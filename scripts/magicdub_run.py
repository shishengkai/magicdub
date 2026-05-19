"""Python entry invoked by scripts/magicdub (shell wrapper)."""

import sys
from pathlib import Path

# Fallback if PYTHONPATH was not set by the wrapper
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from cli.main import app

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "provider":
        from cli.provider import app as provider_app

        sys.argv.pop(1)
        provider_app(prog_name="magicdub provider")
    else:
        app(prog_name="magicdub")
