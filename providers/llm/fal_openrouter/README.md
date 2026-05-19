# fal-openrouter

LLM provider for the OpenAI-compatible FAL OpenRouter endpoint.

## Provider Key

```env
MAGICDUB_LLM_PROVIDER=fal-openrouter
```

## Configuration

The provider reads configuration from the process environment and
`providers/llm/fal_openrouter/.env` when present. The root `.env` only selects
the active provider.

Install provider dependencies with:

```bash
magicdub provider install llm/fal-openrouter
```

Required:

- `FAL_KEY` in `providers/llm/fal_openrouter/.env` when `LLM_API_KEY` is unset

Optional:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_AUTH_SCHEME`
- `LLM_REASONING_ENABLED`
- `LLM_EXTRA_BODY_JSON`

When `LLM_API_KEY` is unset, MagicDub falls back to `FAL_KEY`.

If `LLM_BASE_URL` is changed to a direct `openrouter.ai` URL, MagicDub sends
OpenRouter app attribution headers by default:

- `HTTP-Referer: https://magicdub.com`
- `X-OpenRouter-Title: MagicDub`
- `X-OpenRouter-Categories: video-gen`

These attribution headers are fixed in code and are not configured through
`.env`.

## Interface

Implements `LlmProvider.complete()` and returns MagicDub's normalized `LlmResult`.

## Documentation

- https://fal.ai/models/openrouter/router/openai/v1/chat/completions/api
