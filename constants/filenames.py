from __future__ import annotations

from media.audio_format import pipeline_audio_ext

TASK_STATE_JSON = "task_state.json"
OUTPUT_VIDEO_MP4 = "output_video.mp4"
MIX_SAMPLE_RATE = 48000
ORIGINAL_VOCAL_BED_DB = "-100dB"

VOCAL_TRACK_RAW_STEM = "vocal_track_raw"


def pipeline_audio(stem: str) -> str:
    """Filename for audio produced by the local pipeline (extension from MAGICDUB_PIPELINE_AUDIO_EXT)."""
    return f"{stem}{pipeline_audio_ext()}"


def external_audio(stem: str, extension: str) -> str:
    """Filename for audio materialized from a provider (extension from URL/MIME)."""
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"{stem}{ext}"


def source_audio_name() -> str:
    return pipeline_audio("source_audio")


def vocal_track_name() -> str:
    return pipeline_audio("vocal_track")


def instrumental_track_name() -> str:
    return pipeline_audio("instrumental_track")


def source_video_name(extension: str) -> str:
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"source_video{ext}"


def segment_audio_name(segment_id: str) -> str:
    return pipeline_audio(f"segment_{segment_id}")


def aligned_segment_audio_name(segment_id: str) -> str:
    return pipeline_audio(f"aligned_segment_{segment_id}")


def dubbed_segment_stem(segment_id: str) -> str:
    return f"dubbed_segment_{segment_id}"


def source_segment_stem(segment_id: str) -> str:
    return f"source_segment_{segment_id}"
