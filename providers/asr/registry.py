from __future__ import annotations

from providers._loader import load_provider
from providers.asr.base import AsrProvider


def get_asr_provider() -> AsrProvider:
    return load_provider("asr", "MAGICDUB_ASR_PROVIDER", "fal-wizper")
