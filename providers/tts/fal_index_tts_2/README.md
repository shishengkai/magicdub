# fal-index-tts-2

TTS provider for fal.ai `fal-ai/index-tts-2`.

fal.ai `fal-ai/index-tts-2` 的语音合成 provider。

## Provider Key / Provider 配置键

```env
MAGICDUB_TTS_PROVIDER=fal-index-tts-2
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/tts/fal_index_tts_2/.env` when present. The root `.env` only selects
the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/tts/fal_index_tts_2/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Required:

必填：

- `FAL_KEY` in `providers/tts/fal_index_tts_2/.env`
- `providers/tts/fal_index_tts_2/.env` 中的 `FAL_KEY`

Optional:

可选：

- `FAL_TTS_ENDPOINT`

## Interface / 接口

Implements `TtsProvider.synthesize()` and adapts MagicDub's `TtsRequest` to the
FAL payload fields `audio_url`, `prompt`, and `emotional_audio_url`.

实现 `TtsProvider.synthesize()`，并将 MagicDub 的 `TtsRequest` 适配为 FAL 请求字段
`audio_url`、`prompt` 和 `emotional_audio_url`。

## Documentation / 文档

- https://fal.ai/models/fal-ai/index-tts-2/text-to-speech/api
