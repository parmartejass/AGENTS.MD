from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._docs_checks import _required_project_paths, check_docs
from scripts.check_governance_core._documents import DocumentStore, declared_doc_types, parse_markdown, router_targets
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import REPOSITORY_ROOT, docs_fixture, docs_result, write


class DocsPolicyTests(unittest.TestCase):
    def test_read_text_preserves_original_delimiters(self) -> None:
        cases = ("", "\n", "x", "x\n", "x\n\n", "x\r\ny\r\n", "x\ry", "x\u2028y", "\ufeffx\n")
        with tempfile.TemporaryDirectory() as temp:
            for index, value in enumerate(cases):
                with self.subTest(value=value):
                    path = Path(temp) / f"{index}.md"
                    write(path, value)
                    text, error = DocumentStore().read_text(path)
                    self.assertIsNone(error)
                    self.assertEqual(value, text)

    def test_every_markdown_location_has_no_line_cap(self) -> None:
        locations = ("AGENTS.md", "report.md", "guide.MD", ".hidden/untracked.md",
                     "ignored/report.md", ".governance/report.md", "docs/agents/governance/documentation/template.md")
        for relative in locations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                path = root / relative
                outcomes = []
                for count in (1, 1000):
                    write(path, "x\n" * count)
                    result = docs_result(root)
                    outcomes.append((result["status"], result["errors"]))
                self.assertEqual(outcomes[0], outcomes[1])
                if not relative.startswith("docs/"):
                    self.assertEqual("PASSED", outcomes[0][0], outcomes[0])

    def test_docs_inventory_reads_invalid_utf8_and_aliases_fail_explicitly(self) -> None:
        for kind, expected in (("utf8", "Invalid UTF-8"), ("alias", "alias")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                if kind == "utf8":
                    write(root / "docs/fixture/fixture.md", b"\xff")
                    docs_fixture(root)
                else:
                    docs_fixture(root)
                    write(root / "source.txt", "source\n")
                    os.link(root / "source.txt", root / "outside-docs.MD")
                result = docs_result(root)
                errors = result["errors"]
                self.assertEqual("FAILED", result["status"], result)
                matching = [error for error in errors if expected in error]
                self.assertEqual(1, len(matching), errors)
                if kind == "utf8":
                    self.assertEqual(matching, errors)
                    self.assertIn("fixture.md", matching[0])
                self.assertFalse(any("unexpectedly" in error for error in errors), result)

    def test_required_branches_and_optional_agency_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            policy = docs_fixture(root)
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
                policy = docs_fixture(root)
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
            docs_fixture(root, governance)
            self.assertEqual("PASSED", docs_result(root, governance)["status"])
            self.assertEqual("PASSED", docs_result(root, governance, "project_docs")["status"])
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            write(root / ".gitignore", "ignored/\n")
            write(root / "ignored/report.MD", "x\n" * 1000)
            result = docs_result(root, governance)
            self.assertEqual("PASSED", result["status"], result)
            os.link(root / "ignored/report.MD", root / "ignored/alias.md")
            result = docs_result(root, governance)
            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(any("ignored" in error and "alias" in error for error in result["errors"]), result)

    def test_policy_alias_missing_section_and_duplicate_sections_fail(self) -> None:
        for kind in ("alias", "missing", "duplicate"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy = docs_fixture(root)
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
