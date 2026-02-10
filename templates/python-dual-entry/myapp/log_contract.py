"""Structured event logging contract (SSOT) for template observability."""

from __future__ import annotations

from enum import Enum
from typing import Any


EVENT_LOGGER_NAME = "myapp.events"


class EventName(str, Enum):
    RUN_START = "run_start"
    PHASE_TRANSITION = "phase_transition"
    ITEM_TERMINAL = "item_terminal"
    FAILURE_EVENT = "failure_event"
    RUN_END = "run_end"


class Phase(str, Enum):
    INIT = "INIT"
    VALIDATED = "VALIDATED"
    COMMIT_READY = "COMMIT_READY"
    COMMITTING = "COMMITTING"
    CLEANING = "CLEANING"
    DONE = "DONE"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    FAILED_COMMIT = "FAILED_COMMIT"
    FAILED_CLEANUP = "FAILED_CLEANUP"


class RunResultKind(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"


class ItemOutcome(str, Enum):
    EXECUTED = "EXECUTED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class ReasonCode(str, Enum):
    COMPLETED = "COMPLETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    UNKNOWN_WORKFLOW = "UNKNOWN_WORKFLOW"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    OS_ERROR = "OS_ERROR"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    OUTPUT_NOT_CREATED = "OUTPUT_NOT_CREATED"
    CANCELLED = "CANCELLED"
    UNEXPECTED_EXCEPTION = "UNEXPECTED_EXCEPTION"
    FAILED_CLEANUP = "FAILED_CLEANUP"


_REQUIRED_FIELDS_BY_EVENT: dict[EventName, set[str]] = {
    EventName.RUN_START: {"ts", "event", "run_id", "app", "version", "mode", "inputs", "outputs", "config"},
    EventName.PHASE_TRANSITION: {"ts", "event", "run_id", "phase", "phase_seq"},
    EventName.ITEM_TERMINAL: {
        "ts",
        "event",
        "run_id",
        "phase",
        "item_id",
        "outcome",
        "final_phase",
        "reason_code",
        "reason_detail",
        "evidence",
        "write_effects",
        "duration_ms",
    },
    EventName.FAILURE_EVENT: {
        "ts",
        "event",
        "run_id",
        "phase",
        "reason_code",
        "reason_detail",
        "error",
    },
    EventName.RUN_END: {
        "ts",
        "event",
        "run_id",
        "app",
        "version",
        "mode",
        "result",
        "summary",
        "timings_ms",
        "errors",
    },
}


def validate_event_payload(payload: dict[str, Any]) -> None:
    """Fail fast when an event payload violates the contract."""
    raw_event = payload.get("event")
    try:
        event_name = EventName(str(raw_event))
    except ValueError as exc:
        raise ValueError(f"Unknown event name: {raw_event!r}") from exc

    missing = sorted(_REQUIRED_FIELDS_BY_EVENT[event_name].difference(payload.keys()))
    if missing:
        raise ValueError(f"Event '{event_name.value}' missing required fields: {missing}")

    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")

    if "phase" in payload:
        _validate_enum_value(Phase, payload["phase"], field="phase")
    if "final_phase" in payload:
        _validate_enum_value(Phase, payload["final_phase"], field="final_phase")
    if "result" in payload:
        _validate_enum_value(RunResultKind, payload["result"], field="result")
    if "outcome" in payload:
        _validate_enum_value(ItemOutcome, payload["outcome"], field="outcome")
    if "reason_code" in payload:
        _validate_enum_value(ReasonCode, payload["reason_code"], field="reason_code")


def _validate_enum_value(enum_cls: type[Enum], raw_value: Any, *, field: str) -> None:
    try:
        enum_cls(str(raw_value))
    except ValueError as exc:
        allowed = [item.value for item in enum_cls]
        raise ValueError(f"Invalid {field}: {raw_value!r}. Allowed values: {allowed}") from exc
