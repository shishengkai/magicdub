# google-gemini

LLM provider for Google AI Studio's Gemini API using `gemini-3-flash-preview`.

Google AI Studio Gemini API 的 LLM provider，使用 `gemini-3-flash-preview`。

## Provider Key / Provider 配置键

```env
MAGICDUB_LLM_PROVIDER=google-gemini
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/llm/google_gemini/.env` when present. The root `.env` only selects
the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/llm/google_gemini/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

This provider uses the Gemini REST `generateContent` endpoint through the
project's existing `requests` dependency, so it declares no extra Python
packages.

该 provider 通过项目已有的 `requests` 依赖调用 Gemini REST `generateContent`
接口，因此不声明额外 Python 包。

Required:

必填：

- `GEMINI_API_KEY` in `providers/llm/google_gemini/.env`
- `providers/llm/google_gemini/.env` 中的 `GEMINI_API_KEY`

Optional aliases:

可选别名：

- `GOOGLE_AI_STUDIO_API_KEY`
- `GOOGLE_API_KEY`
- `LLM_API_KEY`

Optional overrides:

可选覆盖项：

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

默认情况下，`GEMINI_RESPONSE_MIME_TYPE` 为 `application/json`，与 MagicDub 的翻译阶段匹配。如需非
JSON 用法，可设为空值、`none` 或 `off` 来禁用响应 MIME 覆盖。

## Interface / 接口

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`.

实现 `LlmProvider.complete()`，并返回 MagicDub 标准化的 `LlmResult`。

Gemini uses `systemInstruction` for MagicDub system messages. User messages are
sent as Gemini `user` contents, and assistant messages are sent as Gemini
`model` contents.

Gemini 使用 `systemInstruction` 承载 MagicDub 的系统消息。用户消息会作为 Gemini `user`
内容发送，助手消息会作为 Gemini `model` 内容发送。

## Documentation / 文档

- https://ai.google.dev/gemini-api/docs
- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/api/generate-content
