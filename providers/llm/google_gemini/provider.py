from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests

from providers.llm.base import LlmMessage, LlmRequest, LlmResult

PROVIDER_REF = "llm/google-gemini"
DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
DEFAULT_GEMINI_TIMEOUT_SECONDS = 180
DEFAULT_RESPONSE_MIME_TYPE = "application/json"


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _resolve_api_key() -> str:
    key = _env_first(
        "GEMINI_API_KEY",
        "GOOGLE_AI_STUDIO_API_KEY",
        "GOOGLE_API_KEY",
        "LLM_API_KEY",
    )
    if key:
        return key
    raise RuntimeError(
        "Missing required env var: GEMINI_API_KEY "
        "(or GOOGLE_AI_STUDIO_API_KEY, GOOGLE_API_KEY, LLM_API_KEY)"
    )


def _resolve_model() -> str:
    return _env_first("GEMINI_MODEL", "LLM_MODEL") or DEFAULT_GEMINI_MODEL


def _resolve_base_url() -> str:
    return (
        _env_first("GEMINI_API_BASE_URL", "GOOGLE_AI_STUDIO_BASE_URL")
        or DEFAULT_GEMINI_BASE_URL
    ).rstrip("/")


def _resolve_timeout_seconds() -> int:
    raw = (
        _env_first("GEMINI_TIMEOUT_SECONDS", "LLM_TIMEOUT_SECONDS")
        or str(DEFAULT_GEMINI_TIMEOUT_SECONDS)
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


def _response_mime_type() -> str | None:
    raw = os.getenv("GEMINI_RESPONSE_MIME_TYPE")
    if raw is None:
        return DEFAULT_RESPONSE_MIME_TYPE
    value = raw.strip()
    if not value or value.lower() in ("none", "off", "false", "0"):
        return None
    return value


def _system_instruction(messages: list[LlmMessage]) -> dict[str, Any] | None:
    system_text = "\n\n".join(
        message.content for message in messages if message.role == "system"
    ).strip()
    if not system_text:
        return None
    return {"parts": [{"text": system_text}]}


def _content_role(message: LlmMessage) -> str:
    if message.role == "assistant":
        return "model"
    return "user"


def _contents(messages: list[LlmMessage]) -> list[dict[str, Any]]:
    contents = [
        {"role": _content_role(message), "parts": [{"text": message.content}]}
        for message in messages
        if message.role != "system"
    ]
    if not contents:
        raise RuntimeError(
            f"Provider {PROVIDER_REF!r} requires at least one user message."
        )
    return contents


def _generation_config() -> dict[str, Any] | None:
    config: dict[str, Any] = {}

    response_mime_type = _response_mime_type()
    if response_mime_type:
        config["responseMimeType"] = response_mime_type

    temperature = _optional_float("GEMINI_TEMPERATURE")
    if temperature is not None:
        config["temperature"] = temperature

    top_p = _optional_float("GEMINI_TOP_P")
    if top_p is not None:
        config["topP"] = top_p

    top_k = _optional_int("GEMINI_TOP_K")
    if top_k is not None:
        config["topK"] = top_k

    max_output_tokens = _optional_int("GEMINI_MAX_OUTPUT_TOKENS")
    if max_output_tokens is not None:
        config["maxOutputTokens"] = max_output_tokens

    return config or None


def _request_payload(request: LlmRequest) -> dict[str, Any]:
    payload: dict[str, Any] = {"contents": _contents(request.messages)}

    system_instruction = _system_instruction(request.messages)
    if system_instruction is not None:
        payload["systemInstruction"] = system_instruction

    generation_config = _generation_config()
    if generation_config is not None:
        payload["generationConfig"] = generation_config

    return payload


def _response_text(candidate: dict[str, Any]) -> str:
    content = candidate.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if not isinstance(parts, list):
        return ""

    text_parts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            text_parts.append(part["text"])
    return "".join(text_parts)


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


class GoogleGeminiProvider:
    def complete(self, request: LlmRequest) -> LlmResult:
        api_key = _resolve_api_key()
        model = _resolve_model()
        base_url = _resolve_base_url()
        model_path = quote(model.removeprefix("models/"), safe="")
        url = f"{base_url}/models/{model_path}:generateContent"

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json=_request_payload(request),
            timeout=_resolve_timeout_seconds(),
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Gemini API request failed with HTTP {response.status_code}: "
                f"{_error_message(response)}"
            )

        raw_response = response.json()
        candidates = raw_response.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            prompt_feedback = raw_response.get("promptFeedback")
            raise RuntimeError(
                "Gemini API returned no candidates"
                + (f": {prompt_feedback}" if prompt_feedback else "")
            )

        candidate = candidates[0]
        if not isinstance(candidate, dict):
            raise RuntimeError(f"Gemini API returned an invalid candidate: {candidate!r}")

        return LlmResult(
            content=_response_text(candidate),
            finish_reason=candidate.get("finishReason"),
            raw_response=raw_response,
            metadata={
                "base_url": base_url,
                "model": model,
                "usage": raw_response.get("usageMetadata"),
            },
        )


Provider = GoogleGeminiProvider
