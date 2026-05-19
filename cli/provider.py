from __future__ import annotations

import typer

from providers._installer import (
    install_provider_dependencies,
    installed_packages_for_provider,
    state_path,
    uninstall_provider_dependencies,
)
from providers._metadata import (
    discover_provider_manifests,
    parse_provider_ref,
    read_provider_manifest,
)

app = typer.Typer(
    name="provider",
    help="Manage MagicDub provider dependencies",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command("list")
def list_providers() -> None:
    """List local providers and their managed dependency state."""
    manifests = discover_provider_manifests()
    if not manifests:
        typer.echo("No providers found.")
        return

    for manifest in manifests:
        deps = ", ".join(manifest.python_dependencies) or "-"
        installed = ", ".join(installed_packages_for_provider(manifest.ref)) or "-"
        typer.echo(f"{manifest.ref}\t{manifest.name}\tdeps: {deps}\tinstalled: {installed}")


@app.command("install")
def install(ref: str = typer.Argument(..., help="Provider ref, e.g. asr/bailian-fun-asr")) -> None:
    """Install Python dependencies declared by a provider."""
    capability, provider_key = parse_provider_ref(ref)
    manifest = read_provider_manifest(capability, provider_key)
    installed = install_provider_dependencies(manifest)
    if installed:
        typer.echo(f"Installed dependencies for {manifest.ref}: {', '.join(installed)}")
        typer.echo(f"Dependency state: {state_path()}")
    else:
        typer.echo(f"{manifest.ref} declares no Python dependencies.")


@app.command("uninstall")
def uninstall(
    ref: str = typer.Argument(..., help="Provider ref, e.g. asr/bailian-fun-asr"),
) -> None:
    """Uninstall dependencies that are only referenced by this provider."""
    capability, provider_key = parse_provider_ref(ref)
    manifest = read_provider_manifest(capability, provider_key)
    removed = uninstall_provider_dependencies(manifest)
    if removed:
        typer.echo(f"Uninstalled dependencies for {manifest.ref}: {', '.join(removed)}")
        typer.echo(f"Dependency state: {state_path()}")
    else:
        typer.echo(
            f"No dependencies were uninstalled for {manifest.ref}. "
            "They may be shared, already untracked, or not declared."
        )
