from __future__ import annotations

import json
import subprocess
from pathlib import Path

FFMPEG_QUIET = ["-hide_banner", "-nostats", "-loglevel", "error"]
FFPROBE_QUIET = ["-hide_banner", "-loglevel", "error"]


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", *FFMPEG_QUIET, *args], check=True)


def run_ffprobe_json(path: Path) -> dict:
    r = subprocess.run(
        [
            "ffprobe",
            *FFPROBE_QUIET,
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate,channels:format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(r.stdout)


def audio_stream_info(path: Path) -> tuple[int, int, float]:
    meta = run_ffprobe_json(path)
    streams = meta.get("streams") or []
    if not streams:
        raise RuntimeError(f"No audio stream in {path}")
    st0 = streams[0]
    sr = int(st0.get("sample_rate") or 0)
    ch = int(st0.get("channels") or 0)
    dur_s = float((meta.get("format") or {}).get("duration") or 0.0)
    if sr <= 0 or ch <= 0:
        raise RuntimeError(f"Invalid audio probe for {path}: sr={sr} ch={ch}")
    return sr, ch, dur_s


def duration_seconds(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe",
            *FFPROBE_QUIET,
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(r.stdout.strip())


def audio_duration_ms(path: Path) -> float:
    return duration_seconds(path) * 1000.0


def wav_duration_ms(path: Path) -> float:
    return audio_duration_ms(path)
