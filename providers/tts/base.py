from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from media.resources import MediaRequirement, PreparedMedia


@dataclass(frozen=True)
class TtsRequest:
    text: str
    reference_audio: PreparedMedia | None = None
    language: str | None = None
    speaker: str | None = None


@dataclass(frozen=True)
class TtsResult:
    audio: PreparedMedia
    duration_ms: int | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)


class TtsProvider(Protocol):
    def reference_audio_requirement(self) -> MediaRequirement:
        ...

    def synthesize(self, request: TtsRequest) -> TtsResult:
        ...
