from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from config.settings import load_env
from pipeline.align_segment_duration import align_segment_duration
from pipeline.compose_output_video import compose_output_video_stage
from pipeline.context import PipelineContext
from pipeline.create_instrumental_track import create_instrumental_track
from pipeline.export_result import export_result
from pipeline.extract_source_audio import extract_source_audio_stage
from pipeline.initialize_task import initialize_task
from pipeline.prepare_source_video import prepare_source_video
from pipeline.separate_vocals import separate_vocals
from pipeline.split_vocal_segments import split_vocal_segments
from pipeline.synthesize_segments import synthesize_segments
from pipeline.transcribe_speech import transcribe_speech
from pipeline.translate_transcript import translate_transcript
from storage.workspace_cleanup import cleanup_workspace_after_success
from utils.logging import log_stage
from utils.time import local_iso_timestamp

StageFn = Callable[[PipelineContext], None]

STAGES: list[tuple[str, StageFn]] = [
    ("prepare_source_video", prepare_source_video),
    ("extract_source_audio", extract_source_audio_stage),
    ("separate_vocals", separate_vocals),
    ("create_instrumental_track", create_instrumental_track),
    ("transcribe_speech", transcribe_speech),
    ("translate_transcript", translate_transcript),
    ("split_vocal_segments", split_vocal_segments),
    ("synthesize_segments", synthesize_segments),
    ("align_segment_duration", align_segment_duration),
    ("compose_output_video", compose_output_video_stage),
]


def run_pipeline(
    *,
    input_video: Path,
    target_lang: str,
    src_lang: str | None,
) -> Path:
    load_env()
    ctx = initialize_task(
        input_video=input_video,
        target_lang=target_lang,
        src_lang=src_lang,
    )
    total = len(STAGES) + 1
    try:
        for i, (name, fn) in enumerate(STAGES, start=1):
            log_stage(i, total, name)
            fn(ctx)
        log_stage(total, total, "export_result")
        out = export_result(ctx)
        ctx.state.status = "completed"
        ctx.state.completed_at = local_iso_timestamp()
        cleanup_workspace_after_success(ctx.workspace, ctx.state)
        return out
    except Exception:
        ctx.state.status = "failed"
        ctx.state.completed_at = ""
        try:
            ctx.save()
        except Exception:
            pass
        raise
