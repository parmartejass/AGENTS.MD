#!/usr/bin/env python3
"""
Cross-platform governance checks.

This script consolidates cross-platform governance checks:
1) check_agents_manifest.ps1
2) check_docs_ssot.ps1
3) check_project_docs.ps1
4) check_repo_hygiene.ps1
5) docs unresolved citation placeholders
6) governance learnings playbook hard-gate parity
7) check_change_records.ps1 equivalent validation
8) optional strict python safety mode
9) instruction derivation scaffold validation
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

if sys.version_info < (3, 11):
    sys.stderr.write("FAILED_VALIDATION: Python 3.11+ is required for governance core checks.\n")
    raise SystemExit(1)

try:
    from ._change_records import check_change_records
    from ._instruction_derivation import check_instruction_derivation_gate
    from ._manifest_and_docs import check_agents_manifest, check_docs_ssot, check_project_docs
    from ._repo_and_governance import (
        check_docs_for_retired_active_references,
        check_docs_for_unresolved_citations,
        check_governance_authority_decisions,
        check_governance_playbook_hard_gates,
        check_repo_hygiene,
        check_subagent_council_profile_coverage,
    )
    from ._runtime_projection import check_runtime_projection_manifest
    from ._shared import PYTHON_SAFETY_TIMEOUT_SEC, configure_logging, context, logger
except ImportError:  # pragma: no cover - script-path execution
    from _change_records import check_change_records
    from _instruction_derivation import check_instruction_derivation_gate
    from _manifest_and_docs import check_agents_manifest, check_docs_ssot, check_project_docs
    from _repo_and_governance import (
        check_docs_for_retired_active_references,
        check_docs_for_unresolved_citations,
        check_governance_authority_decisions,
        check_governance_playbook_hard_gates,
        check_repo_hygiene,
        check_subagent_council_profile_coverage,
    )
    from _runtime_projection import check_runtime_projection_manifest
    from _shared import PYTHON_SAFETY_TIMEOUT_SEC, configure_logging, context, logger


def _run_python_safety_check(
    repo_root: Path, governance_root: Path, *, fail_on_warnings: bool
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    notes: List[str] = []

    safety_script = governance_root / "scripts/check_python_safety/check_python_safety_main.py"
    if not safety_script.is_file():
        return [f"Missing Python safety script: {safety_script}"], notes

    cmd = [sys.executable, str(safety_script), "--root", str(repo_root)]
    if fail_on_warnings:
        cmd.append("--fail-on-warnings")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=PYTHON_SAFETY_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        return ["Python interpreter not found while running scripts/check_python_safety/check_python_safety_main.py."], notes
    except subprocess.TimeoutExpired:
        return [f"scripts/check_python_safety/check_python_safety_main.py timed out after {PYTHON_SAFETY_TIMEOUT_SEC}s."], notes

    notes.extend((result.stdout or "").splitlines())
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if stderr:
            notes.append(stderr)
        errors.append(
            "Python safety baseline check failed. "
            "Run scripts/check_python_safety/check_python_safety_main.py directly for details."
        )
    return errors, notes


def main(argv: Sequence[str]) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(
        description=(
            "Run cross-platform governance checks for manifest/docs/project-docs/hygiene, "
            "governance playbook parity, unresolved citation markers, and change-record validation."
        )
    )
    parser.add_argument("--repo-root", help="Target repo root (default: governance root).")
    parser.add_argument(
        "--governance-root",
        help="Governance root that contains AGENTS.md and agents-manifest.yaml "
        "(default: parent of this script).",
    )
    parser.add_argument(
        "--require-records",
        action="store_true",
        help=(
            "Require docs/project/change-records/*.json (same behavior as "
            "docs/project/change-records/.required marker)."
        ),
    )
    parser.add_argument(
        "--only-change-records",
        action="store_true",
        help="Run only change-record artifact checks.",
    )
    parser.add_argument(
        "--only-docs-ssot",
        action="store_true",
        help="Run only docs SSOT/router/header checks.",
    )
    parser.add_argument(
        "--only-project-docs",
        action="store_true",
        help="Run only project docs linkage/routing checks.",
    )
    parser.add_argument(
        "--fail-on-safety-warnings",
        action="store_true",
        help="Run scripts/check_python_safety/check_python_safety_main.py with --fail-on-warnings.",
    )
    parser.add_argument(
        "--success-marker",
        help="Emit this opaque marker only after the requested validator mode completes successfully.",
    )
    args = parser.parse_args(argv)

    try:
        repo_root, governance_root, governance_rel = context(
            args.repo_root, args.governance_root, Path(__file__).resolve().parent
        )
    except RuntimeError as err:
        logger.error("ERROR: %s", err)
        return 1

    narrow_modes = [args.only_change_records, args.only_docs_ssot, args.only_project_docs]
    if sum(1 for enabled in narrow_modes if enabled) > 1:
        logger.error("ERROR: Choose only one narrow check mode.")
        return 1

    if args.only_change_records:
        change_record_errors, change_record_notes = check_change_records(
            repo_root, governance_root, require_records=args.require_records
        )
        if change_record_errors:
            for issue in change_record_errors:
                logger.error("ERROR: %s", issue)
            logger.error("Change record checks failed: %s issue(s).", len(change_record_errors))
            return 1
        for note in change_record_notes or ["Change record checks passed."]:
            logger.info(note)
        _emit_success_marker(args.success_marker)
        return 0

    if args.only_docs_ssot:
        docs_errors, docs_notes = check_docs_ssot(repo_root, governance_root)
        if docs_errors:
            for issue in docs_errors:
                logger.error("ERROR: %s", issue)
            logger.error("Docs SSOT checks failed: %s issue(s).", len(docs_errors))
            return 1
        logger.info("Docs SSOT checks passed.")
        for note in docs_notes:
            logger.info(note)
        _emit_success_marker(args.success_marker)
        return 0

    if args.only_project_docs:
        project_docs_errors = check_project_docs(repo_root, governance_rel, governance_root)
        if project_docs_errors:
            for issue in project_docs_errors:
                logger.error("ERROR: %s", issue)
            logger.error("Project docs checks failed: %s issue(s).", len(project_docs_errors))
            return 1
        logger.info("Project docs checks passed.")
        _emit_success_marker(args.success_marker)
        return 0

    docs_errors, docs_notes = check_docs_ssot(repo_root, governance_root)
    runtime_projection_errors, runtime_projection_notes = check_runtime_projection_manifest(
        repo_root, governance_root
    )
    total_errors = 0
    for errors, success_message, notes in (
        (check_agents_manifest(governance_root), "Agents manifest checks passed.", []),
        (docs_errors, "Docs SSOT checks passed.", docs_notes),
        (check_project_docs(repo_root, governance_rel, governance_root), "Project docs checks passed.", []),
        (check_repo_hygiene(repo_root), "Repo hygiene checks passed.", []),
        (check_docs_for_unresolved_citations(repo_root), "Docs unresolved-citation checks passed.", []),
        (check_docs_for_retired_active_references(repo_root), "Docs retired-reference checks passed.", []),
        (check_governance_playbook_hard_gates(governance_root), "Governance playbook authority-scaffold checks passed.", []),
        (check_instruction_derivation_gate(governance_root), "Instruction derivation scaffold checks passed.", []),
        (check_subagent_council_profile_coverage(governance_root), "Subagent council profile-coverage checks passed.", []),
        (check_governance_authority_decisions(governance_root), "Governance authority decision registry checks passed.", []),
        (runtime_projection_errors, "Runtime projection manifest checks passed.", runtime_projection_notes),
    ):
        if errors:
            for issue in errors:
                logger.error("ERROR: %s", issue)
            total_errors += len(errors)
        elif success_message:
            logger.info(success_message)
        for note in notes:
            logger.info(note)

    change_record_errors, change_record_notes = check_change_records(
        repo_root, governance_root, require_records=args.require_records
    )
    if change_record_errors:
        for issue in change_record_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(change_record_errors)
    else:
        for note in change_record_notes or ["Change record checks passed."]:
            logger.info(note)

    if args.fail_on_safety_warnings:
        safety_errors, safety_notes = _run_python_safety_check(
            repo_root, governance_root, fail_on_warnings=True
        )
        for note in safety_notes:
            logger.info(note)
        if safety_errors:
            for issue in safety_errors:
                logger.error("ERROR: %s", issue)
            total_errors += len(safety_errors)
        else:
            logger.info("Python safety strict-mode checks passed.")

    if total_errors > 0:
        logger.error("Governance core checks failed: %s issue(s).", total_errors)
        return 1

    logger.info("Governance core checks passed.")
    _emit_success_marker(args.success_marker)
    return 0


def _emit_success_marker(marker: str | None) -> None:
    if marker:
        logger.info("VALIDATOR_SUCCESS_MARKER: %s", marker)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
