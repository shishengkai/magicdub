from __future__ import annotations

from constants.filenames import segment_audio_name, vocal_track_name
from media.audio import cut_segment
from pipeline.context import PipelineContext


def split_vocal_segments(ctx: PipelineContext) -> None:
    vocal_path = ctx.workspace / vocal_track_name()
    if not vocal_path.is_file():
        raise FileNotFoundError(f"Missing {vocal_path}")

    for seg in ctx.state.transcript.segments:
        out_wav = ctx.workspace / segment_audio_name(seg.segment_id)
        cut_segment(vocal_path, out_wav, seg.start_ms, seg.end_ms)
        seg.source_segment.path = ctx.store.rel_path(out_wav)
    ctx.save()
