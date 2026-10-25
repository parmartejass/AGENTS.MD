from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._docs_checks import _physical_lines, _required_project_paths, check_docs
from scripts.check_governance_core._documents import DocumentStore, declared_doc_types, parse_markdown, router_targets
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._repeat_report import DOCS_OWNER
from scripts.check_governance_core._test_support import REPOSITORY_ROOT, docs_fixture, docs_result, repeat_skipped, write


_RULE = "Every agent must keep each plan in the scratchpad folder."
_OWNER = "(documentation owner, Validation boundary)"


def _tracked_docs(root: Path, files: dict[str, str]) -> dict:
    """Install the docs fixture plus ``files``, track everything in Git, and run docs mode."""

    docs_fixture(root)
    for relative, text in files.items():
        write(root / relative, text)
    for command in (["git", "init"], ["git", "add", "-A"]):
        subprocess.run(command, cwd=root, check=True, capture_output=True, timeout=10)
    return docs_result(root)


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

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_warns_on_a_normative_sentence_in_two_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = _tracked_docs(Path(temp), {"one.md": f"# One\n\n{_RULE}\n", "two.md": f"Intro text. {_RULE}\n"})
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual([f"repeat: one.md:3 and two.md:1 share 100% of their 5-word phrases {_OWNER}"],
                             result["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_skips_distinct_short_and_excluded_sentences(self) -> None:
        route = f"- [rules.md](rules.md) - {_RULE} Required when: testing.\n"
        files = {
            "one.md": f"{_RULE}\nAgents must stop.\nThe plan stays in the scratchpad folder today.\n",
            "two.md": "Agents must never delete the shared archive folder.\nAgents must stop.\n"
                      "The plan stays in the scratchpad folder today.\n",
            "three.md": f"---\nnote: {_RULE}\n---\n```\n{_RULE}\n```\n> {_RULE}\n",
            "docs/project/changelog/changelog.md": "---\ndoc_type: reference\nssot_owner: fixture\nupdate_trigger: fixture "
                                                   f"changes\n---\n\n# Changelog\n\n{_RULE}\n",
            "docs/project/rules/rules_index.md": "# Rules\n\n" + route,
        }
        with tempfile.TemporaryDirectory() as temp:
            result = _tracked_docs(Path(temp), files)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual([], result["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_warns_on_a_declaration_in_two_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            files = {"one.md": "sample_key: 1\n  indented_key: 1\n", "two.md": "# Two\nsample_key: 2\n  indented_key: 2\n"}
            result = _tracked_docs(Path(temp), files)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual([f"repeat: declaration sample_key in one.md:1 and two.md:2 {_OWNER}"], result["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_orders_findings_by_file_then_line(self) -> None:
        files = {"c.md": f"{_RULE}\n", "b.md": f"# B\n\n{_RULE}\n", "a.md": f"# A\n{_RULE}\n"}
        expected = [f"repeat: {first} and {second} share 100% of their 5-word phrases {_OWNER}"
                    for first, second in (("a.md:2", "b.md:3"), ("a.md:2", "c.md:1"), ("b.md:3", "c.md:1"))]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(expected, _tracked_docs(root, files)["warnings"])
            self.assertEqual(expected, docs_result(root)["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_reads_fences_through_the_markdown_owner(self) -> None:
        hit = f"repeat: one.md:{{}} and two.md:1 share 100% of their 5-word phrases {_OWNER}"
        cases = {
            "nested shorter fence stays inside": (f"````md\n```\n{_RULE}\n````\n\n{_RULE}\n", [hit.format(6)]),
            "longer closing fence closes": (f"```\n{_RULE}\n`````\n\n{_RULE}\n", [hit.format(5)]),
            "shorter fence inside a longer one stays inside": (f"`````\n````\n{_RULE}\n`````\n", []),
            "backticks do not close a tilde fence": (f"~~~\n```\n{_RULE}\n~~~\n", []),
            "tildes do not close a backtick fence": (f"```\n~~~\n{_RULE}\n```\n", []),
            "a fence line with an info string does not close": (f"```\n```python\n{_RULE}\n```\n", []),
            "indented code is not operative": (f"Intro.\n\n    {_RULE}\n", []),
        }
        for name, (text, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                result = _tracked_docs(Path(temp), {"one.md": text, "two.md": f"{_RULE}\n"})
                self.assertEqual("PASSED", result["status"], result)
                self.assertEqual(expected, result["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repeat_report_joins_wrapped_sentences_and_keeps_their_first_line(self) -> None:
        cases = {
            "Every agent must\nkeep each plan in the scratchpad folder.\n": 1,
            "Intro text here. Every agent must keep\neach plan in the scratchpad folder.\n": 1,
            "Intro text here.\nEvery agent must keep each\nplan in the scratchpad folder.\n": 2,
            "- First item.\n- Every agent must keep each plan\n  in the scratchpad folder.\n": 2,
        }
        for text, line in cases.items():
            with self.subTest(text=text), tempfile.TemporaryDirectory() as temp:
                result = _tracked_docs(Path(temp), {"one.md": text, "two.md": f"{_RULE}\n"})
                self.assertEqual([f"repeat: one.md:{line} and two.md:1 share 100% of their 5-word phrases {_OWNER}"],
                                 result["warnings"])

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_list_items_and_headings_stay_separate_statements(self) -> None:
        text = "# Every agent must keep\n- each plan in the\n- scratchpad folder.\n"
        with tempfile.TemporaryDirectory() as temp:
            result = _tracked_docs(Path(temp), {"one.md": text, "two.md": f"{_RULE}\n"})
            self.assertEqual([], result["warnings"])

    def test_repeat_report_skips_with_reason_outside_a_git_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs_fixture(root)
            write(root / "one.md", f"{_RULE}\n")
            write(root / "two.md", f"{_RULE}\n")
            result = docs_result(root)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(repeat_skipped(root, DOCS_OWNER), result["warnings"])

    def test_missing_or_malformed_repeat_parameters_fail_explicitly(self) -> None:
        terms = "exactly one normative_repeat_terms list"
        cases = {
            "normative_repeat_terms": (("", terms), ("normative_repeat_terms: must||never", terms),
                                       ("normative_repeat_terms: must|Must", terms), ("normative_repeat_terms:", terms),
                                       ("normative_repeat_terms: must\nnormative_repeat_terms: never", terms)),
            "normative_repeat_shingle_words": tuple(
                (value, "exactly one positive normative_repeat_shingle_words")
                for value in ("", "normative_repeat_shingle_words: 0", "normative_repeat_shingle_words: five")),
            "normative_repeat_min_percent": tuple(
                (value, "exactly one positive normative_repeat_min_percent")
                for value in ("", "normative_repeat_min_percent: -1", "normative_repeat_min_percent: 6 0")),
            "normative_repeat_excluded_branches": tuple(
                (value, "exactly one normative_repeat_excluded_branches list")
                for value in ("", "normative_repeat_excluded_branches:", "normative_repeat_excluded_branches: history",
                              "normative_repeat_excluded_branches: changelog|changelog",
                              "normative_repeat_excluded_branches: changelog||goal")),
        }
        for key, replacements in cases.items():
            for replacement, expected in replacements:
                with self.subTest(key=key, replacement=replacement), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    policy, _limit = docs_fixture(root)
                    write(policy, re.sub(rf"(?m)^{key}: .+$", replacement, policy.read_text(encoding="utf-8")))
                    result = docs_result(root)
                    self.assertEqual("FAILED", result["status"], result)
                    self.assertTrue(any(expected in error for error in result["errors"]), result)
                    self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)


if __name__ == "__main__":
    unittest.main()
