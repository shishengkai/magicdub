from __future__ import annotations

import shutil
from pathlib import Path

from constants.filenames import OUTPUT_VIDEO_MP4
from pipeline.context import PipelineContext
from utils.export_path import resolve_magicdub_export_path


def export_result(ctx: PipelineContext) -> Path:

    rel = ctx.state.output_video.path
    if not rel:
        raise RuntimeError("output_video.path is empty")
    src = ctx.workspace / rel
    if not src.is_file():
        src = ctx.workspace / OUTPUT_VIDEO_MP4
    if not src.is_file():
        raise FileNotFoundError("Output video not found in workspace")

    dest = resolve_magicdub_export_path(ctx.input_video)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    ctx.export_path = dest
    ctx.state.output_path = str(dest)
    return dest
