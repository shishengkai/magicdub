# MagicDub

MagicDub is an open-source CLI pipeline for AI video dubbing focused on
source-faithful replacement speech.

MagicDub 是一个开源 AI 视频配音 CLI pipeline，目标是生成尽量忠实于原始声音表现的替换语音。

It takes a source video, extracts and separates audio, transcribes speech,
translates the transcript, synthesizes replacement speech, aligns segment
duration, mixes the final audio, and writes a dubbed video next to the input
file.

它会读取源视频，提取并分离音频，转写语音，翻译文本，合成替换语音，对齐片段时长，混合最终音频，并在输入文件旁输出配音后的视频。

## Core Dubbing Goals / 核心配音目标

MagicDub is designed to produce dubbed speech that stays faithful to the
original performance at sentence level:

MagicDub 的设计目标是在句子级别尽量复刻原始表演：

- Fully time-aligned with the source speech
- 与源语音完整时间对齐
- Duration-matched to the original sentence timing
- 与原句时长匹配
- Sentence-level timbre reproduction of the original voice
- 句子级复刻原声音色
- Sentence-level prosody reproduction of the original voice
- 句子级复刻原声韵律
- Sentence-level emotion reproduction of the original voice
- 句子级复刻原声情绪

The project is built around capability-based provider plugins. The pipeline
depends on stable interfaces such as ASR, TTS, LLM, vocal separation, and asset
storage instead of depending directly on one vendor workflow.

项目围绕“能力域 provider 插件”构建。pipeline 依赖 ASR、TTS、LLM、人声分离、素材存储等稳定接口，而不是直接绑定某一个供应商工作流。

## Status / 状态

This repository is an early open-source CLI version. The provider architecture
is usable, but the end-to-end quality depends heavily on the configured model
providers, input audio quality, and ffmpeg availability.

这是早期开源 CLI 版本。provider 架构已经可用，但端到端质量很大程度取决于所配置的模型 provider、输入音频质量以及 ffmpeg 是否可用。

## Requirements / 运行要求

- Python 3.12+
- Python 3.12+
- `ffmpeg` and `ffprobe` available on `PATH`
- `PATH` 中可用的 `ffmpeg` 和 `ffprobe`
- API keys for the providers you enable
- 已启用 provider 所需的 API key
- macOS, Linux, or another shell environment that can run the bundled CLI script
- macOS、Linux，或其他可以运行随附 CLI 脚本的 shell 环境

Default provider selection uses:

默认 provider 选择如下：

- Asset storage: `fal-cdn`
- 素材存储：`fal-cdn`
- Vocal separation: `fal-demucs`
- 人声分离：`fal-demucs`
- ASR: `fal-wizper`
- 语音识别：`fal-wizper`
- TTS: `fal-index-tts-2`
- 语音合成：`fal-index-tts-2`
- LLM: `google-gemini`
- 大语言模型：`google-gemini`

The default media providers use fal.ai and need `FAL_KEY` in their provider-local
`.env` files. The default LLM provider uses Google Gemini and needs
`GEMINI_API_KEY`.

默认媒体 provider 使用 fal.ai，需要在各自 provider 目录的 `.env` 文件中设置 `FAL_KEY`。默认 LLM
provider 使用 Google Gemini，需要设置 `GEMINI_API_KEY`。

## Installation / 安装

```bash
git clone https://github.com/OpenSiC-ai/magicdub.git
cd magicdub

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
```

Verify the CLI:

验证 CLI：

```bash
magicdub provider list
```

If you run from a local checkout before installation, the shell wrapper also
works:

如果在安装前直接从本地 checkout 运行，也可以使用 shell wrapper：

```bash
scripts/magicdub provider list
```

## Configure Providers / 配置 Provider

The root `.env` selects which provider to use for each capability:

根目录 `.env` 负责选择每个能力域使用哪个 provider：

```bash
MAGICDUB_ASSET_STORE_PROVIDER=fal-cdn
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-demucs
MAGICDUB_ASR_PROVIDER=fal-wizper
MAGICDUB_TTS_PROVIDER=fal-index-tts-2
MAGICDUB_LLM_PROVIDER=google-gemini
```

Provider-specific secrets belong in the provider directory, not in the root
`.env`. Copy the relevant provider example file before running:

provider 专属密钥应放在对应 provider 目录中，而不是根目录 `.env`。运行前请复制相关 provider 示例文件：

