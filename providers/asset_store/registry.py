from __future__ import annotations

from providers._loader import load_provider, load_provider_by_key
from providers.asset_store.base import AssetStoreProvider


def get_asset_store_provider(provider_key: str | None = None) -> AssetStoreProvider:
    if provider_key:
        return load_provider_by_key("asset_store", provider_key)
    return load_provider(
        "asset_store",
        "MAGICDUB_ASSET_STORE_PROVIDER",
        "fal-cdn",
    )
