from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._docs_checks import _physical_lines, _required_project_paths, check_docs
from scripts.check_governance_core._documents import DocumentStore, declared_doc_types, parse_markdown, router_targets
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import REPOSITORY_ROOT, docs_fixture, docs_result, write


class DocsPolicyTests(unittest.TestCase):
    def test_physical_lf_records_preserve_original_delimiters(self) -> None:
        cases = {"": 0, "\n": 1, "x": 1, "x\n": 1, "x\n\n": 2,
                 "x\r\ny\r\n": 2, "x\ry": 1, "x\u2028y": 1, "\ufeffx\n": 1}
        with tempfile.TemporaryDirectory() as temp:
            for index, (value, expected) in enumerate(cases.items()):
                with self.subTest(value=value):
                    path = Path(temp) / f"{index}.md"
                    write(path, value)
                    text, error = DocumentStore().read_text(path)
                    self.assertIsNone(error)
                    self.assertEqual(value, text)
                    self.assertEqual(expected, _physical_lines(text))

    def test_every_markdown_location_obeys_the_owner_boundary(self) -> None:
        locations = ("AGENTS.md", "report.md", "guide.MD", ".hidden/untracked.md",
                     "ignored/report.md", ".governance/report.md", "docs/agents/governance/documentation/template.md")
        for relative in locations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _policy, limit = docs_fixture(root)
                path = root / relative
                for ending in ("\n", ""):
                    for count in (limit, limit + 1):
                        write(path, "x\n" * (count - 1) + "x" + ending)
                        result = docs_result(root)
                        size_errors = [error for error in result["errors"] if "documentation exceeds" in error]
                        self.assertEqual(count > limit, bool(size_errors), result)
                        if count > limit:
                            self.assertTrue(any(str(path) in error for error in size_errors), result)

    def test_docs_inventory_reads_invalid_utf8_and_aliases_fail_explicitly(self) -> None:
        for kind in ("utf8", "alias"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                path = root / "outside-docs.MD"
                if kind == "utf8":
                    write(path, b"\xff")
                else:
                    write(root / "source.txt", "source\n")
                    os.link(root / "source.txt", path)
                result = docs_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("Invalid UTF-8" in error if kind == "utf8" else "alias" in error for error in result["errors"]), result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_missing_malformed_duplicate_and_nonpositive_limits_fail(self) -> None:
        for replacement in ("", "documentation_line_limit: nope", "documentation_line_limit: 0",
                            "documentation_line_limit: -1", "documentation_line_limit: 1\ndocumentation_line_limit: 2"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                write(policy, re.sub(r"(?m)^documentation_line_limit: .+$", replacement, policy.read_text(encoding="utf-8")))
                result = docs_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("exactly one positive documentation_line_limit" in error for error in result["errors"]), result)

    def test_owner_changes_control_acceptance_without_a_checker_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            policy, limit = docs_fixture(root)
            write(root / "report.md", "x\n" * (limit + 1))
            self.assertEqual("FAILED", docs_result(root)["status"])
            write(policy, policy.read_text(encoding="utf-8").replace(f"documentation_line_limit: {limit}", f"documentation_line_limit: {limit + 1}"))
            self.assertEqual("PASSED", docs_result(root)["status"])

    def test_required_branches_and_optional_agency_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            policy, _limit = docs_fixture(root)
            agents = root / "AGENTS.md"
            write(agents, agents.read_text(encoding="utf-8") + "\n## Documentation SSOT Policy (Hard Gate)\n- `docs/project/unrequested/unrequested.md`\n")
            self.assertEqual("PASSED", docs_result(root, mode="project_docs")["status"])
            required, errors = _required_project_paths(parse_markdown(policy.read_text(encoding="utf-8")))
            self.assertEqual([], errors)
            for relative in required[:3]:
                target = root / relative
                saved = target.read_bytes()
                target.unlink()
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any(relative in error for error in result["errors"]), result)
                write(target, saved)

    def test_invalid_required_branch_declarations_fail_without_tracebacks(self) -> None:
        cases = ("- `../escape/`: unsafe", "- `nested/child/`: unsafe", "- `bad\\name/`: unsafe",
                 "- `repeat/`: first\n- `repeat/`: duplicate", "- missing/: malformed", "")
        for body in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                value = policy.read_text(encoding="utf-8")
                value = re.sub(r"(?ms)^## Required project-doc branches\n.*?(?=^## )", "## Required project-doc branches\n" + body + "\n\n", value)
                write(policy, value)
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("Docs policy" in error for error in result["errors"]), result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_vendored_docs_mode_and_ignored_untracked_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance = root / ".governance"
            _policy, limit = docs_fixture(root, governance)
            self.assertEqual("PASSED", docs_result(root, governance)["status"])
            self.assertEqual("PASSED", docs_result(root, governance, "project_docs")["status"])
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            write(root / ".gitignore", "ignored/\n")
            write(root / "ignored/report.MD", "x\n" * (limit + 1))
            result = docs_result(root, governance)
            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(any("ignored" in error and "documentation exceeds" in error for error in result["errors"]), result)

    def test_policy_alias_missing_section_and_duplicate_sections_fail(self) -> None:
        for kind in ("alias", "missing", "duplicate"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                if kind == "alias":
                    source = policy.with_suffix(".source")
                    policy.replace(source)
                    os.link(source, policy)
                else:
                    text = policy.read_text(encoding="utf-8")
                    text = text.replace("## Required project-doc branches", "## Other") if kind == "missing" else text + "\n## Required project-doc branches\n- `another/`: duplicate section\n"
                    write(policy, text)
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_project_docs_rejects_readme_alias_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs_fixture(root)
            readme = root / "README.md"
            source = root / "README.md.source"
            readme.replace(source)
            os.link(source, readme)
            result = docs_result(root, mode="project_docs")
            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(any("README.md" in error and "must not be an alias" in error for error in result["errors"]), result)

    def test_docs_mode_preloads_repository_markdown_without_reading_python(self) -> None:
        root = REPOSITORY_ROOT
        seen: list[Path] = []
        original = RepositoryInventory.tree_entries

        def record(inventory: RepositoryInventory, scan_root: Path):
            seen.append(scan_root.resolve())
            return original(inventory, scan_root)

        with patch.object(RepositoryInventory, "tree_entries", new=record), patch.object(
            RepositoryInventory, "python_files", side_effect=AssertionError("docs must not read Python")
        ):
            result = docs_result(root)
        self.assertEqual("PASSED", result["status"], result)
        self.assertIn(root.resolve(), seen)
        self.assertIn((root / "docs").resolve(), seen)

    def test_report_reconciles_the_selected_work_universe(self) -> None:
        result = docs_result(REPOSITORY_ROOT)
        self.assertEqual(["docs"], result["planned"])
        self.assertEqual(result["planned"], result["eligible"])
        self.assertEqual(result["planned"], result["executed"])
        self.assertEqual([], result["skipped"])
        self.assertEqual([], result["failed"])

    def test_router_target_and_doc_type_contract_helpers_reject_invalid_values(self) -> None:
        router = parse_markdown("# Router\n\n- [ghost](ghost.md) - route. Required when: needed.\n")
        targets, errors = router_targets(router)
        self.assertEqual(["ghost.md"], targets)
        self.assertEqual([], errors)
        policy = "doc_type: policy|reference|runbook|playbook|decision|generated\n"
        self.assertNotIn("nonsense", declared_doc_types(policy))

    def test_docs_check_rejects_dead_router_target_and_invalid_doc_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs_fixture(root)
            write(root / "docs/docs_index.md", "# Docs\n\n- [docs](docs.md) - docs. Required when: reading docs.\n- [ghost](ghost.md) - ghost. Required when: reading ghost.\n")
            write(root / "docs/docs.md", "---\ndoc_type: nonsense\nssot_owner: owner\nupdate_trigger: changes\n---\n\n# Docs\n")
            errors, _warnings = check_docs(root, root, DocumentStore(), RepositoryInventory(root))
            self.assertTrue(any("ghost.md" in error for error in errors), errors)
            self.assertTrue(any("unsupported doc_type" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
