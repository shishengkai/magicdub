from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from config.settings import fal_trace_headers, require_env
from media.resources import MediaRequirement
from providers.asr.base import AsrRequest, AsrResult, TranscriptChunk


def _asr_max_wait_seconds() -> int:
    raw = os.getenv("FAL_ASR_MAX_WAIT_SECONDS", "3600").strip()
    return max(60, int(raw))


def _model_id_from_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip().rstrip("/")
    if "fal.run/" in endpoint:
        return endpoint.split("fal.run/")[-1].split("?")[0].strip("/")
    if "fal.ai/models/" in endpoint:
        rest = endpoint.split("fal.ai/models/")[-1].split("/api")[0]
        return rest.strip("/")
    return endpoint


def _call_fal_queue(
    model_id: str,
    input_payload: dict[str, Any],
    *,
    max_wait_s: int,
    timeout_s: int = 300,
) -> dict[str, Any]:
    fal_key = require_env("FAL_KEY")
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
        **fal_trace_headers(),
    }
    submit = requests.post(
        f"https://queue.fal.run/{model_id}",
        headers=headers,
        data=json.dumps(input_payload),
        timeout=timeout_s,
    )
    submit.raise_for_status()
    submit_data = submit.json()
    status_url = submit_data.get("status_url")
    response_url = submit_data.get("response_url")
    request_id = submit_data.get("request_id")
    if not status_url or not response_url:
        raise RuntimeError(f"Unexpected fal submit response for {model_id}: {submit_data}")

    deadline = time.time() + max_wait_s
    last_status = None
    auth_headers = {"Authorization": f"Key {fal_key}", **fal_trace_headers()}
    while True:
        if time.time() > deadline:
            raise TimeoutError(
                f"fal request timed out: model={model_id} request_id={request_id} last={last_status}"
            )
        st = requests.get(status_url, headers=auth_headers, timeout=timeout_s)
        st.raise_for_status()
        st_data = st.json()
        last_status = st_data
        status = st_data.get("status")
        if status == "COMPLETED":
            break
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(
                f"fal request failed: model={model_id} request_id={request_id} status={st_data}"
            )
        time.sleep(2)

    res = requests.get(response_url, headers=auth_headers, timeout=timeout_s)
    if res.status_code >= 400:
        snippet = (res.text or "")[:4000]
        raise RuntimeError(
            f"fal response fetch failed: model={model_id} request_id={request_id} "
            f"status_code={res.status_code}\n{snippet}"
        )
    res_data = res.json()
    if isinstance(res_data, dict) and "data" in res_data:
        data = res_data["data"]
        if not isinstance(data, dict):
            raise RuntimeError(
                f"Unexpected fal response data type for {model_id}: {type(data).__name__}"
            )
        return data
    if not isinstance(res_data, dict):
        raise RuntimeError(
            f"Unexpected fal response type for {model_id}: {type(res_data).__name__}"
        )
    return res_data


def _parse_languages(result: dict[str, Any]) -> list[str]:
    raw = result.get("languages")
    if not isinstance(raw, list):
        return []
    languages: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            languages.append(item.strip().lower())
    return languages


def _parse_chunks(result: dict[str, Any]) -> list[TranscriptChunk]:
    chunks = result.get("chunks")
    if not isinstance(chunks, list):
        return []

    parsed: list[TranscriptChunk] = []
    for ch in chunks:
        if not isinstance(ch, dict):
            continue
        ts = ch.get("timestamp")
        if not isinstance(ts, (list, tuple)) or len(ts) < 2:
            continue
        start_ms = int(round(float(ts[0]) * 1000))
        end_ms = int(round(float(ts[1]) * 1000))
        text = (ch.get("text") or "").strip()
        parsed.append(TranscriptChunk(start_ms=start_ms, end_ms=end_ms, text=text))
    return parsed


class FalWizperProvider:
    def audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="public_url")

    def transcribe(self, request: AsrRequest) -> AsrResult:
        if request.audio.kind != "url":
            raise RuntimeError("fal-wizper requires audio prepared as URL")

        endpoint = os.getenv("FAL_ASR_ENDPOINT", "https://fal.ai/models/fal-ai/wizper").strip()
        model_id = _model_id_from_endpoint(endpoint)
        language = request.src_lang if request.src_lang else None

        result = _call_fal_queue(
            model_id,
            {
                "audio_url": request.audio.value,
                "task": "transcribe",
                "language": language,
                "chunk_level": "segment",
                "max_segment_len": 20,
                "merge_chunks": False,
                "version": "3",
            },
            max_wait_s=_asr_max_wait_seconds(),
        )
        return AsrResult(
            full_text=(result.get("text") or "").strip(),
            chunks=_parse_chunks(result),
            languages=_parse_languages(result),
            raw_response=result,
        )


Provider = FalWizperProvider