```bash
cp providers/asset_store/fal_cdn/.env.example providers/asset_store/fal_cdn/.env
cp providers/vocal_separation/fal_demucs/.env.example providers/vocal_separation/fal_demucs/.env
cp providers/asr/fal_wizper/.env.example providers/asr/fal_wizper/.env
cp providers/tts/fal_index_tts_2/.env.example providers/tts/fal_index_tts_2/.env
cp providers/llm/google_gemini/.env.example providers/llm/google_gemini/.env
```

Then edit those files and add the required keys:

然后编辑这些文件并填入必需的 key：

```bash
providers/asset_store/fal_cdn/.env          # FAL_KEY
providers/vocal_separation/fal_demucs/.env  # FAL_KEY
providers/asr/fal_wizper/.env               # FAL_KEY
providers/tts/fal_index_tts_2/.env          # FAL_KEY
providers/llm/google_gemini/.env            # GEMINI_API_KEY
```

Root `.env` and all provider-local `.env` files are ignored by git. Only
`.env.example` files should be committed.

根目录 `.env` 和所有 provider 本地 `.env` 文件都会被 git 忽略。只有 `.env.example` 文件应该提交。

## Provider Dependencies / Provider 依赖

Some providers use extra Python packages that are intentionally not installed
with the core package. Install them per provider:

部分 provider 使用额外 Python 包，这些包不会随核心包一起安装。请按 provider 单独安装：

```bash
magicdub provider list
magicdub provider install asset_store/fal-cdn
```

Examples:

示例：

```bash
magicdub provider install asr/bailian-fun-asr
magicdub provider install llm/fal-openrouter
magicdub provider uninstall llm/fal-openrouter
```

`magicdub provider uninstall` only removes dependencies that were installed
through MagicDub's provider dependency tracker and are no longer referenced by
another provider.

`magicdub provider uninstall` 只会移除通过 MagicDub provider 依赖跟踪器安装、且不再被其他 provider
引用的依赖。

## Usage / 使用

```bash
magicdub input.mp4 --target-lang zh
```

Optional source language:

可选源语言：

```bash
magicdub input.mp4 --src-lang en --target-lang zh
```

Output:

输出：

```text
input_MagicDub.mp4
```

Task workspaces are created under `.tmp/<task_id>/`.

任务工作区会创建在 `.tmp/<task_id>/` 下。

- On success, MagicDub keeps only `task_state.json`.
- 成功时，MagicDub 只保留 `task_state.json`。
- On failure, MagicDub keeps generated intermediate files for debugging.
- 失败时，MagicDub 会保留生成的中间文件以便调试。

## LLM Provider Options / LLM Provider 选项

Use Google Gemini:

使用 Google Gemini：

```bash
MAGICDUB_LLM_PROVIDER=google-gemini
```

Set `GEMINI_API_KEY` in:

在以下文件中设置 `GEMINI_API_KEY`：

```text
providers/llm/google_gemini/.env
```

Use OpenAI directly:

直接使用 OpenAI：

```bash
MAGICDUB_LLM_PROVIDER=openai-gpt
```

Set `OPENAI_API_KEY` in:

在以下文件中设置 `OPENAI_API_KEY`：

```text
providers/llm/openai_gpt/.env
```

The default OpenAI model is `gpt-5.4-mini`. Override it with `OPENAI_MODEL`.

默认 OpenAI 模型为 `gpt-5.4-mini`。可通过 `OPENAI_MODEL` 覆盖。

Use DeepSeek directly:

直接使用 DeepSeek：

```bash
MAGICDUB_LLM_PROVIDER=deepseek
```

Set `DEEPSEEK_API_KEY` in:

在以下文件中设置 `DEEPSEEK_API_KEY`：

```text
providers/llm/deepseek/.env
```

The default DeepSeek model is `deepseek-v4-flash`.

默认 DeepSeek 模型为 `deepseek-v4-flash`。

Use OpenRouter directly:

直接使用 OpenRouter：

```bash
MAGICDUB_LLM_PROVIDER=openrouter
```

Set `OPENROUTER_API_KEY` in:

在以下文件中设置 `OPENROUTER_API_KEY`：

```text
providers/llm/openrouter/.env
```

The default OpenRouter model is `~google/gemini-flash-latest`.

默认 OpenRouter 模型为 `~google/gemini-flash-latest`。

## Available Providers / 可用 Provider

Current provider keys:

当前 provider key：

