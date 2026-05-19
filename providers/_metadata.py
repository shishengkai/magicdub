from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import REPO_ROOT

_PROVIDER_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class ProviderManifest:
    capability: str
    key: str
    module_name: str
    path: Path
    name: str
    python_dependencies: tuple[str, ...]

    @property
    def ref(self) -> str:
        return f"{self.capability}/{self.key}"


def provider_module_name(provider_key: str) -> str:
    if not _PROVIDER_KEY_RE.fullmatch(provider_key):
        raise RuntimeError(
            "Invalid provider key: "
            f"{provider_key!r}. Use lowercase letters, numbers, and hyphens only."
        )
    return provider_key.replace("-", "_")


def provider_key_from_module_name(module_name: str) -> str:
    return module_name.replace("_", "-")


def provider_dir(capability: str, provider_key: str) -> Path:
    return REPO_ROOT / "providers" / capability / provider_module_name(provider_key)


def parse_provider_ref(ref: str) -> tuple[str, str]:
    parts = ref.strip().split("/", 1)
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        raise RuntimeError("Provider ref must look like capability/provider-key.")
    capability = parts[0].strip()
    provider_key = parts[1].strip()
    provider_module_name(provider_key)
    return capability, provider_key


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        return {}
    return data


def read_provider_manifest(capability: str, provider_key: str) -> ProviderManifest:
    module_name = provider_module_name(provider_key)
    path = provider_dir(capability, provider_key)
    manifest_path = path / "provider.toml"
    data = _read_toml(manifest_path) if manifest_path.is_file() else {}

    declared_key = str(data.get("key") or provider_key).strip()
    declared_capability = str(data.get("capability") or capability).strip()
    if declared_key != provider_key:
        raise RuntimeError(
            f"{manifest_path} declares key={declared_key!r}, expected {provider_key!r}."
        )
    if declared_capability != capability:
        raise RuntimeError(
            f"{manifest_path} declares capability={declared_capability!r}, "
            f"expected {capability!r}."
        )

    dependencies = data.get("dependencies")
    python_dependencies: tuple[str, ...] = ()
    if isinstance(dependencies, dict):
        raw_python = dependencies.get("python")
        if isinstance(raw_python, list):
            python_dependencies = tuple(
                str(item).strip() for item in raw_python if str(item).strip()
            )

    return ProviderManifest(
        capability=capability,
        key=provider_key,
        module_name=module_name,
        path=path,
        name=str(data.get("name") or provider_key).strip(),
        python_dependencies=python_dependencies,
    )


def discover_provider_manifests() -> list[ProviderManifest]:
    providers_root = REPO_ROOT / "providers"
    manifests: list[ProviderManifest] = []
    if not providers_root.is_dir():
        return manifests

    for capability_dir in sorted(p for p in providers_root.iterdir() if p.is_dir()):
        if capability_dir.name.startswith("__"):
            continue
        capability = capability_dir.name
        for item in sorted(p for p in capability_dir.iterdir() if p.is_dir()):
            if item.name.startswith("__"):
                continue
            if not (item / "provider.toml").is_file() and not (item / "provider.py").is_file():
                continue
            key = provider_key_from_module_name(item.name)
            manifests.append(read_provider_manifest(capability, key))
    return manifests
