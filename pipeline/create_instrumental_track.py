from __future__ import annotations

from pathlib import Path

from config.settings import vocal_subtract_alpha
from constants.filenames import (
    instrumental_track_name,
    source_audio_name,
    vocal_track_name,
    VOCAL_TRACK_RAW_STEM,
    external_audio,
)
from media.audio import resample_like_reference
from media.audio_format import resolve_media_extension
from media.mixing import subtract_instrumental
from media.resources import MediaRequirement, prepare_media, source_from_ref
from pipeline.context import PipelineContext


def create_instrumental_track(ctx: PipelineContext) -> None:
    mix_path = ctx.workspace / source_audio_name()
    if not mix_path.is_file():
        raise FileNotFoundError(f"Missing {mix_path}")

    raw_ext = resolve_media_extension(
        url=ctx.state.vocal_track.url or None,
        path=ctx.state.vocal_track.path or None,
    )
    vocal_raw = ctx.workspace / external_audio(VOCAL_TRACK_RAW_STEM, raw_ext)
    prepared_vocal = prepare_media(
        source_from_ref(
            workspace=ctx.workspace,
            path=ctx.state.vocal_track.path,
            url=ctx.state.vocal_track.url,
        ),
        MediaRequirement(kind="local_path"),
        local_dest=vocal_raw,
    )
    if prepared_vocal is None:
        raise RuntimeError("vocal_track is missing; run separate_vocals first")

    vocal_path = ctx.workspace / vocal_track_name()
    resample_like_reference(Path(prepared_vocal.value), mix_path, vocal_path)
    ctx.state.vocal_track.path = ctx.store.rel_path(vocal_path)

    instrumental_path = ctx.workspace / instrumental_track_name()
    subtract_instrumental(
        mix_path,
        vocal_path,
        instrumental_path,
        vocal_gain=vocal_subtract_alpha(),
    )
    ctx.state.instrumental_track.path = ctx.store.rel_path(instrumental_path)
    ctx.save()
