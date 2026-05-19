from __future__ import annotations

import importlib
from types import ModuleType

from providers._installer import provider_install_command


def require_provider_dependency(
    import_name: str,
    *,
    provider_ref: str,
) -> ModuleType:
    try:
        return importlib.import_module(import_name)
    except ModuleNotFoundError as exc:
        if exc.name != import_name:
            raise
        raise RuntimeError(
            f"Provider {provider_ref!r} requires Python package {import_name!r}. "
            f"Install it with: {provider_install_command(provider_ref)}"
        ) from exc
