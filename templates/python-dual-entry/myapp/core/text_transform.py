"""Text transformation workflow (core business logic, SSOT)."""

from __future__ import annotations

import logging
import os
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myapp.config_keys import STEP_KEY_MS, STEP_KEY_NEW, STEP_KEY_OLD, STEP_KEY_OP, STEP_KEY_VALUE
from myapp.constants import DEFAULT_ENCODING


logger = logging.getLogger(__name__)

OP_STRIP = "strip"
OP_UPPERCASE = "uppercase"
OP_LOWERCASE = "lowercase"
OP_PREFIX = "prefix"
OP_SUFFIX = "suffix"
OP_REPLACE = "replace"
OP_FILTER_CONTAINS = "filter_contains"
OP_SLEEP_MS = "sleep_ms"

SUPPORTED_OPS = frozenset(
    {
        OP_STRIP,
        OP_UPPERCASE,
        OP_LOWERCASE,
        OP_PREFIX,
        OP_SUFFIX,
        OP_REPLACE,
        OP_FILTER_CONTAINS,
        OP_SLEEP_MS,
    }
)


@dataclass(frozen=True)
class ProcessResult:
    success: bool
    lines_processed: int = 0
    cancelled: bool = False
    error: str | None = None


class _StepCancelled(Exception):
    """Internal signal to abort workflow work promptly when cancellation is requested."""


def process_text_file(
    *,
    input_path: Path,
    output_path: Path,
    steps: list[dict[str, Any]],
    is_cancelled: Callable[[], bool],
) -> ProcessResult:
    logger.info("Processing text file: %s -> %s", input_path, output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path: Path | None = None
    lines_processed = 0

    try:
        with input_path.open("r", encoding=DEFAULT_ENCODING, newline="") as in_f:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding=DEFAULT_ENCODING,
                newline="\n",
                delete=False,
                dir=str(output_path.parent),
                prefix=f".tmp_{output_path.stem}_",
                suffix=output_path.suffix or ".txt",
            ) as tmp_f:
                tmp_path = Path(tmp_f.name)

                for raw_line in in_f:
                    if is_cancelled():
                        logger.warning("Cancellation requested; stopping early")
                        return ProcessResult(success=False, cancelled=True, lines_processed=lines_processed)

                    line = raw_line.rstrip("\r\n")
                    try:
                        transformed = _apply_steps(line, steps, is_cancelled=is_cancelled)
                    except _StepCancelled:
                        logger.warning("Cancellation requested during step execution; stopping early")
                        return ProcessResult(success=False, cancelled=True, lines_processed=lines_processed)
                    if transformed is None:
                        continue

                    tmp_f.write(transformed)
                    tmp_f.write("\n")
                    lines_processed += 1

        if tmp_path is None:
            return ProcessResult(success=False, error="Internal error: temporary output missing")

        os.replace(tmp_path, output_path)
        tmp_path = None

        return ProcessResult(success=True, lines_processed=lines_processed)
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError as exc:
                logger.warning("Failed to clean up temp file %s: %s", tmp_path, exc)


def _apply_steps(line: str, steps: list[dict[str, Any]], *, is_cancelled: Callable[[], bool]) -> str | None:
    current: str | None = line

    for step in steps:
        if is_cancelled():
            raise _StepCancelled

        op = step.get(STEP_KEY_OP)
        if op == OP_STRIP:
            current = current.strip() if current is not None else None
        elif op == OP_UPPERCASE:
            current = current.upper() if current is not None else None
        elif op == OP_LOWERCASE:
            current = current.lower() if current is not None else None
        elif op == OP_PREFIX:
            value = step.get(STEP_KEY_VALUE, "")
            current = f"{value}{current}" if current is not None else None
        elif op == OP_SUFFIX:
            value = step.get(STEP_KEY_VALUE, "")
            current = f"{current}{value}" if current is not None else None
        elif op == OP_REPLACE:
            old = step.get(STEP_KEY_OLD, "")
            new = step.get(STEP_KEY_NEW, "")
            current = current.replace(old, new) if current is not None else None
        elif op == OP_FILTER_CONTAINS:
            value = step.get(STEP_KEY_VALUE, "")
            if current is not None and value not in current:
                return None
        elif op == OP_SLEEP_MS:
            ms = step.get(STEP_KEY_MS, 0)
            if _sleep_ms_interruptibly(float(ms), is_cancelled=is_cancelled):
                raise _StepCancelled
        else:
            raise ValueError(f"Unknown operation: {op!r}")

    return current


def _sleep_ms_interruptibly(ms: float, *, is_cancelled: Callable[[], bool]) -> bool:
    remaining = max(ms, 0.0) / 1000.0
    while remaining > 0:
        if is_cancelled():
            return True
        chunk = min(remaining, 0.05)
        time.sleep(chunk)
        remaining -= chunk
    return is_cancelled()
