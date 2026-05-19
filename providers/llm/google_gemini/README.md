# google-gemini

LLM provider for Google AI Studio's Gemini API using `gemini-3-flash-preview`.

## Provider Key

```env
MAGICDUB_LLM_PROVIDER=google-gemini
```

## Configuration

The provider reads configuration from the process environment and
`providers/llm/google_gemini/.env` when present. The root `.env` only selects
the active provider.

This provider uses the Gemini REST `generateContent` endpoint through the
project's existing `requests` dependency, so it declares no extra Python
packages.

Required:

- `GEMINI_API_KEY` in `providers/llm/google_gemini/.env`

Optional aliases:

- `GOOGLE_AI_STUDIO_API_KEY`
- `GOOGLE_API_KEY`
- `LLM_API_KEY`

Optional overrides:

- `GEMINI_MODEL`
- `GEMINI_API_BASE_URL`
- `GEMINI_TIMEOUT_SECONDS`
- `GEMINI_RESPONSE_MIME_TYPE`
- `GEMINI_TEMPERATURE`
- `GEMINI_TOP_P`
- `GEMINI_TOP_K`
- `GEMINI_MAX_OUTPUT_TOKENS`

By default, `GEMINI_RESPONSE_MIME_TYPE` is `application/json`, which matches
MagicDub's translation stage. Set it to an empty value, `none`, or `off` to
disable the response MIME override for non-JSON use.

## Interface

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`.

Gemini uses `systemInstruction` for MagicDub system messages. User messages are
sent as Gemini `user` contents, and assistant messages are sent as Gemini
`model` contents.

## Documentation

- https://ai.google.dev/gemini-api/docs
- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/api/generate-content
