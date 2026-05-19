# openrouter

LLM provider for direct OpenRouter API access. The default model is
`~google/gemini-flash-latest`, OpenRouter's latest alias for the Google Gemini
Flash family.

## Provider Key

```env
MAGICDUB_LLM_PROVIDER=openrouter
```

## Configuration

The provider reads configuration from the process environment and
`providers/llm/openrouter/.env` when present. The root `.env` only selects the
active provider.

This provider calls OpenRouter's OpenAI-compatible Chat Completions REST
endpoint through the project's existing `requests` dependency, so it declares no
extra Python packages.

Required:

- `OPENROUTER_API_KEY` in `providers/llm/openrouter/.env`

Optional aliases:

- `LLM_API_KEY`

Optional overrides:

- `OPENROUTER_MODEL`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_TIMEOUT_SECONDS`
- `OPENROUTER_RESPONSE_FORMAT`
- `OPENROUTER_TEMPERATURE`
- `OPENROUTER_TOP_P`
- `OPENROUTER_TOP_K`
- `OPENROUTER_MAX_TOKENS`

By default:

- `OPENROUTER_MODEL=~google/gemini-flash-latest`
- `OPENROUTER_RESPONSE_FORMAT=json_object`
- `HTTP-Referer: https://magicdub.com`
- `X-OpenRouter-Title: MagicDub`
- `X-OpenRouter-Categories: video-gen`

The OpenRouter app attribution headers are fixed in code and are not configured
through `.env`.

`OPENROUTER_RESPONSE_FORMAT=json_object` matches MagicDub's translation stage.
Set it to `text`, `none`, or `off` if you need non-JSON behavior.

## Interface

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`. OpenRouter's returned concrete model id is preserved in
`LlmResult.metadata["resolved_model"]` when present.

## Documentation

- https://openrouter.ai/~google/gemini-flash-latest/api
- https://openrouter.ai/docs/quickstart
- https://openrouter.ai/docs/api/reference/overview
