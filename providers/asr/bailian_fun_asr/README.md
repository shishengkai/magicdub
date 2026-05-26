# bailian-fun-asr

ASR provider for Alibaba Cloud Bailian [Fun-ASR](https://help.aliyun.com/zh/model-studio/fun-asr-recorded-speech-recognition-restful-api) recorded speech recognition (RESTful API).

阿里云百炼 [Fun-ASR](https://help.aliyun.com/zh/model-studio/fun-asr-recorded-speech-recognition-restful-api) 录音文件识别（RESTful API）的语音识别 provider。

Fixed request parameters:

固定请求参数：

- `model=fun-asr`
- `parameters.diarization_enabled=true`

## Provider Key / Provider 配置键

```env
MAGICDUB_ASR_PROVIDER=bailian-fun-asr
```

## Configuration / 配置

The provider reads configuration from the process environment and
`providers/asr/bailian_fun_asr/.env` when present. The root `.env` only selects
the active provider.

该 provider 会从进程环境变量读取配置；如果存在
`providers/asr/bailian_fun_asr/.env`，也会读取其中的配置。根目录 `.env` 只负责选择当前启用的
provider。

Install provider dependencies with:

使用以下命令安装该 provider 的依赖：

```bash
magicdub provider install asr/bailian-fun-asr
```

Required:

必填：

- `DASHSCOPE_API_KEY` - Bailian / DashScope API Key
- `DASHSCOPE_API_KEY` - 百炼 / DashScope API Key

Optional:

可选：

- `DASHSCOPE_BASE_URL` - default `https://dashscope.aliyuncs.com` (Singapore: `https://dashscope-intl.aliyuncs.com`)
- `DASHSCOPE_BASE_URL` - 默认 `https://dashscope.aliyuncs.com`（新加坡：`https://dashscope-intl.aliyuncs.com`）
- `DASHSCOPE_ASR_MAX_WAIT_SECONDS` - async poll timeout (default `3600`)
- `DASHSCOPE_ASR_MAX_WAIT_SECONDS` - 异步轮询超时时间（默认 `3600`）

## Interface / 接口

Implements `AsrProvider.transcribe()`:

实现 `AsrProvider.transcribe()`：

1. Submit async transcription task with a public audio URL
2. Poll task status until `SUCCEEDED`
3. Download the JSON at `transcription_url`
4. Map `transcripts[].sentences[]` to `TranscriptChunk` (`begin_time` / `end_time` in ms)

1. 使用公开音频 URL 提交异步转写任务
2. 轮询任务状态直到 `SUCCEEDED`
3. 下载 `transcription_url` 指向的 JSON
4. 将 `transcripts[].sentences[]` 映射为 `TranscriptChunk`（`begin_time` / `end_time` 单位为毫秒）

Audio must be reachable via HTTP/HTTPS (`public_url` media requirement).

音频必须能通过 HTTP/HTTPS 访问（`public_url` 媒体要求）。

## Documentation / 文档

- [Fun-ASR RESTful API](https://help.aliyun.com/zh/model-studio/fun-asr-recorded-speech-recognition-restful-api)
- [Get API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
