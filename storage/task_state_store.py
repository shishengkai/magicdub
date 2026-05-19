from __future__ import annotations

import json
from pathlib import Path

from constants.filenames import TASK_STATE_JSON
from schemas.task import TaskState


class TaskStateStore:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        self.path = self.workspace / TASK_STATE_JSON

    def load(self) -> TaskState:
        if not self.path.is_file():
            raise FileNotFoundError(f"Missing task state: {self.path}")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return TaskState.model_validate(data)

    def save(self, state: TaskState) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            state.model_dump_json(indent=2, exclude_none=False) + "\n",
            encoding="utf-8",
        )

    def rel_path(self, absolute: Path) -> str:
        resolved = absolute.resolve()
        try:
            return str(resolved.relative_to(self.workspace))
        except ValueError:
            return str(resolved)
