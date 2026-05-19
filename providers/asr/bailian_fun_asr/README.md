# bailian-fun-asr

ASR provider for Alibaba Cloud Bailian [Fun-ASR](https://help.aliyun.com/zh/model-studio/fun-asr-recorded-speech-recognition-restful-api) recorded speech recognition (RESTful API).

Fixed request parameters:

- `model=fun-asr`
- `parameters.diarization_enabled=true`

## Provider Key

```env
MAGICDUB_ASR_PROVIDER=bailian-fun-asr
```

## Configuration

The provider reads configuration from the process environment and
`providers/asr/bailian_fun_asr/.env` when present. The root `.env` only selects
the active provider.

Install provider dependencies with:

```bash
magicdub provider install asr/bailian-fun-asr
```

Required:

- `DASHSCOPE_API_KEY` — Bailian / DashScope API Key

Optional:

- `DASHSCOPE_BASE_URL` — default `https://dashscope.aliyuncs.com` (Singapore: `https://dashscope-intl.aliyuncs.com`)
- `DASHSCOPE_ASR_MAX_WAIT_SECONDS` — async poll timeout (default `3600`)

## Interface

Implements `AsrProvider.transcribe()`:

1. Submit async transcription task with a public audio URL
2. Poll task status until `SUCCEEDED`
3. Download the JSON at `transcription_url`
4. Map `transcripts[].sentences[]` to `TranscriptChunk` (`begin_time` / `end_time` in ms)

Audio must be reachable via HTTP/HTTPS (`public_url` media requirement).

## Documentation

- [Fun-ASR RESTful API](https://help.aliyun.com/zh/model-studio/fun-asr-recorded-speech-recognition-restful-api)
- [Get API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
