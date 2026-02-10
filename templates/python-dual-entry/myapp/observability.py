"""Structured observability emitters for workflow lifecycle events."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from myapp.log_contract import (
    EVENT_LOGGER_NAME,
    EventName,
    ItemOutcome,
    Phase,
    ReasonCode,
    RunResultKind,
    validate_event_payload,
)
from myapp.log_redaction import describe_path, sanitize_for_logging
from myapp.logging_config import ensure_event_logger_configured, get_event_log_path


logger = logging.getLogger(EVENT_LOGGER_NAME)


@dataclass(frozen=True)
class RunContext:
    run_id: str
    app: str
    version: str
    mode: str
    started_at_monotonic: float
    event_log_path: Path


def begin_run_context(*, app: str, version: str, mode: str) -> RunContext:
    ensure_event_logger_configured()
    run_id = uuid4().hex
    return RunContext(
        run_id=run_id,
        app=app,
        version=version,
        mode=mode,
        started_at_monotonic=time.perf_counter(),
        event_log_path=get_event_log_path(run_id),
    )


def emit_run_start(
    run: RunContext,
    *,
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    config_snapshot: dict[str, Any],
) -> None:
    payload = {
        "ts": _ts_now(),
        "event": EventName.RUN_START.value,
        "run_id": run.run_id,
        "app": run.app,
        "version": run.version,
        "mode": run.mode,
        "inputs": sanitize_for_logging(inputs),
        "outputs": sanitize_for_logging(outputs),
        "config": sanitize_for_logging(config_snapshot),
        "event_log_path": str(run.event_log_path),
    }
    _emit(payload, run=run, stacklevel=3)


def emit_phase_transition(run: RunContext, *, phase: Phase, phase_seq: int, notes: str | None = None) -> None:
    payload = {
        "ts": _ts_now(),
        "event": EventName.PHASE_TRANSITION.value,
        "run_id": run.run_id,
        "phase": phase.value,
        "phase_seq": phase_seq,
        "notes": notes or "",
    }
    _emit(payload, run=run, stacklevel=3)


def emit_failure(
    run: RunContext,
    *,
    phase: Phase,
    reason_code: ReasonCode,
    reason_detail: str,
    exc: BaseException | None = None,
) -> None:
    error_payload: dict[str, Any] = {}
    if exc is not None:
        error_payload = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        where = _exception_where(exc)
        if where is not None:
            error_payload["where"] = where

    payload = {
        "ts": _ts_now(),
        "event": EventName.FAILURE_EVENT.value,
        "run_id": run.run_id,
        "phase": phase.value,
        "reason_code": reason_code.value,
        "reason_detail": reason_detail,
        "error": error_payload,
    }
    _emit(payload, run=run, stacklevel=3)


def emit_item_terminal(
    run: RunContext,
    *,
    phase: Phase,
    item_id: str,
    outcome: ItemOutcome,
    final_phase: Phase,
    reason_code: ReasonCode,
    reason_detail: str,
    evidence: dict[str, Any],
    write_effects: dict[str, Any],
    duration_ms: int,
) -> None:
    payload = {
        "ts": _ts_now(),
        "event": EventName.ITEM_TERMINAL.value,
        "run_id": run.run_id,
        "phase": phase.value,
        "item_id": item_id,
        "outcome": outcome.value,
        "final_phase": final_phase.value,
        "reason_code": reason_code.value,
        "reason_detail": reason_detail,
        "evidence": sanitize_for_logging(evidence),
        "write_effects": sanitize_for_logging(write_effects),
        "duration_ms": duration_ms,
    }
    _emit(payload, run=run, stacklevel=3)


def emit_run_end(
    run: RunContext,
    *,
    result: RunResultKind,
    summary: dict[str, Any],
    timings_ms: dict[str, Any],
    errors: list[dict[str, Any]],
    resources: dict[str, Any] | None = None,
) -> None:
    payload = {
        "ts": _ts_now(),
        "event": EventName.RUN_END.value,
        "run_id": run.run_id,
        "app": run.app,
        "version": run.version,
        "mode": run.mode,
        "result": result.value,
        "summary": sanitize_for_logging(summary),
        "timings_ms": sanitize_for_logging(timings_ms),
        "errors": sanitize_for_logging(errors),
    }
    if resources is not None:
        payload["resources"] = sanitize_for_logging(resources)
    _emit(payload, run=run, stacklevel=3)


def build_io_snapshot(*, input_path: Path, output_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"input_path": describe_path(input_path)},
        {"output_path": describe_path(output_path)},
    )


def _emit(payload: dict[str, Any], *, run: RunContext, stacklevel: int) -> None:
    validate_event_payload(payload)
    logger.info(
        "event=%s",
        payload["event"],
        extra={
            "event_payload": payload,
            "event_log_path": str(run.event_log_path),
        },
        stacklevel=stacklevel,
    )


def _ts_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def _exception_where(exc: BaseException) -> str | None:
    tb = exc.__traceback__
    if tb is None:
        return None
    while tb.tb_next is not None:
        tb = tb.tb_next
    filename = tb.tb_frame.f_code.co_filename
    function = tb.tb_frame.f_code.co_name
    line = tb.tb_lineno
    return f"{filename}:{line}::{function}"
