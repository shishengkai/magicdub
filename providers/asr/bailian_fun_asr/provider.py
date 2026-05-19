from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from config.settings import require_env
from media.resources import MediaRequirement
from providers.asr.base import AsrRequest, AsrResult, TranscriptChunk

_MODEL = "fun-asr"
_SUBMIT_PATH = "/api/v1/services/audio/asr/transcription"


def _asr_max_wait_seconds() -> int:
    raw = os.getenv("DASHSCOPE_ASR_MAX_WAIT_SECONDS", "3600").strip()
    return max(60, int(raw))


def _base_url() -> str:
    explicit = os.getenv("DASHSCOPE_BASE_URL", "").strip().rstrip("/")
    if explicit:
        return explicit
    return "https://dashscope.aliyuncs.com"


def _submit_url() -> str:
    return f"{_base_url()}{_SUBMIT_PATH}"


def _task_url(task_id: str) -> str:
    return f"{_base_url()}/api/v1/tasks/{task_id}"


def _auth_headers() -> dict[str, str]:
    api_key = require_env("DASHSCOPE_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _submit_headers() -> dict[str, str]:
    return {**_auth_headers(), "X-DashScope-Async": "enable"}


def _language_hints(src_lang: str | None) -> list[str] | None:
    if not src_lang:
        return None
    code = src_lang.split(",")[0].strip().lower()
    return [code] if code else None


def _submit_task(file_url: str, *, src_lang: str | None, timeout_s: int = 300) -> str:
    parameters: dict[str, Any] = {"diarization_enabled": True}
    hints = _language_hints(src_lang)
    if hints:
        parameters["language_hints"] = hints

    payload = {
        "model": _MODEL,
        "input": {"file_urls": [file_url]},
        "parameters": parameters,
    }
    response = requests.post(
        _submit_url(),
        headers=_submit_headers(),
        data=json.dumps(payload),
        timeout=timeout_s,
    )
    if response.status_code >= 400:
        snippet = (response.text or "")[:4000]
        raise RuntimeError(
            f"DashScope ASR submit failed: status_code={response.status_code}\n{snippet}"
        )

    body = response.json()
    output = body.get("output")
    if not isinstance(output, dict):
        raise RuntimeError(f"Unexpected DashScope submit response: {body}")
    task_id = output.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise RuntimeError(f"DashScope submit response missing task_id: {body}")
    return task_id.strip()


def _wait_for_task(task_id: str, *, max_wait_s: int, timeout_s: int = 300) -> dict[str, Any]:
    deadline = time.time() + max_wait_s
    last_body: dict[str, Any] | None = None
    while True:
        if time.time() > deadline:
            raise TimeoutError(
                f"DashScope ASR task timed out: task_id={task_id} last={last_body}"
            )
        response = requests.post(
            _task_url(task_id),
            headers=_auth_headers(),
            timeout=timeout_s,
        )
        if response.status_code >= 400:
            snippet = (response.text or "")[:4000]
            raise RuntimeError(
                f"DashScope ASR query failed: task_id={task_id} "
                f"status_code={response.status_code}\n{snippet}"
            )

        body = response.json()
        if not isinstance(body, dict):
            raise RuntimeError(
                f"Unexpected DashScope query response type: {type(body).__name__}"
            )
        last_body = body
        output = body.get("output")
        if not isinstance(output, dict):
            raise RuntimeError(f"DashScope query response missing output: {body}")

        status = output.get("task_status")
        if status == "SUCCEEDED":
            return output
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"DashScope ASR task failed: task_id={task_id} output={output}")
        if status not in ("PENDING", "RUNNING", None):
            raise RuntimeError(
                f"DashScope ASR task ended unexpectedly: task_id={task_id} status={status}"
            )
        time.sleep(2)


def _fetch_transcription(transcription_url: str, *, timeout_s: int = 300) -> dict[str, Any]:
    response = requests.get(transcription_url, timeout=timeout_s)
    if response.status_code >= 400:
        snippet = (response.text or "")[:4000]
        raise RuntimeError(
            f"DashScope transcription download failed: status_code={response.status_code}\n"
            f"{snippet}"
        )
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError(
            f"Unexpected transcription JSON type: {type(data).__name__}"
        )
    return data


def _first_success_result(output: dict[str, Any]) -> dict[str, Any]:
    results = output.get("results")
    if not isinstance(results, list) or not results:
        raise RuntimeError(f"DashScope ASR output has no results: {output}")

    for item in results:
        if not isinstance(item, dict):
            continue
        if item.get("subtask_status") == "SUCCEEDED":
            return item

    failed = [item for item in results if isinstance(item, dict)]
    raise RuntimeError(f"DashScope ASR subtasks failed: {failed}")


def _parse_chunks(transcription: dict[str, Any]) -> list[TranscriptChunk]:
    transcripts = transcription.get("transcripts")
    if not isinstance(transcripts, list):
        return []

    chunks: list[TranscriptChunk] = []
    for track in transcripts:
        if not isinstance(track, dict):
            continue
        sentences = track.get("sentences")
        if not isinstance(sentences, list):
            continue
        for sentence in sentences:
            if not isinstance(sentence, dict):
                continue
            text = (sentence.get("text") or "").strip()
            if not text:
                continue
            begin = sentence.get("begin_time")
            end = sentence.get("end_time")
            if not isinstance(begin, (int, float)) or not isinstance(end, (int, float)):
                continue
            chunks.append(
                TranscriptChunk(
                    start_ms=int(begin),
                    end_ms=int(end),
                    text=text,
                )
            )
    chunks.sort(key=lambda ch: (ch.start_ms, ch.end_ms))
    return chunks


def _parse_full_text(transcription: dict[str, Any], chunks: list[TranscriptChunk]) -> str:
    transcripts = transcription.get("transcripts")
    if isinstance(transcripts, list):
        texts: list[str] = []
        for track in transcripts:
            if not isinstance(track, dict):
                continue
            text = (track.get("text") or "").strip()
            if text:
                texts.append(text)
        if texts:
            return "\n".join(texts)
    if chunks:
        return " ".join(ch.text for ch in chunks if ch.text)
    return ""


class BailianFunAsrProvider:
    def audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="public_url")

    def transcribe(self, request: AsrRequest) -> AsrResult:
        if request.audio.kind != "url":
            raise RuntimeError("bailian-fun-asr requires audio prepared as public URL")

        task_id = _submit_task(
            request.audio.value,
            src_lang=request.src_lang,
        )
        output = _wait_for_task(task_id, max_wait_s=_asr_max_wait_seconds())
        result_item = _first_success_result(output)
        transcription_url = result_item.get("transcription_url")
        if not isinstance(transcription_url, str) or not transcription_url.strip():
            raise RuntimeError(
                f"DashScope ASR result missing transcription_url: {result_item}"
            )

        transcription = _fetch_transcription(transcription_url.strip())
        chunks = _parse_chunks(transcription)
        return AsrResult(
            full_text=_parse_full_text(transcription, chunks),
            chunks=chunks,
            languages=[],
            raw_response={
                "task_id": task_id,
                "task_output": output,
                "transcription": transcription,
            },
        )


Provider = BailianFunAsrProvider
