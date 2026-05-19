from __future__ import annotations

import random
import string
from datetime import datetime
from pathlib import Path

from config.settings import TASKS_DIR
from schemas.task import SourceVideoRef, TaskConfig, TaskState
from pipeline.context import PipelineContext
from storage.task_state_store import TaskStateStore
from utils.time import local_iso_timestamp


def new_task_id() -> str:
    ts = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    suf = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{ts}_{suf}"


def initialize_task(
    *,
    input_video: Path,
    target_lang: str,
    src_lang: str | None,
) -> PipelineContext:
    input_video = input_video.expanduser().resolve()
    if not input_video.is_file():
        raise FileNotFoundError(f"Input video not found: {input_video}")

    task_id = new_task_id()
    workspace = (TASKS_DIR / task_id).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    ext = input_video.suffix or ".mp4"
    state = TaskState(
        task_id=task_id,
        status="running",
        started_at=local_iso_timestamp(),
        input_path=str(input_video),
        source_video=SourceVideoRef(
            filename=input_video.name,
            extension=ext,
        ),
        config=TaskConfig(
            target_lang=target_lang,
            src_lang=src_lang,
        ),
    )
    store = TaskStateStore(workspace)
    store.save(state)

    return PipelineContext(
        workspace=workspace,
        store=store,
        state=state,
        input_video=input_video,
    )