```text
asr/bailian-fun-asr
asr/fal-wizper
asset_store/fal-cdn
llm/deepseek
llm/fal-openrouter
llm/google-gemini
llm/openai-gpt
llm/openrouter
tts/fal-index-tts-2
vocal_separation/fal-demucs
vocal_separation/fal-sam-audio
```

Each provider directory contains its own `README.md`, `.env.example`, and
`provider.toml` when provider-specific configuration or dependencies are needed.

当 provider 需要专属配置或依赖时，它的目录会包含自己的 `README.md`、`.env.example` 和
`provider.toml`。

## Architecture / 架构

MagicDub is organized by capability:

MagicDub 按能力域组织：

```text
cli/                         CLI entry points
pipeline/                    End-to-end dubbing stages
schemas/                     Task state models
media/                       Audio, ffmpeg, mixing, and media resource handling
providers/asr/               Speech recognition providers
providers/tts/               Speech synthesis providers
providers/llm/               Translation/text-generation providers
providers/vocal_separation/  Vocal separation providers
providers/asset_store/       Remote asset storage providers
storage/                     Task state and workspace cleanup
utils/                       Shared utilities
```

Provider keys use kebab-case, while Python package directories use snake_case.
For example:

provider key 使用 kebab-case，而 Python 包目录使用 snake_case。例如：

```text
fal-index-tts-2 -> providers/tts/fal_index_tts_2/
google-gemini   -> providers/llm/google_gemini/
```

The runtime loader maps provider keys to modules, loads provider-local `.env`
files, imports the provider package, and instantiates the exported `Provider`
class.

运行时 loader 会将 provider key 映射到模块，加载 provider 本地 `.env` 文件，导入 provider 包，并实例化其导出的
`Provider` 类。

## Adding a Provider / 添加 Provider

Create one provider directory inside the relevant capability:

在对应能力域下创建一个 provider 目录：

```text
providers/tts/company_model/
  __init__.py
  provider.py
  README.md
  .env.example
  provider.toml
```

Expose `Provider` from `__init__.py`:

从 `__init__.py` 导出 `Provider`：

```python
from providers.tts.company_model.provider import CompanyModelProvider as Provider

__all__ = ["Provider"]
```

Declare metadata and optional dependencies in `provider.toml`:

在 `provider.toml` 中声明元数据和可选依赖：

```toml
key = "company-model"
capability = "tts"
name = "Company Model"

[dependencies]
python = [
    "company-sdk>=1.0,<2",
]
```

Enable it in the root `.env`:

在根目录 `.env` 中启用它：

```bash
MAGICDUB_TTS_PROVIDER=company-model
```

### Media Requirements / 媒体输入要求

Providers declare what shape of media input they need. The media resolver then
prepares the requested form, so the pipeline does not hardcode upload,
download, base64, or local-file assumptions.

provider 会声明自己需要哪种形态的媒体输入。media resolver 会准备对应形式，因此 pipeline 不需要硬编码上传、下载、base64
或本地文件假设。

Example:

示例：

```python
from media.resources import MediaRequirement


class CompanyModelProvider:
    def reference_audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="base64")
```

Supported requirement kinds include:

支持的要求类型包括：

- `none`
- `url`
- `public_url`
- `same_provider_url`
- `base64`
- `local_path`

## Development Checks / 开发检查

Useful local checks before publishing or opening a pull request:

发布或提交 pull request 前可使用以下本地检查：

```bash
.venv/bin/python -m compileall -q media providers pipeline config storage cli schemas constants utils magicdub.py __main__.py
.venv/bin/magicdub provider list
.venv/bin/python -m cli provider list
.venv/bin/python -m pip check
git diff --check
```

## Security Notes / 安全说明

Do not commit:

不要提交：

- Root `.env`
- 根目录 `.env`
- Provider-local `.env` files
- provider 本地 `.env` 文件
- `.tmp/`
- `.venv/`
- `.magicdub/`
- Generated media files
- 生成的媒体文件
- Local drafts or private planning notes
- 本地草稿或私有规划笔记

The repository intentionally commits `.env.example` files only. If a real API
key is ever committed or exposed in a remote URL, revoke it immediately and
generate a new one.

仓库只应提交 `.env.example` 文件。如果真实 API key 被提交或暴露在远程 URL 中，请立即吊销并生成新的 key。

## License / 许可证

MagicDub is released under the license in [LICENSE](LICENSE).

MagicDub 按 [LICENSE](LICENSE) 中的许可证发布。
