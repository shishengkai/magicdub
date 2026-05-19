from __future__ import annotations

from pathlib import Path

from constants.filenames import (
    dubbed_segment_stem,
    external_audio,
    pipeline_audio,
    source_segment_stem,
)
from media.audio_format import resolve_media_extension
from media.resources import MediaRequirement, MediaSource, prepare_media, source_from_ref
from pipeline.context import PipelineContext
from providers.tts import get_tts_provider
from providers.tts.base import TtsRequest


def synthesize_segments(ctx: PipelineContext) -> None:
    provider = get_tts_provider()
    requirement = provider.reference_audio_requirement()
    for seg in ctx.state.transcript.segments:
        if not seg.translated_text:
            raise RuntimeError(f"translated_text missing for segment {seg.segment_id}")
        prepared_ref = prepare_media(
            source_from_ref(
                workspace=ctx.workspace,
                path=seg.source_segment.path,
                url=seg.source_segment.url,
            ),
            requirement,
            local_dest=ctx.workspace / pipeline_audio(source_segment_stem(seg.segment_id)),
        )
        result = provider.synthesize(
            TtsRequest(text=seg.translated_text, reference_audio=prepared_ref)
        )
        if result.audio.kind == "url":
            seg.dubbed_segment.url = result.audio.value
        elif result.audio.kind == "local_path":
            seg.dubbed_segment.path = ctx.store.rel_path(Path(result.audio.value))
        elif result.audio.kind == "base64":
            ext = resolve_media_extension(mime_type=result.audio.mime_type)
            dubbed_local = ctx.workspace / external_audio(
                dubbed_segment_stem(seg.segment_id),
                ext,
            )
            local = prepare_media(
                MediaSource(base64_data=result.audio.value, mime_type=result.audio.mime_type),
                MediaRequirement(kind="local_path"),
                local_dest=dubbed_local,
            )
            if local is None:
                raise RuntimeError(f"Cannot materialize TTS result for segment {seg.segment_id}")
            seg.dubbed_segment.path = ctx.store.rel_path(Path(local.value))
    ctx.save()
