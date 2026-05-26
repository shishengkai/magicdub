# openrouter

LLM provider for direct OpenRouter API access. The default model is
`~google/gemini-flash-latest`, OpenRouter's latest alias for the Google Gemini
Flash family.

直接访问 OpenRouter API 的 LLM provider。默认模型为 `~google/gemini-flash-latest`，这是
OpenRouter 对 Google Gemini Flash 系列的最新别名。

## Provider Key / Provider 配置键

```env
MAGICDUB_LLM_PROVIDER=openrouter
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/llm/openrouter/.env` when present. The root `.env` only selects the
active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/llm/openrouter/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

This provider calls OpenRouter's OpenAI-compatible Chat Completions REST
endpoint through the project's existing `requests` dependency, so it declares no
extra Python packages.

该 provider 通过项目已有的 `requests` 依赖调用 OpenRouter 兼容 OpenAI 的 Chat Completions
REST 接口，因此不声明额外 Python 包。

Required:

必填：

- `OPENROUTER_API_KEY` in `providers/llm/openrouter/.env`
- `providers/llm/openrouter/.env` 中的 `OPENROUTER_API_KEY`

Optional aliases:

可选别名：

- `LLM_API_KEY`

Optional overrides:

可选覆盖项：

- `OPENROUTER_MODEL`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_TIMEOUT_SECONDS`
- `OPENROUTER_RESPONSE_FORMAT`
- `OPENROUTER_TEMPERATURE`
- `OPENROUTER_TOP_P`
- `OPENROUTER_TOP_K`
- `OPENROUTER_MAX_TOKENS`

By default:

默认值：

- `OPENROUTER_MODEL=~google/gemini-flash-latest`
- `OPENROUTER_RESPONSE_FORMAT=json_object`
- `HTTP-Referer: https://magicdub.com`
- `X-OpenRouter-Title: MagicDub`
- `X-OpenRouter-Categories: video-gen`

The OpenRouter app attribution headers are fixed in code and are not configured
through `.env`.

OpenRouter 应用归因请求头固定在代码中，不通过 `.env` 配置。

`OPENROUTER_RESPONSE_FORMAT=json_object` matches MagicDub's translation stage.
Set it to `text`, `none`, or `off` if you need non-JSON behavior.

`OPENROUTER_RESPONSE_FORMAT=json_object` 与 MagicDub 的翻译阶段匹配。如果需要非 JSON 行为，可设为
`text`、`none` 或 `off`。

## Interface / 接口

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`. OpenRouter's returned concrete model id is preserved in
`LlmResult.metadata["resolved_model"]` when present.

实现 `LlmProvider.complete()`，并返回 MagicDub 标准化的 `LlmResult`。如果 OpenRouter
返回具体模型 ID，会保存在 `LlmResult.metadata["resolved_model"]` 中。

## Documentation / 文档

- https://openrouter.ai/~google/gemini-flash-latest/api
- https://openrouter.ai/docs/quickstart
- https://openrouter.ai/docs/api/reference/overview
