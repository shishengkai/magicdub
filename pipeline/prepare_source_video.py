from __future__ import annotations

import shutil

from constants.filenames import source_video_name
from pipeline.context import PipelineContext


def prepare_source_video(ctx: PipelineContext) -> None:
    ext = ctx.state.source_video.extension or ".mp4"
    dest = ctx.workspace / source_video_name(ext)
    shutil.copy2(ctx.input_video, dest)
    ctx.state.source_video.path = ctx.store.rel_path(dest)
    ctx.save()
