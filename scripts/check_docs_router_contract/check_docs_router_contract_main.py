#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock
from uuid import uuid4


POWERSHELL_TIMEOUT_SEC = 30
SCRIPT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SCRIPT_ROOT / "check_governance_core" / "_manifest_and_docs.py"
DOCS_SSOT_SCRIPT_PATH = SCRIPT_ROOT / "check_docs_ssot.ps1"
ENTRYPOINT_REGISTRY_PATH = SCRIPT_ROOT / "entrypoint_contracts.json"

SPEC = importlib.util.spec_from_file_location("_manifest_and_docs", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load docs-check module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_docs_ssot = MODULE.check_docs_ssot

ENTRYPOINT_CONTRACTS = json.loads(ENTRYPOINT_REGISTRY_PATH.read_text(encoding="utf-8"))
DOCS_CONTRACT = ENTRYPOINT_CONTRACTS["docs"]
TMP_ROOT = SCRIPT_ROOT / "check_docs_router_contract" / ".tmp-test-workspaces"


POLICY_DOC = """
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md
update_trigger: docs governance rules change
---

# Docs SSOT Policy

```md
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <module path> | <workflow registry location>
update_trigger: <what change requires updating this doc>
---
```
"""


def resolve_docs_authority(folder_name: str) -> str:
    numbered = re.match(DOCS_CONTRACT["authority_resolution"]["numbered_governance_folder_regex"], folder_name)
    if numbered:
        return numbered.group("authority")
    if re.match(DOCS_CONTRACT["authority_resolution"]["dated_evidence_folder_regex"], folder_name):
        return DOCS_CONTRACT["authority_resolution"]["dated_evidence_authority"]
    return folder_name


def resolve_router_filename(folder_name: str) -> str:
    return DOCS_CONTRACT["router_pattern"].replace("<authority>", resolve_docs_authority(folder_name))


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = textwrap.dedent(content).lstrip("\n")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(rendered)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _write(path: Path, content: str) -> None:
    _atomic_write_text(path, content)


@contextmanager
def _temporary_workspace():
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    tmp_root = TMP_ROOT / uuid4().hex
    tmp_root.mkdir(parents=True, exist_ok=False)
    try:
        yield tmp_root
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def _write_registry(governance_root: Path) -> None:
    _write(
        governance_root / "scripts/entrypoint_contracts.json",
        ENTRYPOINT_REGISTRY_PATH.read_text(encoding="utf-8"),
    )


def _route_line(target: str, description: str, *, when: str | None = None) -> str:
    trigger = when or f"you need {target}"
    return f"- [{target}]({target}) - {description}. Required when: {trigger}."


def _write_router(path: Path, title: str, route_lines: list[str]) -> None:
    _write(path, "\n".join([f"# {title}", "", *route_lines, ""]))


def _write_parent_chain(repo_root: Path, rel_dir: str) -> None:
    parts = rel_dir.split("/")
    chain: list[str] = []
    docs_root = repo_root / "docs"
    for part in parts:
        parent_dir = docs_root / "/".join(chain) if chain else docs_root
        parent_router = parent_dir / resolve_router_filename(parent_dir.name)
        title = "Docs Branch Index" if not chain else f"{chain[-1].title()} Branch Index"
        target = f"{part}/{resolve_router_filename(part)}"
        _write_router(
            parent_router,
            title,
            [_route_line(target, f"route into {part}", when=f"navigating into the {part} branch")],
        )
        chain.append(part)


def _write_router_fixture(
    repo_root: Path,
    governance_root: Path,
    rel_dir: str,
    primary_leaf_name: str,
    *,
    router_target: str | None = None,
    extra_leaf_names: list[str] | None = None,
    content_bearing_router: bool = False,
) -> None:
    _write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
    _write_registry(governance_root)
    _write_parent_chain(repo_root, rel_dir)

    final_dir = repo_root / "docs" / rel_dir
    router_name = resolve_router_filename(final_dir.name)
    router_lines: list[str] = []
    if content_bearing_router:
        router_lines.extend(["This should not be narrative prose.", ""])
    router_lines.append(
        _route_line(
            router_target or primary_leaf_name,
            "canonical narrative leaf",
            when="reviewing the canonical narrative content",
        )
    )
    for extra_leaf_name in extra_leaf_names or []:
        router_lines.append(
            _route_line(
                extra_leaf_name,
                "additional public leaf",
                when=f"reviewing the {extra_leaf_name} public leaf",
            )
        )
    _write_router(final_dir / router_name, f"{rel_dir.split('/')[-1].title()} Branch Index", router_lines)
    _write(
        final_dir / primary_leaf_name,
        """
        ---
        doc_type: reference
        ssot_owner: AGENTS.md
        update_trigger: example fixture changes
        ---

        # Canonical Leaf

        - Example canonical content.
        """,
    )
    for extra_leaf_name in extra_leaf_names or []:
        _write(
            final_dir / extra_leaf_name,
            f"""
            ---
            doc_type: reference
            ssot_owner: AGENTS.md
            update_trigger: example fixture changes
            ---

            # {extra_leaf_name}

            - Additional public leaf.
            """,
        )


def _powershell_executable() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _run_powershell_docs_check(repo_root: Path, governance_root: Path) -> subprocess.CompletedProcess[str]:
    executable = _powershell_executable()
    if executable is None:
        raise RuntimeError("PowerShell executable is required but was not found.")
    return subprocess.run(
        [
            executable,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(DOCS_SSOT_SCRIPT_PATH),
            "-RepoRoot",
            str(repo_root),
            "-GovernanceRoot",
            str(governance_root),
        ],
        capture_output=True,
        text=True,
        cwd=SCRIPT_ROOT,
        timeout=POWERSHELL_TIMEOUT_SEC,
    )


def _run_powershell_docs_check_output(repo_root: Path, governance_root: Path) -> str:
    try:
        result = _run_powershell_docs_check(repo_root, governance_root)
    except subprocess.TimeoutExpired as exc:
        output_parts: list[str] = []
        if exc.output:
            output_parts.append(str(exc.output).strip())
        if exc.stderr:
            output_parts.append(str(exc.stderr).strip())
        timeout_message = f"PowerShell docs check timed out after {POWERSHELL_TIMEOUT_SEC}s."
        if output_parts:
            timeout_message = f"{timeout_message}\n" + "\n".join(part for part in output_parts if part)
        raise AssertionError(timeout_message) from exc

    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if result.returncode == 0:
        raise AssertionError(combined_output or "Expected non-zero exit code from docs SSOT checker.")
    return combined_output


def _assert_negative_powershell_case(repo_root: Path, governance_root: Path) -> None:
    combined_output = _run_powershell_docs_check_output(repo_root, governance_root)
    if "goal.md" not in combined_output:
        raise AssertionError(combined_output or "Expected output to mention goal.md.")


class DocsRouterContractTests(unittest.TestCase):
    def test_malformed_registry_reports_explicit_error(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
            _write(
                governance_root / "scripts/entrypoint_contracts.json",
                """
                {
                  "version": 1,
                  "runtime_code": {
                    "filename_pattern": "<authority>_<entrypoint_token>.<extension>",
                    "languages": {
                      "python": {
                        "artifact_kinds": {
                          "executable": {
                            "extension": "py"
                          }
                        }
                      }
                    }
                  },
                  "docs": {
                    "public_leaf_patterns": {
                      "plain_folder_default": "<authority>.md",
                      "numbered_governance_folder": "<authority>.md",
                      "dated_evidence_folder": "evidence.md"
                    },
                    "authority_resolution": {
                      "numbered_governance_folder_regex": "^[0-9]{2}-(?P<authority>.+)$",
                      "dated_evidence_folder_regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$",
                      "dated_evidence_authority": "evidence"
                    },
                    "public_leaf_model": {
                      "minimum_public_leaf_count": 1
                    },
                    "explicit_family_exceptions": {
                      "identity_files": ["SKILL.md", "mcp.json"]
                    }
                  }
                }
                """,
            )
            _write_parent_chain(repo_root, "project/goal")
            _write(
                repo_root / "docs/project/goal/goal.md",
                """
                ---
                doc_type: reference
                ssot_owner: AGENTS.md
                update_trigger: fixture changes
                ---

                # Goal
                """,
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("docs.router_pattern" in error for error in errors), errors)

    def test_router_plus_primary_leaf_passes_for_representative_folders(self) -> None:
        fixtures = (
            ("project/goal", "goal.md"),
            ("agents/00-principles", "principles.md"),
            ("project/change-records/2026-05-08-governance-cleanup", "evidence.md"),
        )
        for rel_dir, leaf_name in fixtures:
            with self.subTest(rel_dir=rel_dir):
                with _temporary_workspace() as tmp_root:
                    repo_root = tmp_root / "repo"
                    governance_root = tmp_root / "governance"
                    _write_router_fixture(repo_root, governance_root, rel_dir, leaf_name)

                    errors, _warnings = check_docs_ssot(repo_root, governance_root)
                    self.assertEqual(errors, [], errors)

    def test_router_missing_primary_leaf_link_fails(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="missing.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("goal.md" in error for error in errors), errors)

    def test_router_link_case_mismatch_fails(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="Goal.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("goal.md" in error for error in errors), errors)

    def test_multiple_public_leafs_pass(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                extra_leaf_names=["acceptance.md"],
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertEqual(errors, [], errors)

    def test_content_bearing_router_fails(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                content_bearing_router=True,
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("routing-only" in error for error in errors), errors)

    def test_prefix_suffix_trick_does_not_satisfy_direct_child_link(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="goal-other/goal.md",
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(any("missing route" in error for error in errors), errors)

    @unittest.skipIf(_powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_matches_negative_router_contract_case(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="../goal.md",
            )
            _assert_negative_powershell_case(repo_root, governance_root)

    @unittest.skipIf(_powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_rejects_case_mismatched_router_target(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="Goal.md",
            )
            _assert_negative_powershell_case(repo_root, governance_root)

    @unittest.skipIf(_powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_reports_malformed_registry_schema_error(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
            _write(
                governance_root / "scripts/entrypoint_contracts.json",
                """
                {
                  "version": 1,
                  "runtime_code": {
                    "filename_pattern": "<authority>_<entrypoint_token>.<extension>",
                    "languages": {
                      "python": {
                        "artifact_kinds": {
                          "executable": {
                            "extension": "py"
                          }
                        }
                      }
                    }
                  },
                  "docs": {
                    "public_leaf_patterns": {
                      "plain_folder_default": "<authority>.md",
                      "numbered_governance_folder": "<authority>.md",
                      "dated_evidence_folder": "evidence.md"
                    },
                    "authority_resolution": {
                      "numbered_governance_folder_regex": "^[0-9]{2}-(?P<authority>.+)$",
                      "dated_evidence_folder_regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$",
                      "dated_evidence_authority": "evidence"
                    },
                    "public_leaf_model": {
                      "minimum_public_leaf_count": 1
                    },
                    "explicit_family_exceptions": {
                      "identity_files": ["SKILL.md", "mcp.json"]
                    }
                  }
                }
                """,
            )
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)

            combined_output = _run_powershell_docs_check_output(repo_root, governance_root)
            self.assertIn("docs.router_pattern", combined_output)

    @unittest.skipIf(_powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_timeout_reports_deterministic_failure(self) -> None:
        with _temporary_workspace() as tmp_root:
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write_router_fixture(
                repo_root,
                governance_root,
                "project/goal",
                "goal.md",
                router_target="../goal.md",
            )
            with mock.patch(
                "subprocess.run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["pwsh", "-File", str(DOCS_SSOT_SCRIPT_PATH)],
                    timeout=POWERSHELL_TIMEOUT_SEC,
                    output="partial stdout",
                    stderr="partial stderr",
                ),
            ):
                with self.assertRaisesRegex(AssertionError, r"timed out after 30s"):
                    _assert_negative_powershell_case(repo_root, governance_root)


if __name__ == "__main__":
    unittest.main()
