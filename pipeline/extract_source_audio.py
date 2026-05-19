from __future__ import annotations

from constants.filenames import source_audio_name, source_video_name
from media.audio import extract_source_audio
from pipeline.context import PipelineContext


def extract_source_audio_stage(ctx: PipelineContext) -> None:
    ext = ctx.state.source_video.extension or ".mp4"
    video = ctx.workspace / source_video_name(ext)
    out = ctx.workspace / source_audio_name()
    extract_source_audio(video, out)
    ctx.state.source_audio.path = ctx.store.rel_path(out)
    ctx.save()
