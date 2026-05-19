from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


LlmRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LlmMessage:
    role: LlmRole
    content: str


@dataclass(frozen=True)
class LlmRequest:
    messages: list[LlmMessage]


@dataclass(frozen=True)
class LlmResult:
    content: str
    finish_reason: str | None = None
    raw_response: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LlmProvider(Protocol):
    def complete(self, request: LlmRequest) -> LlmResult:
        ...

