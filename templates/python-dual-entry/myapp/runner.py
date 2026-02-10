"""Orchestration layer (SSOT): GUI/CLI/tests all call `run_job()`."""

from __future__ import annotations

import logging
import time
from threading import Event

from myapp import __version__
from myapp.config import JobConfig, JobResult, RunStatus
from myapp.core.validators import validate_job_config
from myapp.log_contract import ItemOutcome, Phase, ReasonCode, RunResultKind
from myapp.log_redaction import sanitize_for_logging
from myapp.observability import (
    begin_run_context,
    build_io_snapshot,
    emit_failure,
    emit_item_terminal,
    emit_phase_transition,
    emit_run_end,
    emit_run_start,
)
from myapp.workflows import get_workflow


logger = logging.getLogger(__name__)


def run_job(config: JobConfig, *, cancel_event: Event | None = None, mode: str = "unknown") -> JobResult:
    run = begin_run_context(app="myapp", version=__version__, mode=mode)
    start_monotonic = time.perf_counter()

    logger.info("Job starting: run_id=%s workflow=%s input=%s", run.run_id, config.workflow_id, config.input_path)
    logger.debug(
        "Full job config: %s",
        sanitize_for_logging(
            {
                "workflow_id": config.workflow_id,
                "input_path": config.input_path,
                "output_path": config.output_path,
                "workflow": config.workflow,
            }
        ),
    )

    inputs, outputs = build_io_snapshot(input_path=config.input_path, output_path=config.output_path)
    emit_run_start(
        run,
        inputs=inputs,
        outputs=outputs,
        config_snapshot={"workflow_id": config.workflow_id, "workflow": config.workflow},
    )

    phase_seq = 0
    current_phase = Phase.INIT
    warnings: list[str] = []
    error_records: list[dict[str, object]] = []
    item_outcome = ItemOutcome.FAILED
    final_phase = Phase.FAILED_COMMIT
    reason_code = ReasonCode.UNEXPECTED_EXCEPTION
    reason_detail = "Execution did not reach a terminal success state."
    run_result = RunResultKind.FAILURE
    lines_processed = 0
    write_effects: dict[str, object] = {"output_path": str(config.output_path), "created": False}

    result = JobResult(
        success=False,
        status=RunStatus.FAILED,
        run_id=run.run_id,
        errors=[reason_detail],
    )

    def transition(phase: Phase, notes: str | None = None) -> None:
        nonlocal phase_seq, current_phase
        phase_seq += 1
        current_phase = phase
        emit_phase_transition(run, phase=phase, phase_seq=phase_seq, notes=notes)

    transition(Phase.INIT, notes="run initialized")

    try:
        validation = validate_job_config(config)
        warnings = validation.warnings
        if not validation.valid:
            reason_code = ReasonCode.VALIDATION_FAILED
            reason_detail = "; ".join(validation.errors) if validation.errors else "Validation failed"
            final_phase = Phase.FAILED_VALIDATION
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("Validation failed: %s", validation.errors)
            error_records.append(
                {
                    "type": "ValidationError",
                    "message": reason_detail,
                    "where": "myapp.runner.run_job",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_VALIDATION, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_VALIDATION,
                reason_code=reason_code,
                reason_detail=reason_detail,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=validation.errors,
                warnings=warnings,
            )
            return result

        transition(Phase.VALIDATED, notes="validation passed")

        workflow = get_workflow(config.workflow_id)
        if workflow is None:
            reason_code = ReasonCode.UNKNOWN_WORKFLOW
            reason_detail = f"Unknown workflow_id: {config.workflow_id}"
            final_phase = Phase.FAILED_VALIDATION
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("%s", reason_detail)
            error_records.append(
                {
                    "type": "WorkflowError",
                    "message": reason_detail,
                    "where": "myapp.runner.run_job",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_VALIDATION, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_VALIDATION,
                reason_code=reason_code,
                reason_detail=reason_detail,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result

        transition(Phase.COMMIT_READY, notes="workflow selected")
        transition(Phase.COMMITTING, notes="workflow execution started")
        is_cancelled = cancel_event.is_set if cancel_event is not None else (lambda: False)

        try:
            workflow_result = workflow.run(config, is_cancelled)
        except FileNotFoundError as exc:
            reason_code = ReasonCode.FILE_NOT_FOUND
            reason_detail = f"File not found: {exc}"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("%s", reason_detail)
            error_records.append(
                {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "where": "workflow.run",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
                exc=exc,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result
        except PermissionError as exc:
            reason_code = ReasonCode.PERMISSION_DENIED
            reason_detail = f"Permission denied: {exc}"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("%s", reason_detail)
            error_records.append(
                {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "where": "workflow.run",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
                exc=exc,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result
        except OSError as exc:
            reason_code = ReasonCode.OS_ERROR
            reason_detail = f"OS error: {exc}"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("%s", reason_detail)
            error_records.append(
                {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "where": "workflow.run",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
                exc=exc,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result
        except Exception as exc:
            reason_code = ReasonCode.UNEXPECTED_EXCEPTION
            reason_detail = f"Unexpected error: {exc}"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.exception("Unexpected error")
            error_records.append(
                {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "where": "workflow.run",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
                exc=exc,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result

        lines_processed = workflow_result.lines_processed

        if workflow_result.cancelled:
            reason_code = ReasonCode.CANCELLED
            reason_detail = "Cancelled"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.SKIPPED
            run_result = RunResultKind.PARTIAL_SUCCESS
            logger.warning("Job cancelled")
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
            )
            transition(Phase.CLEANING, notes="post-failure cleanup")
            result = JobResult(
                success=False,
                status=RunStatus.CANCELLED,
                run_id=run.run_id,
                lines_processed=lines_processed,
                warnings=warnings,
                errors=[reason_detail],
            )
            return result

        if not workflow_result.success:
            reason_code = ReasonCode.WORKFLOW_FAILED
            reason_detail = workflow_result.error or "Unknown workflow error"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("Job failed: %s", reason_detail)
            error_records.append(
                {
                    "type": "WorkflowError",
                    "message": reason_detail,
                    "where": "workflow.run",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                lines_processed=lines_processed,
                warnings=warnings,
                errors=[reason_detail],
            )
            return result

        if not config.output_path.exists():
            reason_code = ReasonCode.OUTPUT_NOT_CREATED
            reason_detail = f"Output file was not created: {config.output_path}"
            final_phase = Phase.FAILED_COMMIT
            item_outcome = ItemOutcome.FAILED
            run_result = RunResultKind.FAILURE
            logger.error("%s", reason_detail)
            error_records.append(
                {
                    "type": "FileIOError",
                    "message": reason_detail,
                    "where": "myapp.runner.run_job",
                    "fatal": True,
                }
            )
            transition(Phase.FAILED_COMMIT, notes=reason_detail)
            emit_failure(
                run,
                phase=Phase.FAILED_COMMIT,
                reason_code=reason_code,
                reason_detail=reason_detail,
            )
            result = JobResult(
                success=False,
                status=RunStatus.FAILED,
                run_id=run.run_id,
                errors=[reason_detail],
                warnings=warnings,
            )
            return result

        write_effects = {
            "output_path": str(config.output_path),
            "created": True,
            "size_bytes": config.output_path.stat().st_size,
        }
        reason_code = ReasonCode.COMPLETED
        reason_detail = "Workflow completed successfully."
        final_phase = Phase.DONE
        item_outcome = ItemOutcome.EXECUTED
        run_result = RunResultKind.SUCCESS
        transition(Phase.CLEANING, notes="post-commit checks")
        transition(Phase.DONE, notes="run complete")
        logger.info("Job completed: lines_processed=%s output=%s", lines_processed, config.output_path)
        result = JobResult(
            success=True,
            status=RunStatus.EXECUTED,
            run_id=run.run_id,
            output_path=config.output_path,
            lines_processed=lines_processed,
            warnings=warnings,
        )
        return result
    except Exception as exc:
        reason_code = ReasonCode.UNEXPECTED_EXCEPTION
        reason_detail = f"Unexpected runner error: {exc}"
        final_phase = Phase.FAILED_COMMIT
        item_outcome = ItemOutcome.FAILED
        run_result = RunResultKind.FAILURE
        logger.exception("Unexpected error while orchestrating run")
        error_records.append(
            {
                "type": type(exc).__name__,
                "message": str(exc),
                "where": "myapp.runner.run_job",
                "fatal": True,
            }
        )
        transition(Phase.FAILED_COMMIT, notes=reason_detail)
        emit_failure(
            run,
            phase=Phase.FAILED_COMMIT,
            reason_code=reason_code,
            reason_detail=reason_detail,
            exc=exc,
        )
        result = JobResult(
            success=False,
            status=RunStatus.FAILED,
            run_id=run.run_id,
            lines_processed=lines_processed,
            warnings=warnings,
            errors=[reason_detail],
        )
        return result
    finally:
        duration_ms = int((time.perf_counter() - start_monotonic) * 1000)
        emit_item_terminal(
            run,
            phase=current_phase,
            item_id=str(config.input_path),
            outcome=item_outcome,
            final_phase=final_phase,
            reason_code=reason_code,
            reason_detail=reason_detail,
            evidence={"warnings": warnings, "lines_processed": lines_processed},
            write_effects=write_effects,
            duration_ms=duration_ms,
        )
        summary = {
            "by_outcome": {
                "executed": 1 if item_outcome == ItemOutcome.EXECUTED else 0,
                "skipped": 1 if item_outcome == ItemOutcome.SKIPPED else 0,
                "failed": 1 if item_outcome == ItemOutcome.FAILED else 0,
            },
            "failed_by_phase": {
                "validation": 1 if final_phase == Phase.FAILED_VALIDATION else 0,
                "commit": 1 if final_phase == Phase.FAILED_COMMIT else 0,
                "cleanup": 1 if final_phase == Phase.FAILED_CLEANUP else 0,
            },
        }
        emit_run_end(
            run,
            result=run_result,
            summary=summary,
            timings_ms={"total": duration_ms},
            errors=error_records,
            resources={"event_log_path": str(run.event_log_path)},
        )
