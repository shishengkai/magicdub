from __future__ import annotations

from pathlib import Path

import fal_client
import requests

from config.settings import load_env, require_env
from providers.asset_store.base import DownloadRequest, UploadRequest, UploadResult


def _ensure_fal_configured() -> None:
    load_env()
    require_env("FAL_KEY")


class FalAssetStoreProvider:
    def upload(self, request: UploadRequest) -> UploadResult:
        _ensure_fal_configured()
        path = Path(request.local_path)
        if not path.is_file():
            raise FileNotFoundError(str(path))
        return UploadResult(url=fal_client.upload_file(path))

    def download(self, request: DownloadRequest) -> None:
        r = requests.get(request.url.strip(), timeout=request.timeout_s)
        r.raise_for_status()
        request.dest.parent.mkdir(parents=True, exist_ok=True)
        request.dest.write_bytes(r.content)


class FalCdnProvider(FalAssetStoreProvider):
    pass


Provider = FalCdnProvider
