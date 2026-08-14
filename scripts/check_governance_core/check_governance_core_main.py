#!/usr/bin/env python3
"""Stable public API and CLI adapter for governance-core validation.

Programmatic contract:
    run_checks(request) -> plain dictionary

The request accepts ``repo_root``, ``governance_root``, ``mode`` (``full``,
``docs``, or ``project_docs``), and ``fail_on_safety_warnings``. Validation is
read-only; strict mode promotes Python-safety warnings to failures. Invalid
requests and unexpected failures are returned as
explicit FAILED_VALIDATION/FAILED results; callers do not import private files.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path


REPO_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_IMPORT_ROOT))

from scripts.check_governance_core._engine import execute, resolve_documents_request  # noqa: E402


logger = logging.getLogger("check_governance_core")


def _validate_root_fields(request: Mapping[str, object]) -> str | None:
    for field in ("repo_root", "governance_root"):
        value = request.get(field)
        if value is not None and not isinstance(value, (str, Path)):
            return f"{field} must be a path string, Path, or null"
        if field in request and isinstance(value, (str, Path)) and not str(value).strip():
            return f"{field} must not be empty when provided"
    return None


def _validate_check_request(request: Mapping[str, object]) -> str | None:
    root_error = _validate_root_fields(request)
    if root_error:
        return root_error
    mode = request.get("mode", "full")
    if not isinstance(mode, str):
        return "mode must be a string"
    strict = request.get("fail_on_safety_warnings", False)
    if not isinstance(strict, bool):
        return "fail_on_safety_warnings must be a boolean"
    return None


def run_checks(request: Mapping[str, object]) -> dict[str, object]:
    """Run deterministic checks through the only supported programmatic boundary.

    Inputs and outputs contain plain data only. The function does not mutate the
    caller's mapping. Unsupported keys are rejected so extension remains an
    explicit public-contract change.
    """

    if not isinstance(request, Mapping):
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "checks": [],
            "planned": [],
            "eligible": [],
            "executed": [],
            "skipped": [],
            "failed": [],
            "errors": ["request must be a mapping"],
            "warnings": [],
        }
    allowed = {"repo_root", "governance_root", "mode", "fail_on_safety_warnings"}
    unknown = sorted(str(key) for key in request if key not in allowed)
    if unknown:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "checks": [],
            "planned": [],
            "eligible": [],
            "executed": [],
            "skipped": [],
            "failed": [],
            "errors": [f"unsupported request key(s): {', '.join(unknown)}"],
            "warnings": [],
        }
    validation_error = _validate_check_request(request)
    if validation_error:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "checks": [],
            "planned": [],
            "eligible": [],
            "executed": [],
            "skipped": [],
            "failed": [],
            "errors": [validation_error],
            "warnings": [],
        }
    try:
        return execute(dict(request))
    except ValueError as exc:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "checks": [],
            "planned": [],
            "eligible": [],
            "executed": [],
            "skipped": [],
            "failed": [],
            "errors": [str(exc)],
            "warnings": [],
        }
    except Exception as exc:  # public boundary converts crashes into explicit failure
        return {
            "api_version": 1,
            "status": "FAILED",
            "checks": [],
            "planned": [],
            "eligible": [],
            "executed": [],
            "skipped": [],
            "failed": [],
            "errors": [f"internal governance-check failure: {type(exc).__name__}: {exc}"],
            "warnings": [],
        }


def resolve_documents(request: Mapping[str, object]) -> dict[str, object]:
    """Return the canonical router-owned governance research corpus.

    Accepted inputs are ``repo_root`` and ``governance_root``. The read-only
    result contains ``api_version``, terminal ``status``, ``AGENTS.md`` followed
    by ordered terminal Markdown leaves reachable from
    ``docs/agents/agents_index.md``, and ``errors``. Routing-manifest membership
    does not define this corpus. Invalid, aliased, escaped, missing, cyclic, or
    duplicate topology returns an empty document list and explicit failure.
    """

    if not isinstance(request, Mapping):
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "documents": [],
            "errors": ["request must be a mapping"],
        }
    unknown = sorted(str(key) for key in request if key not in {"repo_root", "governance_root"})
    if unknown:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "documents": [],
            "errors": [f"unsupported request key(s): {', '.join(unknown)}"],
        }
    root_error = _validate_root_fields(request)
    if root_error:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "documents": [],
            "errors": [root_error],
        }
    try:
        return resolve_documents_request(dict(request))
    except ValueError as exc:
        return {
            "api_version": 1,
            "status": "FAILED_VALIDATION",
            "documents": [],
            "errors": [str(exc)],
        }
    except Exception as exc:
        return {
            "api_version": 1,
            "status": "FAILED",
            "documents": [],
            "errors": [f"internal governance-document resolution failure: {type(exc).__name__}: {exc}"],
        }


def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def main(argv: Sequence[str]) -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(description="Run the governance-core public validation contract.")
    parser.add_argument("--repo-root")
    parser.add_argument("--governance-root")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--only-docs-ssot", action="store_true")
    modes.add_argument("--only-project-docs", action="store_true")
    parser.add_argument("--fail-on-safety-warnings", action="store_true")
    args = parser.parse_args(argv)
    mode = "docs" if args.only_docs_ssot else "project_docs" if args.only_project_docs else "full"
    result = run_checks(
        {
            "repo_root": args.repo_root,
            "governance_root": args.governance_root,
            "mode": mode,
            "fail_on_safety_warnings": args.fail_on_safety_warnings,
        }
    )
    for record in result.get("checks", []):
        logger.info("%s: %s", record["id"], record["status"])
        for warning in record["warnings"]:
            logger.warning("WARNING: %s", warning)
        for error in record["errors"]:
            logger.error("ERROR: %s", error)
    for error in result.get("errors", []) if not result.get("checks") else []:
        logger.error("ERROR: %s", error)
    logger.info("Governance core: %s", result["status"])
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
