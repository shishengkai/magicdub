from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from config.settings import require_env
from pathlib import Path
from urllib.parse import urlparse

from media.resources import MediaRequirement, PreparedMedia, guess_mime_type
from providers.tts.base import TtsRequest, TtsResult


def _fal_trace_headers() -> dict[str, str]:
    return {"x-my-trace-id": os.getenv("FAL_MY_TRACE_ID", "MagicDub").strip() or "MagicDub"}


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
    max_wait_s: int = 900,
    timeout_s: int = 300,
) -> dict[str, Any]:
    fal_key = require_env("FAL_KEY")
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
        **_fal_trace_headers(),
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
    auth_headers = {"Authorization": f"Key {fal_key}", **_fal_trace_headers()}
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


def _pick_tts_audio_url(out: dict[str, Any]) -> str | None:
    audio = out.get("audio")
    if isinstance(audio, dict) and audio.get("url"):
        return str(audio["url"])
    output = out.get("output")
    if isinstance(output, dict) and output.get("url"):
        return str(output["url"])
    audio_url = out.get("audio_url")
    if isinstance(audio_url, str) and audio_url.startswith("http"):
        return audio_url
    url = out.get("url")
    if isinstance(url, str) and url.startswith("http"):
        return url
    return None


class FalIndexTts2Provider:
    def reference_audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="public_url")

    def synthesize(self, request: TtsRequest) -> TtsResult:
        if request.reference_audio is None:
            raise RuntimeError("fal-index-tts-2 requires reference_audio")
        if request.reference_audio.kind != "url":
            raise RuntimeError("fal-index-tts-2 requires reference audio prepared as URL")

        endpoint = os.getenv(
            "FAL_TTS_ENDPOINT",
            "https://fal.ai/models/fal-ai/index-tts-2/text-to-speech",
        ).strip()
        model_id = _model_id_from_endpoint(endpoint)
        result = _call_fal_queue(
            model_id,
            {
                "audio_url": request.reference_audio.value,
                "prompt": request.text,
                "emotional_audio_url": request.reference_audio.value,
            },
        )
        url = _pick_tts_audio_url(result)
        if not url:
            raise RuntimeError(f"TTS response has no audio URL: {result}")
        return TtsResult(
            audio=PreparedMedia(
                kind="url",
                value=url,
                mime_type=guess_mime_type(Path(urlparse(url).path)),
            ),
            raw_response=result,
        )


Provider = FalIndexTts2Provider
