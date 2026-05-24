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
    VALID_NOOP = "VALID_NOOP"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    UNKNOWN_ITEM_UNIVERSE = "UNKNOWN_ITEM_UNIVERSE"
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
    if event_name == EventName.RUN_END:
        _validate_run_end_summary(payload.get("summary"), result=RunResultKind(str(payload["result"])))


def _validate_enum_value(enum_cls: type[Enum], raw_value: Any, *, field: str) -> None:
    try:
        enum_cls(str(raw_value))
    except ValueError as exc:
        allowed = [item.value for item in enum_cls]
        raise ValueError(f"Invalid {field}: {raw_value!r}. Allowed values: {allowed}") from exc


def _validate_run_end_summary(summary: Any, *, result: RunResultKind) -> None:
    if not isinstance(summary, dict):
        raise ValueError("summary must be an object")

    by_outcome = _validate_count_group(
        summary.get("by_outcome"),
        keys={"executed", "skipped", "failed"},
        field="summary.by_outcome",
    )
    failed_by_phase = _validate_count_group(
        summary.get("failed_by_phase"),
        keys={"validation", "commit", "cleanup"},
        field="summary.failed_by_phase",
    )
    work_counts = summary.get("work_counts")
    if not isinstance(work_counts, dict):
        raise ValueError("summary.work_counts must be an object")

    required = {"planned", "eligible", "executed", "skipped", "failed"}
    missing = sorted(required.difference(work_counts.keys()))
    if missing:
        raise ValueError(f"summary.work_counts missing required fields: {missing}")

    for key in sorted(required):
        value = work_counts[key]
        if type(value) is not int or value < 0:
            raise ValueError(f"summary.work_counts.{key} must be a non-negative integer")

    planned = work_counts["planned"]
    eligible = work_counts["eligible"]
    if eligible > planned:
        raise ValueError("summary.work_counts.eligible must be less than or equal to planned")
    if work_counts["executed"] > eligible:
        raise ValueError("summary.work_counts.executed must be less than or equal to eligible")

    terminalized = work_counts["executed"] + work_counts["skipped"] + work_counts["failed"]
    if planned != terminalized:
        raise ValueError("summary.work_counts must reconcile: planned == executed + skipped + failed")

    for key in ("executed", "skipped", "failed"):
        if by_outcome[key] != work_counts[key]:
            raise ValueError(f"summary.by_outcome.{key} must match summary.work_counts.{key}")

    if result == RunResultKind.SUCCESS and (work_counts["failed"] or work_counts["skipped"]):
        raise ValueError("SUCCESS run_end cannot include skipped or failed work")
    if result == RunResultKind.SUCCESS and work_counts["executed"] == 0:
        raise ValueError("SUCCESS run_end must include executed work")
    if result == RunResultKind.SUCCESS and sum(failed_by_phase.values()) != 0:
        raise ValueError("SUCCESS run_end cannot include failed phase counts")
    if result == RunResultKind.FAILURE and work_counts["failed"] == 0:
        raise ValueError("FAILURE run_end must include failed work")
    if result == RunResultKind.FAILURE and sum(failed_by_phase.values()) == 0:
        raise ValueError("FAILURE run_end must include failed phase counts")
    if result == RunResultKind.PARTIAL_SUCCESS and not (work_counts["skipped"] or work_counts["failed"]):
        raise ValueError("PARTIAL_SUCCESS run_end must include skipped or failed work")


def _validate_count_group(raw_group: Any, *, keys: set[str], field: str) -> dict[str, int]:
    if not isinstance(raw_group, dict):
        raise ValueError(f"{field} must be an object")

    missing = sorted(keys.difference(raw_group.keys()))
    if missing:
        raise ValueError(f"{field} missing required fields: {missing}")

    result: dict[str, int] = {}
    for key in sorted(keys):
        value = raw_group[key]
        if type(value) is not int or value < 0:
            raise ValueError(f"{field}.{key} must be a non-negative integer")
        result[key] = value
    return result
