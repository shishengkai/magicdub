from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from config.settings import instrumental_mix_volume
from constants.filenames import MIX_SAMPLE_RATE, ORIGINAL_VOCAL_BED_DB
from media.audio_format import ffmpeg_audio_output_args
from media.ffmpeg import FFMPEG_QUIET, audio_stream_info, duration_seconds
from schemas.task import TranscriptSegment


def subtract_instrumental(
    mix_path: Path,
    vocals_path: Path,
    instrumental_out: Path,
    *,
    vocal_gain: float,
) -> None:
    _, ch, d0 = audio_stream_info(mix_path)
    _, _, d1 = audio_stream_info(vocals_path)
    dmin = min(d0, d1)
    if dmin <= 0:
        raise RuntimeError(f"Invalid duration for subtract: mix={d0} vocals={d1}")
    d_use = max(0.01, dmin - 0.02)
    trim = f"atrim=start=0:duration={d_use:.6f}"
    vol = f",volume={vocal_gain}"
    if ch == 1:
        fc = (
            f"[0:a]{trim},aformat=sample_fmts=fltp:channel_layouts=mono[mx];"
            f"[1:a]{trim},aformat=sample_fmts=fltp:channel_layouts=mono{vol}[vc];"
            f"[mx][vc]amerge=inputs=2,pan=mono|c0=c0-c1,"
            f"alimiter=level_in=1:level_out=0.95:limit=0.95,"
            f"aformat=sample_fmts=s16:channel_layouts=mono[out]"
        )
    elif ch == 2:
        fc = (
            f"[0:a]{trim},aformat=sample_fmts=fltp:channel_layouts=stereo[mx];"
            f"[1:a]{trim},aformat=sample_fmts=fltp:channel_layouts=stereo{vol}[vc];"
            f"[mx][vc]amerge=inputs=2,"
            f"pan=stereo|c0=c0-c2|c1=c1-c3,"
            f"alimiter=level_in=1:level_out=0.95:limit=0.95,"
            f"aformat=sample_fmts=s16:channel_layouts=stereo[out]"
        )
    else:
        raise RuntimeError(f"Unsupported channel count for subtract: {ch}")

    subprocess.run(
        [
            "ffmpeg",
            *FFMPEG_QUIET,
            "-y",
            "-i",
            str(mix_path),
            "-i",
            str(vocals_path),
            "-filter_complex",
            fc,
            "-map",
            "[out]",
            *ffmpeg_audio_output_args(instrumental_out),
            str(instrumental_out),
        ],
        check=True,
    )


def _mono_chain(
    idx: int,
    label_out: str,
    extra: str = "",
    *,
    volume: Optional[str] = None,
) -> str:
    vol = f",volume={volume}" if volume is not None else ""
    return (
        f"[{idx}:a]aresample={MIX_SAMPLE_RATE},aformat=sample_fmts=fltp:channel_layouts=mono"
        f"{extra}{vol}{label_out}"
    )


def compose_output_video(
    *,
    video_path: Path,
    instrumental_path: Path,
    vocal_bed_path: Path,
    aligned_clips: list[tuple[TranscriptSegment, Path]],
    output_path: Path,
) -> None:
    vd = duration_seconds(video_path)
    rd = duration_seconds(instrumental_path)
    sd = duration_seconds(vocal_bed_path)
    segments = sorted(aligned_clips, key=lambda x: x[0].start_ms)

    inputs: list[str] = ["-i", str(video_path), "-i", str(instrumental_path), "-i", str(vocal_bed_path)]
    for _, clip in segments:
        inputs.extend(["-i", str(clip)])

    fc_parts: list[str] = []

    residual_extra = ""
    if vd > rd:
        pad_samples = max(0, int((vd - rd) * MIX_SAMPLE_RATE))
        if pad_samples > 0:
            residual_extra = f",apad=pad_len={pad_samples}"
    elif rd > vd:
        residual_extra = f",atrim=start=0:duration={vd:.6f}"

    speech_extra = ""
    if vd > sd:
        pad_samples_s = max(0, int((vd - sd) * MIX_SAMPLE_RATE))
        if pad_samples_s > 0:
            speech_extra = f",apad=pad_len={pad_samples_s}"
    elif sd > vd:
        speech_extra = f",atrim=start=0:duration={vd:.6f}"

    inst_vol = instrumental_mix_volume()

    if not segments:
        fc_parts.append(_mono_chain(1, "[nr]", residual_extra, volume=inst_vol))
        fc_parts.append(_mono_chain(2, "[ns]", speech_extra, volume=ORIGINAL_VOCAL_BED_DB))
        fc_parts.append("[nr][ns]amix=inputs=2:duration=longest:normalize=0[a_mix]")
        fc_parts.append("[a_mix]alimiter=limit=0.98:attack=2:release=50[aout]")
    else:
        fc_parts.append(_mono_chain(1, "[nr]", residual_extra, volume=inst_vol))
        fc_parts.append(_mono_chain(2, "[ns]", speech_extra, volume=ORIGINAL_VOCAL_BED_DB))
        for i, (seg, _) in enumerate(segments):
            stream_idx = 3 + i
            fc_parts.append(
                _mono_chain(stream_idx, f"[nt{i}]", f",adelay={seg.start_ms}|{seg.start_ms}")
            )
        tails = "".join(f"[nt{i}]" for i in range(len(segments)))
        n_mix = 2 + len(segments)
        fc_parts.append(f"[nr][ns]{tails}amix=inputs={n_mix}:duration=longest:normalize=0[a_mix]")
        fc_parts.append("[a_mix]alimiter=limit=0.98:attack=2:release=50[aout]")

    fc = ";".join(fc_parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            *FFMPEG_QUIET,
            "-y",
            *inputs,
            "-filter_complex",
            fc,
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-t",
            str(vd),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ],
        check=True,
    )
