from __future__ import annotations

import os
from typing import Any

import requests

from providers.llm._openrouter_attribution import openrouter_app_attribution_headers
from providers.llm.base import LlmRequest, LlmResult

PROVIDER_REF = "llm/openrouter"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "~google/gemini-flash-latest"
DEFAULT_OPENROUTER_TIMEOUT_SECONDS = 180
DEFAULT_RESPONSE_FORMAT = "json_object"


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _resolve_api_key() -> str:
    key = _env_first("OPENROUTER_API_KEY", "LLM_API_KEY")
    if key:
        return key
    raise RuntimeError("Missing required env var: OPENROUTER_API_KEY or LLM_API_KEY")


def _resolve_base_url() -> str:
    return (
        _env_first("OPENROUTER_BASE_URL", "LLM_BASE_URL")
        or DEFAULT_OPENROUTER_BASE_URL
    ).rstrip("/")


def _resolve_model() -> str:
    return _env_first("OPENROUTER_MODEL", "LLM_MODEL") or DEFAULT_OPENROUTER_MODEL


def _resolve_timeout_seconds() -> int:
    raw = (
        _env_first("OPENROUTER_TIMEOUT_SECONDS", "LLM_TIMEOUT_SECONDS")
        or str(DEFAULT_OPENROUTER_TIMEOUT_SECONDS)
    )
    return max(30, int(raw))


def _optional_float(name: str) -> float | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return float(raw)


def _optional_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return int(raw)


def _response_format() -> dict[str, str] | None:
    raw = os.getenv("OPENROUTER_RESPONSE_FORMAT")
    value = DEFAULT_RESPONSE_FORMAT if raw is None else raw.strip()
    if not value or value.lower() in ("none", "off", "false", "0"):
        return None
    if value == "json_object":
        return {"type": "json_object"}
    if value == "text":
        return None
    raise RuntimeError(
        "OPENROUTER_RESPONSE_FORMAT must be json_object, text, none, or off."
    )


def _headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {_resolve_api_key()}",
        "Content-Type": "application/json",
    }
    headers.update(openrouter_app_attribution_headers())
    return headers


def _request_payload(request: LlmRequest) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": _resolve_model(),
        "messages": [
            {"role": message.role, "content": message.content}
            for message in request.messages
        ],
        "stream": False,
    }

    response_format = _response_format()
    if response_format is not None:
        payload["response_format"] = response_format

    temperature = _optional_float("OPENROUTER_TEMPERATURE")
    if temperature is not None:
        payload["temperature"] = temperature

    top_p = _optional_float("OPENROUTER_TOP_P")
    if top_p is not None:
        payload["top_p"] = top_p

    top_k = _optional_int("OPENROUTER_TOP_K")
    if top_k is not None:
        payload["top_k"] = top_k

    max_tokens = _optional_int("OPENROUTER_MAX_TOKENS")
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    return payload


def _assistant_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if isinstance(block.get("text"), str):
                    parts.append(block["text"])
                elif block.get("type") == "text" and isinstance(
                    block.get("content"), str
                ):
                    parts.append(block["content"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _error_message(response: requests.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text.strip()
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])
    return str(data)


class OpenRouterProvider:
    def complete(self, request: LlmRequest) -> LlmResult:
        base_url = _resolve_base_url()
        payload = _request_payload(request)
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=_headers(),
            json=payload,
            timeout=_resolve_timeout_seconds(),
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenRouter API request failed with HTTP {response.status_code}: "
                f"{_error_message(response)}"
            )

        raw_response = response.json()
        choices = raw_response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"OpenRouter API returned no choices: {raw_response}")

        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError(f"OpenRouter API returned an invalid choice: {choice!r}")

        message = choice.get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"OpenRouter API returned an invalid message: {message!r}")

        return LlmResult(
            content=_assistant_text(message.get("content")),
            finish_reason=choice.get("finish_reason"),
            raw_response=raw_response,
            metadata={
                "base_url": base_url,
                "model": payload["model"],
                "resolved_model": raw_response.get("model"),
                "native_finish_reason": choice.get("native_finish_reason"),
                "usage": raw_response.get("usage"),
            },
        )


Provider = OpenRouterProvider
