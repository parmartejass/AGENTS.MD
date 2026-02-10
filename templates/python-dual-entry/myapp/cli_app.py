"""CLI entry point (thin): parse args -> load scenario -> run job -> optional verify."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from myapp import __version__
from myapp.core.verification import compare_text_files
from myapp.errors import ConfigError
from myapp.logging_config import setup_logging
from myapp.runner import run_job
from myapp.scenarios import load_scenario


logger = logging.getLogger(__name__)

CLI_INTENT_FLAGS = frozenset(
    {
        "--cli",
        "--scenario",
        "--verify",
        "--verbose",
        "--log-file",
        "--event-log",
        "--help",
        "-h",
        "--version",
    }
)
CLI_INTENT_PREFIXES = ("--scenario=", "--log-file=", "--event-log=")


def has_cli_intent(argv: list[str]) -> bool:
    for token in argv:
        if token in CLI_INTENT_FLAGS:
            return True
        if any(token.startswith(prefix) for prefix in CLI_INTENT_PREFIXES):
            return True
        if token.startswith("-"):
            return True
    return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="myapp", description="Dual-entry automation template (CLI mode).")

    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (dispatcher trigger).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--scenario", type=Path, required=True, help="Path to a scenario JSON file.")
    parser.add_argument("--verify", action="store_true", help="Verify outputs vs scenario.expected.*.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional log file path.")
    parser.add_argument("--event-log", type=Path, default=None, help="Optional structured JSONL event log path.")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(verbose=args.verbose, log_file=args.log_file, event_log=args.event_log)

    try:
        scenario = load_scenario(args.scenario)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    logger.info("Scenario: %s", scenario.scenario_id)
    if scenario.description:
        logger.info("Description: %s", scenario.description)

    result = run_job(scenario.job, mode="cli")

    if args.verify:
        if result.success != scenario.expected.success:
            logger.error(
                "Verification failed: expected success=%s but got success=%s",
                scenario.expected.success,
                result.success,
            )
            return 1

        if scenario.expected.output_path is not None and result.output_path is not None and result.success:
            verification = compare_text_files(
                expected_path=scenario.expected.output_path,
                actual_path=result.output_path,
            )
            if not verification.matches:
                logger.error("Verification failed: output mismatch")
                if verification.diff:
                    logger.error("Diff:\n%s", verification.diff)
                return 1

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
