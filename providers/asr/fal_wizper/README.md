# fal-wizper

ASR provider for fal.ai `fal-ai/wizper`.

## Provider Key

```env
MAGICDUB_ASR_PROVIDER=fal-wizper
```

## Configuration

The provider reads configuration from the process environment and
`providers/asr/fal_wizper/.env` when present. The root `.env` only selects the
active provider.

Required:

- `FAL_KEY` in `providers/asr/fal_wizper/.env`

Optional:

- `FAL_ASR_ENDPOINT`
- `FAL_ASR_MAX_WAIT_SECONDS`

## Interface

Implements `AsrProvider.transcribe()` and converts the FAL `chunks` response into
MagicDub's normalized `TranscriptChunk` list.

## Documentation

- https://fal.ai/models/fal-ai/wizper/api
