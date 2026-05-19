from __future__ import annotations

from pathlib import Path

from media.audio_format import ffmpeg_audio_output_args
from media.ffmpeg import audio_duration_ms, run_ffmpeg


def extract_source_audio(video_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ar",
            "16000",
            "-ac",
            "1",
            *ffmpeg_audio_output_args(output_path),
            str(output_path),
        ]
    )


def resample_like_reference(vocals_in: Path, mix_ref: Path, output_path: Path) -> None:
    from media.ffmpeg import audio_stream_info

    sr, ch, _ = audio_stream_info(mix_ref)
    run_ffmpeg(
        [
            "-y",
            "-i",
            str(vocals_in),
            "-ac",
            str(ch),
            "-ar",
            str(sr),
            *ffmpeg_audio_output_args(output_path),
            str(output_path),
        ]
    )


def atempo_chain(ratio: float) -> str:
    factors: list[float] = []
    x = ratio
    eps = 1e-9
    while x > 4.0:
        factors.append(4.0)
        x /= 4.0
    while x < 0.5 - eps:
        factors.append(0.5)
        x /= 0.5
    factors.append(x)
    return ",".join(f"atempo={f:.6f}" for f in factors)


def align_audio_duration(input_path: Path, output_path: Path, target_ms: float) -> None:
    input_ms = audio_duration_ms(input_path)
    if target_ms <= 0:
        raise RuntimeError(f"Invalid target duration: {target_ms}")
    ratio = input_ms / target_ms
    filt = atempo_chain(ratio)
    run_ffmpeg(
        [
            "-y",
            "-i",
            str(input_path),
            "-filter:a",
            filt,
            *ffmpeg_audio_output_args(output_path),
            str(output_path),
        ]
    )


def cut_segment(vocal_track: Path, output_path: Path, start_ms: int, end_ms: int) -> None:
    start_s = start_ms / 1000.0
    end_s = end_ms / 1000.0
    if end_s <= start_s:
        raise RuntimeError(f"Invalid segment range: {start_ms}-{end_ms}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "-y",
            "-i",
            str(vocal_track),
            "-ss",
            f"{start_s:.6f}",
            "-to",
            f"{end_s:.6f}",
            *ffmpeg_audio_output_args(output_path),
            str(output_path),
        ]
    )


def wav_duration_ms(path: Path) -> float:
    return audio_duration_ms(path)
