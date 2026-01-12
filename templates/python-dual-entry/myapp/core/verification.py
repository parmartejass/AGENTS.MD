"""Output verification helpers (core SSOT) for tests and CLI."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from myapp.constants import DEFAULT_ENCODING


@dataclass(frozen=True)
class VerificationResult:
    matches: bool
    diff: str | None = None


def compare_text_files(*, expected_path: Path, actual_path: Path) -> VerificationResult:
    expected_lines = _read_lines(expected_path)
    actual_lines = _read_lines(actual_path)

    if expected_lines == actual_lines:
        return VerificationResult(matches=True, diff=None)

    diff_lines = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile=str(expected_path),
        tofile=str(actual_path),
        lineterm="",
    )
    diff_text = "\n".join(diff_lines)
    return VerificationResult(matches=False, diff=diff_text)


def _read_lines(path: Path) -> list[str]:
    text = Path(path).read_text(encoding=DEFAULT_ENCODING)
    return text.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)

