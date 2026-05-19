# deepseek

LLM provider for the DeepSeek API. The default model is `deepseek-v4-flash`
with thinking enabled and `reasoning_effort=high`.

## Provider Key

```env
MAGICDUB_LLM_PROVIDER=deepseek
```

## Configuration

The provider reads configuration from the process environment and
`providers/llm/deepseek/.env` when present. The root `.env` only selects the
active provider.

DeepSeek uses an OpenAI-compatible Chat Completions API. This provider calls the
REST endpoint through the project's existing `requests` dependency, so it
declares no extra Python packages.

Required:

- `DEEPSEEK_API_KEY` in `providers/llm/deepseek/.env`

Optional aliases:

- `LLM_API_KEY`

Optional overrides:

- `DEEPSEEK_MODEL`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_TIMEOUT_SECONDS`
- `DEEPSEEK_THINKING`
- `DEEPSEEK_REASONING_EFFORT`
- `DEEPSEEK_RESPONSE_FORMAT`
- `DEEPSEEK_MAX_TOKENS`

By default:

- `DEEPSEEK_MODEL=deepseek-v4-flash`
- `DEEPSEEK_THINKING=enabled`
- `DEEPSEEK_REASONING_EFFORT=high`
- `DEEPSEEK_RESPONSE_FORMAT=json_object`

`DEEPSEEK_RESPONSE_FORMAT=json_object` matches MagicDub's translation stage. Set
it to `text`, `none`, or `off` if you need non-JSON behavior.

## Interface

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`. DeepSeek's returned `reasoning_content` is preserved in
`LlmResult.metadata["reasoning_content"]`; `LlmResult.content` contains the
final answer.

## Documentation

- https://api-docs.deepseek.com/zh-cn/
- https://api-docs.deepseek.com/zh-cn/guides/thinking_mode
- https://api-docs.deepseek.com/zh-cn/guides/json_mode
