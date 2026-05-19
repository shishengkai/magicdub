from __future__ import annotations

import mimetypes
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

_SUPPORTED_PIPELINE_AUDIO_EXT = frozenset({".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"})

_MIME_TO_EXT: dict[str, str] = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/wave": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "audio/webm": ".webm",
}

_KNOWN_AUDIO_EXTENSIONS = frozenset(_MIME_TO_EXT.values())


def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if not ext:
        return ""
    return ext if ext.startswith(".") else f".{ext}"


@lru_cache
def pipeline_audio_ext() -> str:
    """Canonical extension for pipeline-produced audio (configurable via env)."""
    raw = os.getenv("MAGICDUB_PIPELINE_AUDIO_EXT", ".wav").strip()
    ext = _normalize_ext(raw) or ".wav"
    if ext not in _SUPPORTED_PIPELINE_AUDIO_EXT:
        supported = ", ".join(sorted(_SUPPORTED_PIPELINE_AUDIO_EXT))
        raise RuntimeError(
            f"Unsupported MAGICDUB_PIPELINE_AUDIO_EXT: {raw!r}. Supported: {supported}"
        )
    return ext


def ffmpeg_audio_output_args(output_path: Path) -> list[str]:
    """ffmpeg output arguments matching the destination file extension."""
    ext = _normalize_ext(output_path.suffix)
    if ext == ".wav":
        return ["-acodec", "pcm_s16le"]
    if ext == ".mp3":
        return ["-acodec", "libmp3lame", "-q:a", "2"]
    if ext in (".m4a", ".aac"):
        return ["-acodec", "aac", "-b:a", "192k"]
    if ext == ".flac":
        return ["-acodec", "flac"]
    if ext == ".ogg":
        return ["-acodec", "libvorbis", "-q:a", "5"]
    raise RuntimeError(
        f"Unsupported audio output extension {ext!r} for {output_path.name}. "
        f"Set MAGICDUB_PIPELINE_AUDIO_EXT to one of: {', '.join(sorted(_SUPPORTED_PIPELINE_AUDIO_EXT))}"
    )


def extension_from_path(path: str | Path | None) -> str:
    if not path:
        return ""
    suffix = _normalize_ext(Path(path).suffix)
    if suffix in _KNOWN_AUDIO_EXTENSIONS:
        return suffix
    return ""


def extension_from_url(url: str | None) -> str:
    if not url:
        return ""
    path = urlparse(url.strip()).path
    return extension_from_path(path)


def extension_from_mime(mime_type: str | None) -> str:
    if not mime_type:
        return ""
    mime = mime_type.split(";", 1)[0].strip().lower()
    if mime in _MIME_TO_EXT:
        return _MIME_TO_EXT[mime]
    guessed = mimetypes.guess_extension(mime) or ""
    return _normalize_ext(guessed) if guessed in _KNOWN_AUDIO_EXTENSIONS else ""


def resolve_media_extension(
    *,
    url: str | None = None,
    path: str | Path | None = None,
    mime_type: str | None = None,
    default: str = ".bin",
) -> str:
    for resolver in (
        lambda: extension_from_path(path),
        lambda: extension_from_url(url),
        lambda: extension_from_mime(mime_type),
    ):
        ext = resolver()
        if ext:
            return ext
    return _normalize_ext(default) or ".bin"
