from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from providers.asset_store import get_asset_store_provider
from providers.asset_store.base import DownloadRequest, UploadRequest

MediaRequirementKind = Literal[
    "none",
    "url",
    "public_url",
    "same_provider_url",
    "base64",
    "local_path",
]
PreparedMediaKind = Literal["url", "base64", "local_path"]


@dataclass(frozen=True)
class MediaRequirement:
    kind: MediaRequirementKind
    asset_store_provider: str | None = None


@dataclass(frozen=True)
class MediaSource:
    local_path: Path | None = None
    url: str | None = None
    base64_data: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class PreparedMedia:
    kind: PreparedMediaKind
    value: str
    mime_type: str | None = None


def guess_mime_type(path: Path | None, fallback: str | None = None) -> str | None:
    if path is None:
        return fallback
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or fallback


def prepare_media(
    source: MediaSource,
    requirement: MediaRequirement,
    *,
    local_dest: Path | None = None,
) -> PreparedMedia | None:
    if requirement.kind == "none":
        return None

    if requirement.kind in ("url", "public_url", "same_provider_url"):
        if source.url:
            return PreparedMedia(kind="url", value=source.url, mime_type=source.mime_type)
        if source.local_path is None:
            raise RuntimeError("Media source has no URL or local path")
        provider = get_asset_store_provider(requirement.asset_store_provider)
        result = provider.upload(UploadRequest(local_path=source.local_path))
        return PreparedMedia(
            kind="url",
            value=result.url,
            mime_type=guess_mime_type(source.local_path, source.mime_type),
        )

    if requirement.kind == "local_path":
        if source.local_path is not None and source.local_path.is_file():
            return PreparedMedia(
                kind="local_path",
                value=str(source.local_path),
                mime_type=guess_mime_type(source.local_path, source.mime_type),
            )
        if local_dest is None:
            raise RuntimeError("local_dest is required to prepare media as local_path")
        if source.url:
            provider = get_asset_store_provider(requirement.asset_store_provider)
            provider.download(DownloadRequest(url=source.url, dest=local_dest))
            return PreparedMedia(
                kind="local_path",
                value=str(local_dest),
                mime_type=guess_mime_type(local_dest, source.mime_type),
            )
        if source.base64_data:
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            local_dest.write_bytes(base64.b64decode(source.base64_data))
            return PreparedMedia(
                kind="local_path",
                value=str(local_dest),
                mime_type=guess_mime_type(local_dest, source.mime_type),
            )
        raise RuntimeError("Media source cannot be prepared as local_path")

    if requirement.kind == "base64":
        if source.base64_data:
            return PreparedMedia(
                kind="base64",
                value=source.base64_data,
                mime_type=source.mime_type,
            )
        local = source.local_path
        if local is None:
            if local_dest is None:
                raise RuntimeError("local_dest is required to prepare URL media as base64")
            local_prepared = prepare_media(
                source,
                MediaRequirement(
                    kind="local_path",
                    asset_store_provider=requirement.asset_store_provider,
                ),
                local_dest=local_dest,
            )
            if local_prepared is None:
                raise RuntimeError("Media source cannot be prepared as base64")
            local = Path(local_prepared.value)
        return PreparedMedia(
            kind="base64",
            value=base64.b64encode(local.read_bytes()).decode("ascii"),
            mime_type=guess_mime_type(local, source.mime_type),
        )

    raise RuntimeError(f"Unsupported media requirement: {requirement.kind}")


def source_from_ref(
    *,
    workspace: Path,
    path: str = "",
    url: str = "",
    mime_type: str | None = None,
) -> MediaSource:
    local_path: Path | None = None
    if path:
        p = Path(path)
        local_path = p if p.is_absolute() else workspace / p
    return MediaSource(local_path=local_path, url=url or None, mime_type=mime_type)
