from __future__ import annotations

import argparse
import logging
import logging.config
from collections.abc import Sequence

from scripts.check_governance_core._api import run_checks


logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"message": {"format": "%(message)s"}},
            "handlers": {
                "stdout": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "message"},
            },
            "loggers": {__name__: {"handlers": ["stdout"], "level": "INFO"}},
        }
    )


def _parse_request(argv: Sequence[str]) -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Run the governance-core public validation contract.")
    parser.add_argument("--repo-root")
    parser.add_argument("--governance-root")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--only-docs-ssot", action="store_true")
    modes.add_argument("--only-project-docs", action="store_true")
    parser.add_argument("--fail-on-safety-warnings", action="store_true")
    args = parser.parse_args(argv)
    if args.only_docs_ssot:
        mode = "docs"
    elif args.only_project_docs:
        mode = "project_docs"
    else:
        mode = "full"
    return {
        "repo_root": args.repo_root,
        "governance_root": args.governance_root,
        "mode": mode,
        "fail_on_safety_warnings": args.fail_on_safety_warnings,
    }


def _render(result: dict[str, object]) -> None:
    records = result.get("checks", [])
    for record in records:
        logger.info("%s: %s", record["id"], record["status"])
        for warning in record["warnings"]:
            logger.warning("WARNING: %s", warning)
        for error in record["errors"]:
            logger.error("ERROR: %s", error)
    if not records:
        for error in result.get("errors", []):
            logger.error("ERROR: %s", error)
    logger.info("Governance core: %s", result["status"])


def main(argv: Sequence[str]) -> int:
    """Command-line adapter: parse arguments, run the public contract, render the result."""

    _configure_logging()
    result = run_checks(_parse_request(argv))
    _render(result)
    return 0 if result["status"] == "PASSED" else 1
