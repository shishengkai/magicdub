# fal-openrouter

LLM provider for the OpenAI-compatible FAL OpenRouter endpoint.

兼容 OpenAI 的 FAL OpenRouter endpoint 的 LLM provider。

## Provider Key / Provider 配置键

```env
MAGICDUB_LLM_PROVIDER=fal-openrouter
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/llm/fal_openrouter/.env` when present. The root `.env` only selects
the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/llm/fal_openrouter/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Install provider dependencies with:

使用以下命令安装该 provider 的依赖：

```bash
magicdub provider install llm/fal-openrouter
```

Required:

必填：

- `FAL_KEY` in `providers/llm/fal_openrouter/.env` when `LLM_API_KEY` is unset
- 未设置 `LLM_API_KEY` 时，需在 `providers/llm/fal_openrouter/.env` 中设置 `FAL_KEY`

Optional:

可选：

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_AUTH_SCHEME`
- `LLM_REASONING_ENABLED`
- `LLM_EXTRA_BODY_JSON`

When `LLM_API_KEY` is unset, MagicDub falls back to `FAL_KEY`.

未设置 `LLM_API_KEY` 时，MagicDub 会回退使用 `FAL_KEY`。

If `LLM_BASE_URL` is changed to a direct `openrouter.ai` URL, MagicDub sends
OpenRouter app attribution headers by default:

如果 `LLM_BASE_URL` 改为直接访问 `openrouter.ai` 的 URL，MagicDub 默认会发送 OpenRouter
应用归因请求头：

- `HTTP-Referer: https://magicdub.com`
- `X-OpenRouter-Title: MagicDub`
- `X-OpenRouter-Categories: video-gen`

These attribution headers are fixed in code and are not configured through
`.env`.

这些归因请求头固定在代码中，不通过 `.env` 配置。

## Interface / 接口

Implements `LlmProvider.complete()` and returns MagicDub's normalized `LlmResult`.

实现 `LlmProvider.complete()`，并返回 MagicDub 标准化的 `LlmResult`。

## Documentation / 文档

- https://fal.ai/models/openrouter/router/openai/v1/chat/completions/api
