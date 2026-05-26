# fal-sam-audio

Text-guided vocal separation via [fal.ai SAM Audio](https://fal.ai/models/fal-ai/sam-audio/separate/api).

通过 [fal.ai SAM Audio](https://fal.ai/models/fal-ai/sam-audio/separate/api) 进行文本引导的人声分离。

## Provider Key / Provider 配置键

```env
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-sam-audio
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/vocal_separation/fal_sam_audio/.env` when present. The root `.env`
only selects the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/vocal_separation/fal_sam_audio/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Required:

必填：

- `FAL_KEY` in `providers/vocal_separation/fal_sam_audio/.env`
- `providers/vocal_separation/fal_sam_audio/.env` 中的 `FAL_KEY`

Optional:

可选：

- `FAL_SAM_AUDIO_ENDPOINT`

## Fixed API Parameters / 固定 API 参数

These are hardcoded in the provider implementation:

以下参数在 provider 实现中固定写入：

| Parameter | Value |
|-----------|-------|
| `prompt` | `speech` |
| `predict_spans` | `false` |
| `reranking_candidates` | `1` |
| `acceleration` | `balanced` |
| `max_chunk_duration` | `60` |
| `chunk_overlap` | `5` |
| `output_format` | `mp3` |

The isolated `target` track is mapped to MagicDub's vocal track.

分离出的 `target` 轨会映射为 MagicDub 的人声轨。

## Interface / 接口

Implements `VocalSeparationProvider.separate_vocals()` and returns MagicDub's
normalized `VocalSeparationResult`.

实现 `VocalSeparationProvider.separate_vocals()`，并返回 MagicDub 标准化的
`VocalSeparationResult`。

## Documentation / 文档

- https://fal.ai/models/fal-ai/sam-audio/separate/api
