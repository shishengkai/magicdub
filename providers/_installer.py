from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from config.settings import REPO_ROOT
from providers._metadata import ProviderManifest

_STATE_PATH = REPO_ROOT / ".magicdub" / "provider-deps.json"


def state_path() -> Path:
    return _STATE_PATH


def load_dependency_state() -> dict[str, list[str]]:
    if not _STATE_PATH.is_file():
        return {}
    data = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    state: dict[str, list[str]] = {}
    for package, refs in data.items():
        if not isinstance(refs, list):
            continue
        state[str(package)] = sorted({str(ref) for ref in refs if str(ref).strip()})
    return state


def save_dependency_state(state: dict[str, list[str]]) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean = {
        package: sorted({ref for ref in refs if ref})
        for package, refs in sorted(state.items())
        if refs
    }
    _STATE_PATH.write_text(
        json.dumps(clean, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def requirement_package_name(requirement: str) -> str:
    value = requirement.strip()
    if not value:
        raise RuntimeError("Empty requirement.")

    for marker in (";", "[", "<", ">", "=", "!", "~", " "):
        if marker in value:
            value = value.split(marker, 1)[0]
    return value.strip().replace("_", "-").lower()


def provider_install_command(provider_ref: str) -> str:
    return f"magicdub provider install {provider_ref}"


def install_provider_dependencies(manifest: ProviderManifest) -> list[str]:
    requirements = list(manifest.python_dependencies)
    if not requirements:
        return []

    subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])

    state = load_dependency_state()
    for requirement in requirements:
        package = requirement_package_name(requirement)
        refs = set(state.get(package, []))
        refs.add(manifest.ref)
        state[package] = sorted(refs)
    save_dependency_state(state)
    return requirements


def uninstall_provider_dependencies(manifest: ProviderManifest) -> list[str]:
    requirements = list(manifest.python_dependencies)
    if not requirements:
        return []

    state = load_dependency_state()
    packages_to_uninstall: list[str] = []
    for requirement in requirements:
        package = requirement_package_name(requirement)
        refs = set(state.get(package, []))
        if manifest.ref not in refs:
            continue
        refs.remove(manifest.ref)
        if refs:
            state[package] = sorted(refs)
        else:
            state.pop(package, None)
            packages_to_uninstall.append(package)

    if packages_to_uninstall:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "uninstall", "-y", *packages_to_uninstall]
        )
    save_dependency_state(state)
    return packages_to_uninstall


def installed_refs_by_package() -> dict[str, list[str]]:
    return load_dependency_state()


def installed_packages_for_provider(provider_ref: str) -> list[str]:
    packages: list[str] = []
    for package, refs in load_dependency_state().items():
        if provider_ref in refs:
            packages.append(package)
    return sorted(packages)
