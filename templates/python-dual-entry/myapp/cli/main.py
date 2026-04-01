"""CLI entry point (thin): parse args -> load scenario -> return plain request data."""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from myapp import __version__
from myapp.errors import ConfigError
from myapp.logging_config import setup_logging
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


@dataclass(frozen=True)
class CliRequest:
    job: object
    verify: bool
    expected_success: bool
    expected_output_path: Path | None


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


def build_cli_request(argv: list[str] | None = None) -> CliRequest:
    args = parse_args(argv)
    setup_logging(verbose=args.verbose, log_file=args.log_file, event_log=args.event_log)

    scenario = load_scenario(args.scenario)

    logger.info("Scenario: %s", scenario.scenario_id)
    if scenario.description:
        logger.info("Description: %s", scenario.description)

    return CliRequest(
        job=scenario.job,
        verify=args.verify,
        expected_success=scenario.expected.success,
        expected_output_path=scenario.expected.output_path,
    )
