from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Protocol, TypeVar, cast

from dotenv import load_dotenv

from config.settings import REPO_ROOT
from providers._installer import provider_install_command
from providers._metadata import (
    provider_dir,
    provider_module_name,
    read_provider_manifest,
)

_T = TypeVar("_T")


class _ProviderFactory(Protocol[_T]):
    def __call__(self) -> _T:
        ...


def load_provider_env(capability: str, module_name: str) -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    provider_key = module_name.replace("_", "-")
    new_env = provider_dir(capability, provider_key) / ".env"
    legacy_env = REPO_ROOT / "providers" / capability / f"{module_name}.env"
    load_dotenv(new_env, override=False)
    load_dotenv(legacy_env, override=False)


def load_provider(capability: str, env_name: str, default_key: str) -> _T:
    load_dotenv(REPO_ROOT / ".env", override=False)
    provider_key = os.getenv(env_name, default_key).strip() or default_key
    return load_provider_by_key(capability, provider_key)


def load_provider_by_key(capability: str, provider_key: str) -> _T:
    module_name = provider_module_name(provider_key)
    load_provider_env(capability, module_name)

    import_name = f"providers.{capability}.{module_name}"
    try:
        module = importlib.import_module(import_name)
    except ModuleNotFoundError as exc:
        if exc.name not in (import_name, f"{import_name}.provider"):
            manifest = read_provider_manifest(capability, provider_key)
            if manifest.python_dependencies:
                raise RuntimeError(
                    f"Provider {provider_key!r} for {capability} is missing "
                    f"Python dependency {exc.name!r}. Install provider dependencies with: "
                    f"{provider_install_command(manifest.ref)}"
                ) from exc
            raise
        expected = (
            f"providers/{capability}/{module_name}/provider.py "
            f"or providers/{capability}/{module_name}.py"
        )
        raise RuntimeError(
            f"Provider {provider_key!r} not found for {capability}. Expected {expected}."
        ) from exc

    provider_factory = getattr(module, "Provider", None)
    if provider_factory is None:
        raise RuntimeError(
            f"Provider module providers.{capability}.{module_name} must expose Provider."
        )
    return cast(_ProviderFactory[_T], provider_factory)()


def provider_doc_path(capability: str, provider_key: str) -> Path:
    module_name = provider_module_name(provider_key)
    doc_path = provider_dir(capability, provider_key) / "README.md"
    if doc_path.is_file():
        return doc_path
    return REPO_ROOT / "providers" / capability / f"{module_name}.md"
