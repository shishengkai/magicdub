from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from config.settings import fal_trace_headers, require_env
from providers.llm._openrouter_attribution import openrouter_app_attribution_headers
from providers.llm.base import LlmRequest, LlmResult

DEFAULT_LLM_BASE_URL = "https://fal.run/openrouter/router/openai/v1"
DEFAULT_LLM_MODEL = "google/gemini-3-flash-preview"
DEFAULT_LLM_TIMEOUT_SECONDS = 1800


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _resolve_api_key() -> str:
    key = _env_first("LLM_API_KEY", "OPENAI_API_KEY")
    if key:
        return key
    return require_env("FAL_KEY")


def _resolve_base_url() -> str:
    return (
        _env_first("LLM_BASE_URL", "FAL_OPENROUTER_BASE_URL", "OPENAI_BASE_URL")
        or DEFAULT_LLM_BASE_URL
    ).rstrip("/")


def _resolve_model() -> str:
    return (
        _env_first("LLM_MODEL", "OPENROUTER_CHAT_MODEL", "OPENROUTER_MODEL")
        or DEFAULT_LLM_MODEL
    )


def _resolve_timeout_seconds() -> int:
    raw = (
        _env_first("LLM_TIMEOUT_SECONDS", "OPENROUTER_CHAT_TIMEOUT_SECONDS")
        or str(DEFAULT_LLM_TIMEOUT_SECONDS)
    )
    return max(60, int(raw))


def _resolve_auth_scheme(base_url: str) -> str:
    explicit = os.getenv("LLM_AUTH_SCHEME", "").strip().lower()
    if explicit in ("bearer", "fal_key"):
        return explicit
    if "fal.run" in base_url:
        return "fal_key"
    return "bearer"


def _openrouter_client_headers(base_url: str) -> dict[str, str]:
    if "openrouter.ai" not in base_url:
        return {}
    return openrouter_app_attribution_headers()


def _fal_llm_trace_headers(base_url: str) -> dict[str, str]:
    if "fal.run" not in base_url:
        return {}
    return fal_trace_headers()


def _extra_body(base_url: str) -> dict[str, Any] | None:
    raw = os.getenv("LLM_EXTRA_BODY_JSON", "").strip()
    if raw:
        return json.loads(raw)

    flag = os.getenv("LLM_REASONING_ENABLED", "").strip().lower()
    if flag in ("0", "false", "no"):
        return None
    if flag in ("1", "true", "yes"):
        return {"reasoning": {"enabled": True}}
    if "openrouter" in base_url.lower():
        return {"reasoning": {"enabled": True}}
    return None


def _assistant_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if hasattr(block, "text"):
                parts.append(str(getattr(block, "text", None) or ""))
            elif isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text") or ""))
                elif "text" in block:
                    parts.append(str(block.get("text") or ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


class FalOpenRouterProvider:
    def complete(self, request: LlmRequest) -> LlmResult:
        api_key = _resolve_api_key()
        base_url = _resolve_base_url()
        auth_scheme = _resolve_auth_scheme(base_url)

        default_headers: dict[str, str] = {}
        default_headers.update(_openrouter_client_headers(base_url))
        default_headers.update(_fal_llm_trace_headers(base_url))

        client_api_key = api_key
        if auth_scheme == "fal_key":
            default_headers["Authorization"] = f"Key {api_key}"
            client_api_key = "not-needed"

        client = OpenAI(
            api_key=client_api_key,
            base_url=base_url,
            timeout=float(_resolve_timeout_seconds()),
            default_headers=default_headers or None,
        )

        request_kwargs: dict[str, Any] = {
            "model": _resolve_model(),
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ],
            "stream": False,
        }
        extra_body = _extra_body(base_url)
        if extra_body is not None:
            request_kwargs["extra_body"] = extra_body

        completion = client.chat.completions.create(**request_kwargs)
        choice = completion.choices[0]
        return LlmResult(
            content=_assistant_text(choice.message.content),
            finish_reason=choice.finish_reason,
            raw_response=completion,
            metadata={"base_url": base_url, "model": request_kwargs["model"]},
        )


Provider = FalOpenRouterProvider
