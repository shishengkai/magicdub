# openai-gpt

LLM provider for the OpenAI API. The default model is `gpt-5.4-mini`, selected
as the closest OpenAI mini-tier match for Gemini Flash-style translation
workloads: high quality, lower latency, and lower cost than flagship models.

OpenAI API 的 LLM provider。默认模型为 `gpt-5.4-mini`，它是最接近 Gemini Flash
式翻译工作负载的 OpenAI mini 档模型：质量较高，延迟和成本低于旗舰模型。

## Provider Key / Provider 配置键

```env
MAGICDUB_LLM_PROVIDER=openai-gpt
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/llm/openai_gpt/.env` when present. The root `.env` only selects the
active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/llm/openai_gpt/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

This provider calls OpenAI's Chat Completions REST endpoint through the
project's existing `requests` dependency, so it declares no extra Python
packages.

该 provider 通过项目已有的 `requests` 依赖调用 OpenAI Chat Completions REST
接口，因此不声明额外 Python 包。

Required:

必填：

- `OPENAI_API_KEY` in `providers/llm/openai_gpt/.env`
- `providers/llm/openai_gpt/.env` 中的 `OPENAI_API_KEY`

Optional aliases:

可选别名：

- `LLM_API_KEY`

Optional overrides:

可选覆盖项：

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

默认情况下，`OPENAI_RESPONSE_FORMAT` 为 `json_object`，与 MagicDub 的翻译阶段匹配。如果需要非
JSON 行为，可设为 `text`、`none` 或 `off`。

## Interface / 接口

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`.

实现 `LlmProvider.complete()`，并返回 MagicDub 标准化的 `LlmResult`。

## Documentation / 文档

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.4-mini
- https://platform.openai.com/docs/api-reference/chat/create
