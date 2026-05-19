from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class MediaRef(BaseModel):
    path: str = ""
    url: str = ""


class SourceVideoRef(BaseModel):
    path: str = ""
    filename: str = ""
    extension: str = ""


class InstrumentalTrackRef(BaseModel):
    path: str = ""


class OutputVideoRef(BaseModel):
    path: str = ""


class SegmentMediaRef(BaseModel):
    path: str = ""
    url: str = ""


class AlignedSegmentRef(BaseModel):
    path: str = ""


class TranscriptSegment(BaseModel):
    segment_id: str
    start_ms: int = 0
    end_ms: int = 0
    duration_ms: int = 0
    source_text: str = ""
    translated_text: str = ""
    source_segment: SegmentMediaRef = Field(default_factory=SegmentMediaRef)
    dubbed_segment: SegmentMediaRef = Field(default_factory=SegmentMediaRef)
    aligned_segment: AlignedSegmentRef = Field(default_factory=AlignedSegmentRef)


class Transcript(BaseModel):
    full_text: str = ""
    segments: list[TranscriptSegment] = Field(default_factory=list)


class TaskConfig(BaseModel):
    target_lang: str = ""
    src_lang: Optional[str] = None


TaskStatus = Literal["pending", "running", "completed", "failed"]


class TaskState(BaseModel):
    task_id: str
    status: TaskStatus = "pending"
    started_at: str = ""
    completed_at: str = ""
    input_path: str = ""
    output_path: str = ""
    source_video: SourceVideoRef = Field(default_factory=SourceVideoRef)
    source_audio: MediaRef = Field(default_factory=MediaRef)
    vocal_track: MediaRef = Field(default_factory=MediaRef)
    instrumental_track: InstrumentalTrackRef = Field(default_factory=InstrumentalTrackRef)
    transcript: Transcript = Field(default_factory=Transcript)
    output_video: OutputVideoRef = Field(default_factory=OutputVideoRef)
    config: TaskConfig = Field(default_factory=TaskConfig)
