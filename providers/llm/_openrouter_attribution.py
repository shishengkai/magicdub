from __future__ import annotations

OPENROUTER_HTTP_REFERER = "https://magicdub.com"
OPENROUTER_APP_TITLE = "MagicDub"
OPENROUTER_APP_CATEGORIES = "video-gen"


def openrouter_app_attribution_headers() -> dict[str, str]:
    return {
        "HTTP-Referer": OPENROUTER_HTTP_REFERER,
        "X-OpenRouter-Title": OPENROUTER_APP_TITLE,
        "X-OpenRouter-Categories": OPENROUTER_APP_CATEGORIES,
    }
