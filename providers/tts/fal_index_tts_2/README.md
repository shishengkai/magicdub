# fal-index-tts-2

TTS provider for fal.ai `fal-ai/index-tts-2`.

## Provider Key

```env
MAGICDUB_TTS_PROVIDER=fal-index-tts-2
```

## Configuration

The provider reads configuration from the process environment and
`providers/tts/fal_index_tts_2/.env` when present. The root `.env` only selects
the active provider.

Required:

- `FAL_KEY` in `providers/tts/fal_index_tts_2/.env`

Optional:

- `FAL_TTS_ENDPOINT`

## Interface

Implements `TtsProvider.synthesize()` and adapts MagicDub's `TtsRequest` to the
FAL payload fields `audio_url`, `prompt`, and `emotional_audio_url`.

## Documentation

- https://fal.ai/models/fal-ai/index-tts-2/text-to-speech/api
