# openai-gpt

LLM provider for the OpenAI API. The default model is `gpt-5.4-mini`, selected
as the closest OpenAI mini-tier match for Gemini Flash-style translation
workloads: high quality, lower latency, and lower cost than flagship models.

## Provider Key

```env
MAGICDUB_LLM_PROVIDER=openai-gpt
```

## Configuration

The provider reads configuration from the process environment and
`providers/llm/openai_gpt/.env` when present. The root `.env` only selects the
active provider.

This provider calls OpenAI's Chat Completions REST endpoint through the
project's existing `requests` dependency, so it declares no extra Python
packages.

Required:

- `OPENAI_API_KEY` in `providers/llm/openai_gpt/.env`

Optional aliases:

- `LLM_API_KEY`

Optional overrides:

- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `OPENAI_TIMEOUT_SECONDS`
- `OPENAI_RESPONSE_FORMAT`
- `OPENAI_TEMPERATURE`
- `OPENAI_TOP_P`
- `OPENAI_MAX_COMPLETION_TOKENS`

By default, `OPENAI_RESPONSE_FORMAT` is `json_object`, which matches MagicDub's
translation stage. Set it to `text`, `none`, or `off` if you need non-JSON
behavior.

## Interface

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`.

## Documentation

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.4-mini
- https://platform.openai.com/docs/api-reference/chat/create
