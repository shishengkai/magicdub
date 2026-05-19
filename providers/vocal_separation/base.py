from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from media.resources import MediaRequirement, PreparedMedia


@dataclass(frozen=True)
class VocalSeparationRequest:
    audio: PreparedMedia


@dataclass(frozen=True)
class VocalSeparationResult:
    vocals: PreparedMedia
    raw_response: dict[str, Any] = field(default_factory=dict)


class VocalSeparationProvider(Protocol):
    def audio_requirement(self) -> MediaRequirement:
        ...

    def separate_vocals(self, request: VocalSeparationRequest) -> VocalSeparationResult:
        ...
