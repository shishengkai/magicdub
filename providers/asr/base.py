from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from media.resources import MediaRequirement, PreparedMedia


@dataclass(frozen=True)
class AsrRequest:
    audio: PreparedMedia
    src_lang: str | None = None


@dataclass(frozen=True)
class TranscriptChunk:
    start_ms: int
    end_ms: int
    text: str

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)


@dataclass(frozen=True)
class AsrResult:
    full_text: str
    chunks: list[TranscriptChunk] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)


def languages_to_src_lang(languages: list[str]) -> str | None:
    codes = [code.strip().lower() for code in languages if isinstance(code, str) and code.strip()]
    if not codes:
        return None
    return ",".join(codes)


class AsrProvider(Protocol):
    def audio_requirement(self) -> MediaRequirement:
        ...

    def transcribe(self, request: AsrRequest) -> AsrResult:
        ...
