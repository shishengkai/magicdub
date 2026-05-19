from __future__ import annotations

from providers._loader import load_provider
from providers.tts.base import TtsProvider


def get_tts_provider() -> TtsProvider:
    return load_provider("tts", "MAGICDUB_TTS_PROVIDER", "fal-index-tts-2")
