from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

from config.settings import require_env
from urllib.parse import urlparse

from media.resources import MediaRequirement, PreparedMedia, guess_mime_type
from providers.vocal_separation.base import VocalSeparationRequest, VocalSeparationResult


def _fal_trace_headers() -> dict[str, str]:
    return {"x-my-trace-id": os.getenv("FAL_MY_TRACE_ID", "MagicDub").strip() or "MagicDub"}


def _resolve_demucs_endpoint() -> str:
    explicit = os.getenv("FAL_DEMUCS_ENDPOINT", "").strip()
    if explicit:
        return explicit
    legacy = os.getenv("FAL_SEPARATE_ENDPOINT", "").strip()
    if legacy and "demucs" in legacy.lower():
        return legacy
    return "https://fal.ai/models/fal-ai/demucs/api"


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


def _pick_vocals_url(out: dict[str, Any]) -> str | None:
    vocals = out.get("vocals")
    if isinstance(vocals, dict) and vocals.get("url"):
        return str(vocals["url"])
    if isinstance(vocals, str) and vocals.startswith("http"):
        return vocals
    vocals_url = out.get("vocals_url")
    if isinstance(vocals_url, str) and vocals_url.startswith("http"):
        return vocals_url
    if isinstance(vocals_url, dict) and vocals_url.get("url"):
        return str(vocals_url["url"])
    return None


class FalDemucsProvider:
    def audio_requirement(self) -> MediaRequirement:
        return MediaRequirement(kind="public_url")

    def separate_vocals(self, request: VocalSeparationRequest) -> VocalSeparationResult:
        if request.audio.kind != "url":
            raise RuntimeError("fal-demucs requires audio prepared as URL")

        endpoint = _resolve_demucs_endpoint()
        model_id = _model_id_from_endpoint(endpoint)
        demucs_model = os.getenv("FAL_DEMUCS_MODEL", "htdemucs_ft").strip() or "htdemucs_ft"
        shifts = max(1, int(os.getenv("FAL_DEMUCS_SHIFTS", "1").strip() or "1"))
        overlap = float(os.getenv("FAL_DEMUCS_OVERLAP", "0.25").strip() or "0.25")

        result = _call_fal_queue(
            model_id,
            {
                "audio_url": request.audio.value,
                "model": demucs_model,
                "stems": ["vocals"],
                "shifts": shifts,
                "overlap": overlap,
                "output_format": "wav",
            },
        )
        vocals_url = _pick_vocals_url(result)
        if not vocals_url:
            raise RuntimeError(f"Unexpected fal demucs response (need vocals url): {result}")
        return VocalSeparationResult(
            vocals=PreparedMedia(
                kind="url",
                value=vocals_url,
                mime_type=guess_mime_type(Path(urlparse(vocals_url).path)),
            ),
            raw_response=result,
        )


Provider = FalDemucsProvider
