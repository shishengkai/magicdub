from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from config.settings import default_target_lang, load_env
from pipeline.runner import run_pipeline

load_env()

app = typer.Typer(
    name="magicdub",
    help="MagicDub — AI video dubbing pipeline",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def main(
    input_video: Path = typer.Argument(..., help="Path to input video file"),
    target_lang: Optional[str] = typer.Option(
        default_target_lang(),
        "--target-lang",
        help="Target language code for translation (default: MAGICDUB_TARGET_LANG in .env)",
    ),
    src_lang: Optional[str] = typer.Option(
        None,
        "--src-lang",
        help="Source language for ASR (omit for auto-detect)",
    ),
) -> None:
    """Process a video and write {stem}_MagicDub{ext} next to the input file."""
    input_path = input_video.expanduser().resolve()
    if not input_path.is_file():
        typer.echo(f"File not found: {input_path}", err=True)
        raise typer.Exit(code=1)

    resolved_target_lang = (target_lang or "").strip()
    if not resolved_target_lang:
        typer.echo(
            "Missing target language: set MAGICDUB_TARGET_LANG in .env "
            "or pass --target-lang",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Input: {input_path}")

    try:
        out = run_pipeline(
            input_video=input_path,
            target_lang=resolved_target_lang,
            src_lang=src_lang.strip() if src_lang else None,
        )
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    typer.echo(f"Done! {out}")


if __name__ == "__main__":
    app()
