#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


POWERSHELL_TIMEOUT_SEC = 30
SCRIPT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SCRIPT_ROOT / "check_governance_core" / "_manifest_and_docs.py"
DOCS_SSOT_SCRIPT_PATH = SCRIPT_ROOT / "check_docs_ssot.ps1"
MIGRATED_ROUTER_MAP_PATH = SCRIPT_ROOT / "migrated_router_leaves.json"

SPEC = importlib.util.spec_from_file_location("_manifest_and_docs", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load docs-check module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_docs_ssot = MODULE.check_docs_ssot
MIGRATED_ROUTER_LEAVES = json.loads(MIGRATED_ROUTER_MAP_PATH.read_text(encoding="utf-8"))[
    "migrated_router_leaves"
]


POLICY_DOC = """
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md
update_trigger: docs governance rules change
---

# Docs SSOT Policy
"""


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


def _write_router_map(governance_root: Path) -> None:
    _write(
        governance_root / "scripts/migrated_router_leaves.json",
        MIGRATED_ROUTER_MAP_PATH.read_text(encoding="utf-8"),
    )


def _route_line(target: str, description: str) -> str:
    return f"- [{target}]({target}) - {description}. Required when: {description}."


def _write_index(path: Path, title: str, route_lines: list[str]) -> None:
    _write(
        path,
        "\n".join(
            [
                f"# {title}",
                "",
                *route_lines,
                "",
            ]
        ),
    )


def _write_parent_chain(repo_root: Path, rel_dir: str) -> None:
    parts = rel_dir.split("/")
    chain: list[str] = []
    docs_root = repo_root / "docs"
    for part in parts:
        parent_index = docs_root / "/".join(chain) / "index.md" if chain else docs_root / "index.md"
        title = "Docs Branch Index" if not chain else f"{chain[-1].title()} Branch Index"
        target = f"{part}/index.md"
        _write_index(parent_index, title, [_route_line(target, f"route into {part}")])
        chain.append(part)


def _write_router_fixture(
    repo_root: Path,
    governance_root: Path,
    rel_dir: str,
    leaf_name: str,
    *,
    router_target: str | None = None,
    content_bearing_router: bool = False,
) -> None:
    _write(
        governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
        POLICY_DOC,
    )
    _write_router_map(governance_root)
    _write_parent_chain(repo_root, rel_dir)

    final_dir = repo_root / "docs" / rel_dir
    router_lines = []
    if content_bearing_router:
        router_lines.extend(["This should not be narrative prose.", ""])
    router_lines.append(
        _route_line(
            router_target or leaf_name,
            "canonical narrative leaf",
        )
    )
    _write_index(final_dir / "index.md", f"{rel_dir.split('/')[-1].title()} Branch Index", router_lines)
    _write(
        final_dir / leaf_name,
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


def _assert_negative_powershell_case(repo_root: Path, governance_root: Path) -> None:
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
    if "goal.md" not in combined_output:
        raise AssertionError(combined_output or "Expected output to mention goal.md.")


class DocsRouterContractTests(unittest.TestCase):
    def test_router_plus_leaf_passes_for_all_migrated_folders(self) -> None:
        for rel_dir, leaf_name in sorted(MIGRATED_ROUTER_LEAVES.items()):
            with self.subTest(rel_dir=rel_dir):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_root = Path(tmp_dir)
                    repo_root = tmp_root / "repo"
                    governance_root = tmp_root / "governance"
                    _write_router_fixture(repo_root, governance_root, rel_dir, leaf_name)

                    errors, _warnings = check_docs_ssot(repo_root, governance_root)
                    self.assertEqual(errors, [], errors)

    def test_router_missing_canonical_leaf_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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
            self.assertTrue(
                any("goal.md" in error and "missing a markdown link" in error for error in errors),
                errors,
            )

    def test_content_bearing_router_fails_for_migrated_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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
            self.assertTrue(
                any("routing-only" in error for error in errors),
                errors,
            )

    def test_content_bearing_router_fails_for_unmapped_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            repo_root = tmp_root / "repo"
            governance_root = tmp_root / "governance"

            _write(
                governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
                POLICY_DOC,
            )
            _write_router_map(governance_root)
            _write_parent_chain(repo_root, "project/unmapped")
            _write(
                repo_root / "docs/project/unmapped/index.md",
                """
                ---
                doc_type: reference
                ssot_owner: AGENTS.md
                update_trigger: fixture changes
                ---

                # Unmapped Fixture

                This should have been moved into a canonical leaf doc.
                """,
            )

            errors, _warnings = check_docs_ssot(repo_root, governance_root)
            self.assertTrue(
                any("routing-only" in error for error in errors),
                errors,
            )

    def test_prefix_suffix_trick_does_not_satisfy_direct_child_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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
            self.assertTrue(
                any("goal.md" in error and "missing a markdown link" in error for error in errors),
                errors,
            )

    @unittest.skipIf(_powershell_executable() is None, "PowerShell is not available in PATH.")
    def test_powershell_checker_matches_negative_router_contract_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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
    def test_powershell_checker_timeout_reports_deterministic_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
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
