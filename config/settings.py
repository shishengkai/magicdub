from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / ".tmp"


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)


def require_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


def default_target_lang() -> str | None:
    raw = os.getenv("MAGICDUB_TARGET_LANG", "").strip()
    return raw or None


@lru_cache
def vocal_subtract_alpha() -> float:
    raw = os.getenv("MAGICDUB_VOCAL_SUBTRACT_ALPHA", "0.98").strip()
    return float(raw)


def instrumental_mix_volume() -> str | None:
    raw = os.getenv("MAGICDUB_RESIDUAL_MIX_VOLUME", "").strip()
    if not raw:
        return None
    try:
        if abs(float(raw) - 1.0) < 1e-12:
            return None
    except ValueError:
        pass
    return raw
