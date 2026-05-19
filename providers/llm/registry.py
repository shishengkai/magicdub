from __future__ import annotations

from providers._loader import load_provider
from providers.llm.base import LlmProvider


def get_llm_provider() -> LlmProvider:
    return load_provider("llm", "MAGICDUB_LLM_PROVIDER", "google-gemini")
