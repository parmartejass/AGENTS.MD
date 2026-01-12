"""Configuration models (SSOT) shared across GUI/CLI/tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class RunStatus(str, Enum):
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class JobConfig:
    workflow_id: str
    input_path: Path
    output_path: Path
    workflow: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.input_path = Path(self.input_path)
        self.output_path = Path(self.output_path)


@dataclass
class JobResult:
    success: bool
    status: RunStatus
    output_path: Path | None = None
    lines_processed: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return 0 if self.success else 1

