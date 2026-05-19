from __future__ import annotations

from providers._loader import load_provider
from providers.vocal_separation.base import VocalSeparationProvider


def get_vocal_separation_provider() -> VocalSeparationProvider:
    return load_provider(
        "vocal_separation",
        "MAGICDUB_VOCAL_SEPARATION_PROVIDER",
        "fal-demucs",
    )
