from __future__ import annotations

import os
from typing import Any

import requests

from providers.llm.base import LlmRequest, LlmResult

PROVIDER_REF = "llm/deepseek"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_DEEPSEEK_TIMEOUT_SECONDS = 180
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_RESPONSE_FORMAT = "json_object"
DEFAULT_THINKING_TYPE = "enabled"


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _resolve_api_key() -> str:
    key = _env_first("DEEPSEEK_API_KEY", "LLM_API_KEY")
    if key:
        return key
    raise RuntimeError("Missing required env var: DEEPSEEK_API_KEY or LLM_API_KEY")


def _resolve_base_url() -> str:
    return (
        _env_first("DEEPSEEK_BASE_URL", "LLM_BASE_URL") or DEFAULT_DEEPSEEK_BASE_URL
    ).rstrip("/")


def _resolve_model() -> str:
    return _env_first("DEEPSEEK_MODEL", "LLM_MODEL") or DEFAULT_DEEPSEEK_MODEL


def _resolve_timeout_seconds() -> int:
    raw = (
        _env_first("DEEPSEEK_TIMEOUT_SECONDS", "LLM_TIMEOUT_SECONDS")
        or str(DEFAULT_DEEPSEEK_TIMEOUT_SECONDS)
    )
    return max(30, int(raw))


def _optional_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return int(raw)


def _response_format() -> dict[str, str] | None:
    raw = os.getenv("DEEPSEEK_RESPONSE_FORMAT")
    value = DEFAULT_RESPONSE_FORMAT if raw is None else raw.strip()
    if not value or value.lower() in ("none", "off", "false", "0"):
        return None
    if value == "json_object":
        return {"type": "json_object"}
    if value == "text":
        return {"type": "text"}
    raise RuntimeError(
        "DEEPSEEK_RESPONSE_FORMAT must be json_object, text, none, or off."
    )


def _thinking_config() -> dict[str, str] | None:
    raw = os.getenv("DEEPSEEK_THINKING")
    value = DEFAULT_THINKING_TYPE if raw is None else raw.strip().lower()
    if not value or value in ("none", "off", "false", "0", "disabled"):
        return {"type": "disabled"}
    if value in ("enabled", "on", "true", "1"):
        return {"type": "enabled"}
    raise RuntimeError("DEEPSEEK_THINKING must be enabled, disabled, on, or off.")


def _reasoning_effort() -> str | None:
    raw = os.getenv("DEEPSEEK_REASONING_EFFORT")
    value = DEFAULT_REASONING_EFFORT if raw is None else raw.strip().lower()
    if not value or value in ("none", "off", "false", "0"):
        return None
    if value not in ("high", "max"):
        raise RuntimeError("DEEPSEEK_REASONING_EFFORT must be high, max, none, or off.")
    return value


def _request_payload(request: LlmRequest) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": _resolve_model(),
        "messages": [
            {"role": message.role, "content": message.content}
            for message in request.messages
        ],
        "stream": False,
    }

    thinking = _thinking_config()
    if thinking is not None:
        payload["thinking"] = thinking

    reasoning_effort = _reasoning_effort()
    if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort

    response_format = _response_format()
    if response_format is not None:
        payload["response_format"] = response_format

    max_tokens = _optional_int("DEEPSEEK_MAX_TOKENS")
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
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
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


class DeepSeekProvider:
    def complete(self, request: LlmRequest) -> LlmResult:
        base_url = _resolve_base_url()
        payload = _request_payload(request)
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {_resolve_api_key()}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=_resolve_timeout_seconds(),
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"DeepSeek API request failed with HTTP {response.status_code}: "
                f"{_error_message(response)}"
            )

        raw_response = response.json()
        choices = raw_response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"DeepSeek API returned no choices: {raw_response}")

        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError(f"DeepSeek API returned an invalid choice: {choice!r}")

        message = choice.get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"DeepSeek API returned an invalid message: {message!r}")

        return LlmResult(
            content=_assistant_text(message.get("content")),
            finish_reason=choice.get("finish_reason"),
            raw_response=raw_response,
            metadata={
                "base_url": base_url,
                "model": payload["model"],
                "reasoning_effort": payload.get("reasoning_effort"),
                "thinking": payload.get("thinking"),
                "reasoning_content": message.get("reasoning_content"),
                "usage": raw_response.get("usage"),
            },
        )


Provider = DeepSeekProvider
