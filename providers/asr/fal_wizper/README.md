# fal-wizper

ASR provider for fal.ai `fal-ai/wizper`.

fal.ai `fal-ai/wizper` 的语音识别 provider。

## Provider Key / Provider 配置键

```env
MAGICDUB_ASR_PROVIDER=fal-wizper
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/asr/fal_wizper/.env` when present. The root `.env` only selects the
active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/asr/fal_wizper/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Required:

必填：

- `FAL_KEY` in `providers/asr/fal_wizper/.env`
- `providers/asr/fal_wizper/.env` 中的 `FAL_KEY`

Optional:

可选：

- `FAL_ASR_ENDPOINT`
- `FAL_ASR_MAX_WAIT_SECONDS`

## Interface / 接口

Implements `AsrProvider.transcribe()` and converts the FAL `chunks` response into
MagicDub's normalized `TranscriptChunk` list.

实现 `AsrProvider.transcribe()`，并将 FAL 返回的 `chunks` 转换为 MagicDub 标准化的
`TranscriptChunk` 列表。

## Documentation / 文档

- https://fal.ai/models/fal-ai/wizper/api
