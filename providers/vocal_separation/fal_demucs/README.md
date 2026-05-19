# fal-demucs

Vocal separation provider for fal.ai Demucs.

## Provider Key

```env
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-demucs
```

## Configuration

The provider reads configuration from the process environment and
`providers/vocal_separation/fal_demucs/.env` when present. The root `.env` only
selects the active provider.

Required:

- `FAL_KEY` in `providers/vocal_separation/fal_demucs/.env`

Optional:

- `FAL_DEMUCS_ENDPOINT`
- `FAL_DEMUCS_MODEL`
- `FAL_DEMUCS_SHIFTS`
- `FAL_DEMUCS_OVERLAP`

## Interface

Implements `VocalSeparationProvider.separate_vocals()` and returns MagicDub's
normalized `VocalSeparationResult`.

## Documentation

- https://fal.ai/models/fal-ai/demucs/api
