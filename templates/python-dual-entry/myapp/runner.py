"""Orchestration layer (SSOT): GUI/CLI/tests all call `run_job()`."""

from __future__ import annotations

import logging
from threading import Event

from myapp.config import JobConfig, JobResult, RunStatus
from myapp.core.validators import validate_job_config
from myapp.workflows import get_workflow


logger = logging.getLogger(__name__)


def run_job(config: JobConfig, *, cancel_event: Event | None = None) -> JobResult:
    logger.info("Job starting: workflow=%s input=%s", config.workflow_id, config.input_path)
    logger.debug("Full job config: %s", config)

    validation = validate_job_config(config)
    if not validation.valid:
        logger.error("Validation failed: %s", validation.errors)
        return JobResult(
            success=False,
            status=RunStatus.FAILED,
            errors=validation.errors,
            warnings=validation.warnings,
        )

    workflow = get_workflow(config.workflow_id)
    if workflow is None:
        message = f"Unknown workflow_id: {config.workflow_id}"
        logger.error(message)
        return JobResult(success=False, status=RunStatus.FAILED, errors=[message])

    is_cancelled = cancel_event.is_set if cancel_event is not None else (lambda: False)

    try:
        result = workflow.run(config, is_cancelled)
    except FileNotFoundError as exc:
        logger.error("File not found: %s", exc)
        return JobResult(success=False, status=RunStatus.FAILED, errors=[f"File not found: {exc}"])
    except PermissionError as exc:
        logger.error("Permission denied: %s", exc)
        return JobResult(success=False, status=RunStatus.FAILED, errors=[f"Permission denied: {exc}"])
    except OSError as exc:
        logger.error("OS error: %s", exc)
        return JobResult(success=False, status=RunStatus.FAILED, errors=[f"OS error: {exc}"])
    except Exception as exc:
        logger.exception("Unexpected error")
        return JobResult(success=False, status=RunStatus.FAILED, errors=[f"Unexpected error: {exc}"])

    if result.cancelled:
        logger.warning("Job cancelled")
        return JobResult(
            success=False,
            status=RunStatus.CANCELLED,
            lines_processed=result.lines_processed,
            warnings=validation.warnings,
            errors=["Cancelled"],
        )

    if not result.success:
        logger.error("Job failed: %s", result.error or "unknown error")
        return JobResult(
            success=False,
            status=RunStatus.FAILED,
            lines_processed=result.lines_processed,
            warnings=validation.warnings,
            errors=[result.error or "Unknown error"],
        )

    if not config.output_path.exists():
        message = f"Output file was not created: {config.output_path}"
        logger.error(message)
        return JobResult(success=False, status=RunStatus.FAILED, errors=[message], warnings=validation.warnings)

    logger.info("Job completed: lines_processed=%s output=%s", result.lines_processed, config.output_path)
    return JobResult(
        success=True,
        status=RunStatus.EXECUTED,
        output_path=config.output_path,
        lines_processed=result.lines_processed,
        warnings=validation.warnings,
    )

