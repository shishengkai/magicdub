# fal-sam-audio

Text-guided vocal separation via [fal.ai SAM Audio](https://fal.ai/models/fal-ai/sam-audio/separate/api).

## Provider Key

```env
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-sam-audio
```

## Configuration

The provider reads configuration from the process environment and
`providers/vocal_separation/fal_sam_audio/.env` when present. The root `.env`
only selects the active provider.

Required:

- `FAL_KEY` in `providers/vocal_separation/fal_sam_audio/.env`

Optional:

- `FAL_SAM_AUDIO_ENDPOINT`

## Fixed API Parameters

These are hardcoded in the provider implementation:

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

## Interface

Implements `VocalSeparationProvider.separate_vocals()` and returns MagicDub's
normalized `VocalSeparationResult`.

## Documentation

- https://fal.ai/models/fal-ai/sam-audio/separate/api
