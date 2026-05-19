from __future__ import annotations


def log_stage(index: int, total: int, message: str) -> None:
    print(f"[{index}/{total}] {message}", flush=True)
