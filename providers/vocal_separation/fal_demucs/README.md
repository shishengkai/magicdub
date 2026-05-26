# fal-demucs

Vocal separation provider for fal.ai Demucs.

fal.ai Demucs 的人声分离 provider。

## Provider Key / Provider 配置键

```env
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-demucs
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/vocal_separation/fal_demucs/.env` when present. The root `.env` only
selects the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/vocal_separation/fal_demucs/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Required:

必填：

- `FAL_KEY` in `providers/vocal_separation/fal_demucs/.env`
- `providers/vocal_separation/fal_demucs/.env` 中的 `FAL_KEY`

Optional:

可选：

- `FAL_DEMUCS_ENDPOINT`
- `FAL_DEMUCS_MODEL`
- `FAL_DEMUCS_SHIFTS`
- `FAL_DEMUCS_OVERLAP`

## Interface / 接口

Implements `VocalSeparationProvider.separate_vocals()` and returns MagicDub's
normalized `VocalSeparationResult`.

实现 `VocalSeparationProvider.separate_vocals()`，并返回 MagicDub 标准化的
`VocalSeparationResult`。

## Documentation / 文档

- https://fal.ai/models/fal-ai/demucs/api
