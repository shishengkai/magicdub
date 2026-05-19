from __future__ import annotations

from constants.filenames import (
    OUTPUT_VIDEO_MP4,
    instrumental_track_name,
    vocal_track_name,
    source_video_name,
)
from media.mixing import compose_output_video
from pipeline.context import PipelineContext


def compose_output_video_stage(ctx: PipelineContext) -> None:
    ext = ctx.state.source_video.extension or ".mp4"
    video = ctx.workspace / source_video_name(ext)
    instrumental = ctx.workspace / instrumental_track_name()
    vocal_bed = ctx.workspace / vocal_track_name()
    output = ctx.workspace / OUTPUT_VIDEO_MP4

    if not video.is_file():
        raise FileNotFoundError(f"Missing {video}")
    if not instrumental.is_file():
        raise FileNotFoundError(f"Missing {instrumental}")
    if not vocal_bed.is_file():
        raise FileNotFoundError(f"Missing {vocal_bed}")

    aligned_clips = []
    for seg in ctx.state.transcript.segments:
        rel = seg.aligned_segment.path
        if not rel:
            raise RuntimeError(f"aligned_segment.path missing for {seg.segment_id}")
        clip = ctx.workspace / rel
        if not clip.is_file():
            raise FileNotFoundError(f"Missing aligned clip: {clip}")
        aligned_clips.append((seg, clip))

    compose_output_video(
        video_path=video,
        instrumental_path=instrumental,
        vocal_bed_path=vocal_bed,
        aligned_clips=aligned_clips,
        output_path=output,
    )
    ctx.state.output_video.path = ctx.store.rel_path(output)
    ctx.save()
