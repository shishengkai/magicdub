from __future__ import annotations

from constants.filenames import vocal_track_name
from media.resources import prepare_media, source_from_ref
from schemas.task import TranscriptSegment
from pipeline.context import PipelineContext
from providers.asr import get_asr_provider
from providers.asr.base import AsrRequest, languages_to_src_lang


def transcribe_speech(ctx: PipelineContext) -> None:
    vocal_path = ctx.workspace / vocal_track_name()
    if not vocal_path.is_file():
        raise FileNotFoundError(f"Missing {vocal_path}")

    provider = get_asr_provider()
    prepared = prepare_media(
        source_from_ref(
            workspace=ctx.workspace,
            path=ctx.state.vocal_track.path,
            url=ctx.state.vocal_track.url,
        ),
        provider.audio_requirement(),
    )
    if prepared is None:
        raise RuntimeError("ASR requires an input audio resource")

    result = provider.transcribe(
        AsrRequest(audio=prepared, src_lang=ctx.state.config.src_lang)
    )

    segments: list[TranscriptSegment] = []
    for i, ch in enumerate(result.chunks):
        segments.append(
            TranscriptSegment(
                segment_id=f"{i + 1:04d}",
                start_ms=ch.start_ms,
                end_ms=ch.end_ms,
                duration_ms=ch.duration_ms,
                source_text=ch.text,
            )
        )

    ctx.state.transcript.full_text = result.full_text
    ctx.state.transcript.segments = segments
    detected_src_lang = languages_to_src_lang(result.languages)
    if detected_src_lang:
        ctx.state.config.src_lang = detected_src_lang
    ctx.save()
