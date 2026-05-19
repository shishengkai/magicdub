# MagicDub

MagicDub is an open-source CLI pipeline for AI video dubbing focused on
source-faithful replacement speech.

It takes a source video, extracts and separates audio, transcribes speech,
translates the transcript, synthesizes replacement speech, aligns segment
duration, mixes the final audio, and writes a dubbed video next to the input
file.

## Core Dubbing Goals

MagicDub is designed to produce dubbed speech that stays faithful to the
original performance at sentence level:

- Fully time-aligned with the source speech
- Duration-matched to the original sentence timing
- Sentence-level timbre reproduction of the original voice
- Sentence-level prosody reproduction of the original voice
- Sentence-level emotion reproduction of the original voice

The project is built around capability-based provider plugins. The pipeline
depends on stable interfaces such as ASR, TTS, LLM, vocal separation, and asset
storage instead of depending directly on one vendor workflow.

## Status

This repository is an early open-source CLI version. The provider architecture
is usable, but the end-to-end quality depends heavily on the configured model
providers, input audio quality, and ffmpeg availability.

## Requirements

- Python 3.12+
- `ffmpeg` and `ffprobe` available on `PATH`
- API keys for the providers you enable
- macOS, Linux, or another shell environment that can run the bundled CLI script

Default provider selection uses:

- Asset storage: `fal-cdn`
- Vocal separation: `fal-demucs`
- ASR: `fal-wizper`
- TTS: `fal-index-tts-2`
- LLM: `google-gemini`

The default media providers use fal.ai and need `FAL_KEY` in their provider-local
`.env` files. The default LLM provider uses Google Gemini and needs
`GEMINI_API_KEY`.

## Installation

```bash
git clone https://github.com/OpenSiC-ai/magicdub.git
cd magicdub

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
```

Verify the CLI:

```bash
magicdub --help
magicdub provider list
```

If you run from a local checkout before installation, the shell wrapper also
works:

```bash
scripts/magicdub --help
```

## Configure Providers

The root `.env` selects which provider to use for each capability:

```bash
MAGICDUB_ASSET_STORE_PROVIDER=fal-cdn
MAGICDUB_VOCAL_SEPARATION_PROVIDER=fal-demucs
MAGICDUB_ASR_PROVIDER=fal-wizper
MAGICDUB_TTS_PROVIDER=fal-index-tts-2
MAGICDUB_LLM_PROVIDER=google-gemini
```

Provider-specific secrets belong in the provider directory, not in the root
`.env`. Copy the relevant provider example file before running:

```bash
cp providers/asset_store/fal_cdn/.env.example providers/asset_store/fal_cdn/.env
cp providers/vocal_separation/fal_demucs/.env.example providers/vocal_separation/fal_demucs/.env
cp providers/asr/fal_wizper/.env.example providers/asr/fal_wizper/.env
cp providers/tts/fal_index_tts_2/.env.example providers/tts/fal_index_tts_2/.env
cp providers/llm/google_gemini/.env.example providers/llm/google_gemini/.env
```

Then edit those files and add the required keys:

```bash
providers/asset_store/fal_cdn/.env          # FAL_KEY
providers/vocal_separation/fal_demucs/.env  # FAL_KEY
providers/asr/fal_wizper/.env               # FAL_KEY
providers/tts/fal_index_tts_2/.env          # FAL_KEY
providers/llm/google_gemini/.env            # GEMINI_API_KEY
```

Root `.env` and all provider-local `.env` files are ignored by git. Only
`.env.example` files should be committed.

## Provider Dependencies

Some providers use extra Python packages that are intentionally not installed
with the core package. Install them per provider:

```bash
magicdub provider list
magicdub provider install asset_store/fal-cdn
```

Examples:

```bash
magicdub provider install asr/bailian-fun-asr
magicdub provider install llm/fal-openrouter
magicdub provider uninstall llm/fal-openrouter
```

`magicdub provider uninstall` only removes dependencies that were installed
through MagicDub's provider dependency tracker and are no longer referenced by
another provider.

## Usage

```bash
magicdub input.mp4 --target-lang zh
```

Optional source language:

```bash
magicdub input.mp4 --src-lang en --target-lang zh
```

Output:

```text
input_MagicDub.mp4
```

Task workspaces are created under `.tmp/<task_id>/`.

- On success, MagicDub keeps only `task_state.json`.
- On failure, MagicDub keeps generated intermediate files for debugging.

## LLM Provider Options

Use Google Gemini:

```bash
MAGICDUB_LLM_PROVIDER=google-gemini
```

Set `GEMINI_API_KEY` in:

```text
providers/llm/google_gemini/.env
```

Use OpenAI directly:

```bash
MAGICDUB_LLM_PROVIDER=openai-gpt
```

Set `OPENAI_API_KEY` in:

```text
providers/llm/openai_gpt/.env
```

The default OpenAI model is `gpt-5.4-mini`. Override it with `OPENAI_MODEL`.

Use DeepSeek directly:

```bash
MAGICDUB_LLM_PROVIDER=deepseek
```

Set `DEEPSEEK_API_KEY` in:

```text
providers/llm/deepseek/.env
```

The default DeepSeek model is `deepseek-v4-flash`.

Use OpenRouter directly:

```bash
MAGICDUB_LLM_PROVIDER=openrouter
```

Set `OPENROUTER_API_KEY` in:

```text
providers/llm/openrouter/.env
```

The default OpenRouter model is `~google/gemini-flash-latest`.

## Available Providers

Current provider keys:

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

## Architecture

MagicDub is organized by capability:

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

```text
fal-index-tts-2 -> providers/tts/fal_index_tts_2/
google-gemini   -> providers/llm/google_gemini/
```

The runtime loader maps provider keys to modules, loads provider-local `.env`
files, imports the provider package, and instantiates the exported `Provider`
class.

## Adding a Provider

Create one provider directory inside the relevant capability:

```text
providers/tts/company_model/
  __init__.py
  provider.py
  README.md
  .env.example
  provider.toml
```

Expose `Provider` from `__init__.py`:

```python
from providers.tts.company_model.provider import CompanyModelProvider as Provider

__all__ = ["Provider"]
```

Declare metadata and optional dependencies in `provider.toml`:

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

```bash
MAGICDUB_TTS_PROVIDER=company-model
```

### Media Requirements

Providers declare what shape of media input they need. The media resolver then
prepares the requested form, so the pipeline does not hardcode upload,
download, base64, or local-file assumptions.

Example:

```python
from media.resources import MediaRequirement


class CompanyModelProvider:
    def reference_audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="base64")
```

Supported requirement kinds include:

- `none`
- `url`
- `public_url`
- `same_provider_url`
- `base64`
- `local_path`

## Development Checks

Useful local checks before publishing or opening a pull request:

```bash
.venv/bin/python -m compileall -q media providers pipeline config storage cli schemas constants utils magicdub.py __main__.py
.venv/bin/magicdub --help
.venv/bin/magicdub provider list
.venv/bin/python -m pip check
git diff --check
```

## Security Notes

Do not commit:

- Root `.env`
- Provider-local `.env` files
- `.tmp/`
- `.venv/`
- `.magicdub/`
- Generated media files
- Local drafts or private planning notes

The repository intentionally commits `.env.example` files only. If a real API
key is ever committed or exposed in a remote URL, revoke it immediately and
generate a new one.

## License

MagicDub is released under the license in [LICENSE](LICENSE).
