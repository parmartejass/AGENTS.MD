"""Top-level entry wrapper: default to GUI, auto-route CLI flags."""

from __future__ import annotations

import logging
import sys

from myapp.cli.main import build_cli_request, has_cli_intent
from myapp.core.main import compare_text_files
from myapp.errors import ConfigError
from myapp.gui.main import start_gui
from myapp.logging_config import setup_logging
from myapp.runner.main import run_job


logger = logging.getLogger(__name__)


def _run_cli(argv: list[str]) -> int:
    try:
        request = build_cli_request(argv)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    result = run_job(request.job, mode="cli")

    if request.verify:
        if result.success != request.expected_success:
            logger.error(
                "Verification failed: expected success=%s but got success=%s",
                request.expected_success,
                result.success,
            )
            return 1

        if request.expected_output_path is not None and result.output_path is not None and result.success:
            verification = compare_text_files(
                expected_path=request.expected_output_path,
                actual_path=result.output_path,
            )
            if not verification.matches:
                logger.error("Verification failed: output mismatch")
                if verification.diff:
                    logger.error("Diff:\n%s", verification.diff)
                return 1

    return result.exit_code


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if has_cli_intent(argv):
        return _run_cli(argv)

    setup_logging()
    logger.debug("argv=%s", argv)

    try:
        start_gui(run_job)
        return 0
    except Exception:
        logger.exception("GUI startup failed")
        return 1
