from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from schemas.task import TaskState
from storage.task_state_store import TaskStateStore


@dataclass
class PipelineContext:
    workspace: Path
    store: TaskStateStore
    state: TaskState
    input_video: Path
    export_path: Path | None = None

    def save(self) -> None:
        self.store.save(self.state)

    def abs(self, rel_or_name: str) -> Path:
        p = Path(rel_or_name)
        if p.is_absolute():
            return p
        return self.workspace / p
