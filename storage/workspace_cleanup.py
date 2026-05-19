from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from constants.filenames import TASK_STATE_JSON
from schemas.task import TaskState


class WorkspaceCleanupError(RuntimeError):
    pass


def cleanup_workspace_after_success(workspace: Path, state: TaskState) -> None:
    workspace = workspace.resolve()
    task_state_path = workspace / TASK_STATE_JSON
    if not task_state_path.is_file():
        raise WorkspaceCleanupError(f"Missing task state file: {task_state_path}")

    entries = [p for p in workspace.iterdir() if p.name != TASK_STATE_JSON]
    original_task_state = task_state_path.read_text(encoding="utf-8")
    staged: list[tuple[Path, Path]] = []
    task_state_updated = False

    staging_dir = workspace.parent / f".{workspace.name}_cleanup_{uuid.uuid4().hex}"
    staging_dir.mkdir(parents=True, exist_ok=False)

    try:
        for src in entries:
            dest = staging_dir / src.name
            shutil.move(str(src), str(dest))
            staged.append((src, dest))

        task_state_path.write_text(
            state.model_dump_json(indent=2, exclude_none=False) + "\n",
            encoding="utf-8",
        )
        task_state_updated = True
        shutil.rmtree(staging_dir)
    except Exception as exc:
        if task_state_updated:
            task_state_path.write_text(original_task_state, encoding="utf-8")

        for original_path, staged_path in reversed(staged):
            if staged_path.exists() and not original_path.exists():
                shutil.move(str(staged_path), str(original_path))

        try:
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
        except Exception:
            pass

        raise WorkspaceCleanupError(
            f"Failed to cleanup workspace after success: {workspace}"
        ) from exc
