"""Validation logic (core SSOT)."""

from __future__ import annotations

from dataclasses import dataclass, field

from myapp.config import JobConfig
from myapp.config_keys import (
    STEP_KEY_MS,
    STEP_KEY_NEW,
    STEP_KEY_OLD,
    STEP_KEY_OP,
    STEP_KEY_VALUE,
    WORKFLOW_KEY_STEPS,
)
from myapp.core.text_transform import (
    OP_FILTER_CONTAINS,
    OP_PREFIX,
    OP_REPLACE,
    OP_SLEEP_MS,
    OP_SUFFIX,
    SUPPORTED_OPS,
)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_job_config(config: JobConfig) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not config.workflow_id or not str(config.workflow_id).strip():
        errors.append("workflow_id is required")

    if not config.input_path.exists():
        errors.append(f"Input file not found: {config.input_path}")
    elif not config.input_path.is_file():
        errors.append(f"Input path is not a file: {config.input_path}")

    if config.output_path.exists() and config.output_path.is_dir():
        errors.append(f"Output path is a directory: {config.output_path}")

    workflow = config.workflow if isinstance(config.workflow, dict) else None
    if workflow is None:
        errors.append("workflow must be an object")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    steps = workflow.get(WORKFLOW_KEY_STEPS, [])
    if steps is None:
        steps = []
    if not isinstance(steps, list):
        errors.append(f"workflow.{WORKFLOW_KEY_STEPS} must be a list")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"steps[{idx}] must be an object")
            continue

        op = step.get(STEP_KEY_OP)
        if not isinstance(op, str) or not op.strip():
            errors.append(f"steps[{idx}].{STEP_KEY_OP} is required")
            continue

        if op not in SUPPORTED_OPS:
            errors.append(f"steps[{idx}].{STEP_KEY_OP} unknown op: {op}")
            continue

        if op in (OP_PREFIX, OP_SUFFIX, OP_FILTER_CONTAINS):
            if STEP_KEY_VALUE not in step or not isinstance(step.get(STEP_KEY_VALUE), str):
                errors.append(f"steps[{idx}] requires string '{STEP_KEY_VALUE}'")

        if op == OP_REPLACE:
            if STEP_KEY_OLD not in step or not isinstance(step.get(STEP_KEY_OLD), str):
                errors.append(f"steps[{idx}] requires string '{STEP_KEY_OLD}'")
            if STEP_KEY_NEW not in step or not isinstance(step.get(STEP_KEY_NEW), str):
                errors.append(f"steps[{idx}] requires string '{STEP_KEY_NEW}'")

        if op == OP_SLEEP_MS:
            ms = step.get(STEP_KEY_MS)
            if not isinstance(ms, (int, float)) or ms < 0:
                errors.append(f"steps[{idx}] requires non-negative number '{STEP_KEY_MS}'")

    return ValidationResult(valid=(len(errors) == 0), errors=errors, warnings=warnings)

