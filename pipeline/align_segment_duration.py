from __future__ import annotations

from pathlib import Path

from constants.filenames import aligned_segment_audio_name, dubbed_segment_stem, external_audio
from media.audio import align_audio_duration
from media.audio_format import resolve_media_extension
from media.resources import MediaRequirement, prepare_media, source_from_ref
from pipeline.context import PipelineContext


def align_segment_duration(ctx: PipelineContext) -> None:
    for seg in ctx.state.transcript.segments:
        ext = resolve_media_extension(
            url=seg.dubbed_segment.url or None,
            path=seg.dubbed_segment.path or None,
        )
        dubbed_local = ctx.workspace / external_audio(dubbed_segment_stem(seg.segment_id), ext)
        prepared = prepare_media(
            source_from_ref(
                workspace=ctx.workspace,
                path=seg.dubbed_segment.path,
                url=seg.dubbed_segment.url,
            ),
            MediaRequirement(kind="local_path"),
            local_dest=dubbed_local,
        )
        if prepared is None:
            raise RuntimeError(f"dubbed_segment media missing for segment {seg.segment_id}")
        dubbed_local = ctx.abs(prepared.value)
        seg.dubbed_segment.path = ctx.store.rel_path(dubbed_local)

        aligned = ctx.workspace / aligned_segment_audio_name(seg.segment_id)
        align_audio_duration(dubbed_local, aligned, float(seg.duration_ms))
        seg.aligned_segment.path = ctx.store.rel_path(aligned)
    ctx.save()
