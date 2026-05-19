from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class UploadRequest:
    local_path: Path


@dataclass(frozen=True)
class UploadResult:
    url: str
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    dest: Path
    timeout_s: int = 1800


class AssetStoreProvider(Protocol):
    def upload(self, request: UploadRequest) -> UploadResult:
        ...

    def download(self, request: DownloadRequest) -> None:
        ...
