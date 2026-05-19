from __future__ import annotations

import json
import re
from typing import Any

from schemas.task import TranscriptSegment
from pipeline.context import PipelineContext
from providers.llm import get_llm_provider
from providers.llm.base import LlmMessage, LlmRequest


def _extract_json_object(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if not raw:
        raise RuntimeError("Model returned empty content, cannot parse JSON")
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    return json.loads(raw)


def _targets_from_response(obj: dict[str, Any]) -> dict[str, str]:
    target_list = obj.get("translated_sentences")
    if not isinstance(target_list, list):
        raise RuntimeError(f"LLM JSON missing translated_sentences: {obj}")
    target_by_id: dict[str, str] = {}
    for t in target_list:
        if not isinstance(t, dict):
            continue
        sid = t.get("segment_id") or t.get("sentence_id") or t.get("id")
        txt = (
            t.get("translated_text")
            or t.get("sentence_translated_text")
            or t.get("translation")
            or t.get("text")
        )
        if sid is not None and isinstance(txt, str):
            target_by_id[str(sid)] = txt
    return target_by_id


def _translate_segments(
    *,
    full_text: str,
    segments: list[TranscriptSegment],
    src_lang: str | None,
    target_lang: str,
) -> dict[str, str]:
    system_template = """\
You are a professional audiovisual translator for timed dubbing.

Source language: {src_lang}
Target language: {target_lang}

The user message is JSON with:
- "text": full transcript
- "segments": list of {segment_id, source_text, duration_ms}
- "src_lang": source language code (from ASR)
- "target_lang": target language code

Translate each segment from the source language into the target language for timed dubbing. Use duration_ms as timing context for each segment.

Respond with ONLY valid JSON (no markdown), shape:
{"translated_sentences":[{"segment_id":"0001","translated_text":"..."}, ...]}

Include every segment_id from the input, exactly once.
"""
    src_label = (src_lang or "").strip() or "unknown"
    system = system_template.replace("{target_lang}", target_lang).replace(
        "{src_lang}", src_label
    )

    built: list[dict[str, Any]] = []
    for seg in segments:
        built.append(
            {
                "segment_id": seg.segment_id,
                "source_text": seg.source_text,
                "duration_ms": seg.duration_ms,
            }
        )
    if not built:
        raise RuntimeError("No segments to translate")

    payload: dict[str, Any] = {
        "text": full_text,
        "segments": built,
        "target_lang": target_lang,
    }
    if src_lang:
        payload["src_lang"] = src_lang
    user_content = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    provider = get_llm_provider()
    result = provider.complete(
        LlmRequest(
            messages=[
                LlmMessage(role="system", content=system),
                LlmMessage(role="user", content=user_content),
            ]
        )
    )
    content = result.content
    if not content.strip():
        raise RuntimeError(
            f"LLM returned empty content (finish_reason={result.finish_reason})"
        )
    obj = _extract_json_object(content)
    target_by_id = _targets_from_response(obj)

    expected_ids = {seg.segment_id for seg in segments}
    if set(target_by_id.keys()) != expected_ids:
        missing = sorted(expected_ids - set(target_by_id.keys()))
        extra = sorted(set(target_by_id.keys()) - expected_ids)
        raise RuntimeError(
            f"Translation id mismatch. missing={missing[:20]!r} extra={extra[:10]!r}"
        )
    return target_by_id


def translate_transcript(ctx: PipelineContext) -> None:
    target_lang = ctx.state.config.target_lang
    if not target_lang:
        raise RuntimeError("target_lang is required")

    segments = ctx.state.transcript.segments
    if not segments:
        raise RuntimeError("No transcript segments to translate")

    translations = _translate_segments(
        full_text=ctx.state.transcript.full_text,
        segments=segments,
        src_lang=ctx.state.config.src_lang,
        target_lang=target_lang,
    )
    for seg in segments:
        seg.translated_text = translations[seg.segment_id]
    ctx.save()
