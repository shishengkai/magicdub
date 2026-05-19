from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from config.settings import load_env
from pipeline.runner import run_pipeline

app = typer.Typer(
    name="magicdub",
    help="MagicDub — AI video dubbing pipeline",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def main(
    input_video: Path = typer.Argument(..., help="Path to input video file"),
    target_lang: str = typer.Option(
        ...,
        "--target-lang",
        help="Target language code for translation (required)",
    ),
    src_lang: Optional[str] = typer.Option(
        None,
        "--src-lang",
        help="Source language for ASR (omit for auto-detect)",
    ),
) -> None:
    """Process a video and write {stem}_MagicDub{ext} next to the input file."""
    load_env()

    input_path = input_video.expanduser().resolve()
    if not input_path.is_file():
        typer.echo(f"File not found: {input_path}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Input: {input_path}")

    try:
        out = run_pipeline(
            input_video=input_path,
            target_lang=target_lang.strip(),
            src_lang=src_lang.strip() if src_lang else None,
        )
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    typer.echo(f"Done! {out}")


if __name__ == "__main__":
    app()
