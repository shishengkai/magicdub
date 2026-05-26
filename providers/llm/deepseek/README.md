# deepseek

LLM provider for the DeepSeek API. The default model is `deepseek-v4-flash`
with thinking enabled and `reasoning_effort=high`.

DeepSeek API 的 LLM provider。默认模型为 `deepseek-v4-flash`，启用 thinking，并设置
`reasoning_effort=high`。

## Provider Key / Provider 配置键

```env
MAGICDUB_LLM_PROVIDER=deepseek
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/llm/deepseek/.env` when present. The root `.env` only selects the
active provider.

该 provider 会从进程环境变量读取配置；如果存在 `providers/llm/deepseek/.env`，也会读取其中的配置。根目录
`.env` 只负责选择当前启用的 provider。

DeepSeek uses an OpenAI-compatible Chat Completions API. This provider calls the
REST endpoint through the project's existing `requests` dependency, so it
declares no extra Python packages.

DeepSeek 使用兼容 OpenAI 的 Chat Completions API。该 provider 通过项目已有的
`requests` 依赖调用 REST 接口，因此不声明额外 Python 包。

Required:

必填：

- `DEEPSEEK_API_KEY` in `providers/llm/deepseek/.env`
- `providers/llm/deepseek/.env` 中的 `DEEPSEEK_API_KEY`

Optional aliases:

可选别名：

- `LLM_API_KEY`

Optional overrides:

可选覆盖项：

- `DEEPSEEK_MODEL`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_TIMEOUT_SECONDS`
- `DEEPSEEK_THINKING`
- `DEEPSEEK_REASONING_EFFORT`
- `DEEPSEEK_RESPONSE_FORMAT`
- `DEEPSEEK_MAX_TOKENS`

By default:

默认值：

- `DEEPSEEK_MODEL=deepseek-v4-flash`
- `DEEPSEEK_THINKING=enabled`
- `DEEPSEEK_REASONING_EFFORT=high`
- `DEEPSEEK_RESPONSE_FORMAT=json_object`

`DEEPSEEK_RESPONSE_FORMAT=json_object` matches MagicDub's translation stage. Set
it to `text`, `none`, or `off` if you need non-JSON behavior.

`DEEPSEEK_RESPONSE_FORMAT=json_object` 与 MagicDub 的翻译阶段匹配。如果需要非 JSON 行为，可设为
`text`、`none` 或 `off`。

## Interface / 接口

Implements `LlmProvider.complete()` and returns MagicDub's normalized
`LlmResult`. DeepSeek's returned `reasoning_content` is preserved in
`LlmResult.metadata["reasoning_content"]`; `LlmResult.content` contains the
final answer.

实现 `LlmProvider.complete()`，并返回 MagicDub 标准化的 `LlmResult`。DeepSeek 返回的
`reasoning_content` 会保存在 `LlmResult.metadata["reasoning_content"]` 中；
`LlmResult.content` 保存最终答案。

## Documentation / 文档

- https://api-docs.deepseek.com/zh-cn/
- https://api-docs.deepseek.com/zh-cn/guides/thinking_mode
- https://api-docs.deepseek.com/zh-cn/guides/json_mode
