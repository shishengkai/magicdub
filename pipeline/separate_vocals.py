from __future__ import annotations

from constants.filenames import source_audio_name
from media.resources import MediaSource, prepare_media
from pipeline.context import PipelineContext
from providers.vocal_separation import get_vocal_separation_provider
from providers.vocal_separation.base import VocalSeparationRequest


def separate_vocals(ctx: PipelineContext) -> None:
    source_audio = ctx.workspace / source_audio_name()
    if not source_audio.is_file():
        raise FileNotFoundError(f"Missing {source_audio}")

    provider = get_vocal_separation_provider()
    prepared = prepare_media(
        MediaSource(local_path=source_audio, url=ctx.state.source_audio.url or None),
        provider.audio_requirement(),
    )
    if prepared is None:
        raise RuntimeError("Vocal separation requires an input audio resource")

    result = provider.separate_vocals(VocalSeparationRequest(audio=prepared))
    if result.vocals.kind == "url":
        ctx.state.vocal_track.url = result.vocals.value
    elif result.vocals.kind == "local_path":
        ctx.state.vocal_track.path = ctx.store.rel_path(ctx.abs(result.vocals.value))
    else:
        raise RuntimeError("Vocal separation returned unsupported base64 media")
    ctx.save()
