from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._test_support import REPOSITORY_ROOT, install_foundations, write
from scripts.check_governance_core.check_governance_core_main import resolve_documents, run_checks


def _policy(path: Path, declaration: str) -> None:
    write(path, "---\ndoc_type: policy\nssot_owner: fixture\nupdate_trigger: fixture changes\n"
          "---\n\n# Coding fixture\n\n" + declaration + "\n")


def _fixture(root: Path) -> tuple[dict[str, str], Path]:
    declared = install_foundations(root)
    write(root / "docs/project/architecture/architecture.md",
          "<!-- governance-core-python-root: scripts -->\n")
    source = root / "scripts/example/example_main.py"
    write(source, "VALUE = 1\n" * 7)
    return declared, root / declared["coding_principles"]


def _folder_result(root: Path, *, strict: bool = False) -> dict:
    result = run_checks({"repo_root": root, "governance_root": root,
                         "fail_on_safety_warnings": strict})
    return next(record for record in result["checks"] if record["id"] == "folder_architecture")


class CodingPolicyTests(unittest.TestCase):
    def test_owner_change_controls_warning_without_a_checker_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            _policy(policy, "code_decomposition_review_lines: 7")
            at_limit = _folder_result(root)
            self.assertEqual("PASSED", at_limit["status"], at_limit)
            self.assertEqual([], at_limit["warnings"])
            write(policy, policy.read_text(encoding="utf-8").replace(
                "code_decomposition_review_lines: 7", "code_decomposition_review_lines: 6"))
            above_limit = _folder_result(root, strict=True)
            self.assertEqual("PASSED", above_limit["status"], above_limit)
            self.assertEqual(
                ["Python file exceeds the 6-line decomposition review trigger: "
                 "scripts/example/example_main.py (7 lines)"],
                above_limit["warnings"],
            )


    def test_python_line_boundaries_preserve_splitlines_counting(self) -> None:
        cases = (
            ("", 0), ("\n", 1), ("# comment\n\nVALUE = 1", 3),
            ("# comment\n\nVALUE = 1\n", 3), ("# comment\r\n\r\nVALUE = 1\r\n", 3),
            ("# comment\n\nVALUE = 1\n# extra", 4),
            ("# comment\r\n\r\nVALUE = 1\r\n# extra\r\n", 4),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            _policy(policy, "code_decomposition_review_lines: 3")
            source = root / "scripts/example/example_main.py"
            for body, count in cases:
                with self.subTest(body=body):
                    write(source, body)
                    result = _folder_result(root)
                    self.assertEqual("PASSED", result["status"], result)
                    self.assertEqual(count > 3, bool(result["warnings"]), result)
                    if count > 3:
                        self.assertIn(f"({count} lines)", result["warnings"][0])

    def test_invalid_declarations_fail_explicitly_and_preserve_input(self) -> None:
        cases = (
            "", "code_decomposition_review_lines: nope", "code_decomposition_review_lines: 0",
            "code_decomposition_review_lines: -1", "code_decomposition_review_lines: +1",
            "code_decomposition_review_lines: 01", "code_decomposition_review_lines:1",
            "code_decomposition_review_lines: 1 ", " code_decomposition_review_lines: 1",
            "code_decomposition_review_lines = 1",
            "code_decomposition_review_lines: 1\ncode_decomposition_review_lines: 2",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            for declaration in cases:
                with self.subTest(declaration=declaration):
                    _policy(policy, declaration)
                    original = policy.read_bytes()
                    result = _folder_result(root)
                    self.assertEqual("FAILED", result["status"], result)
                    self.assertEqual(["Coding principles must declare exactly one positive "
                                      "code_decomposition_review_lines"], result["errors"])
                    self.assertEqual([], result["warnings"])
                    self.assertEqual(original, policy.read_bytes())

    def test_unsupported_integer_fails_without_a_traceback_or_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            _policy(policy, "code_decomposition_review_lines: " + "9" * 5000)
            original = policy.read_bytes()
            result = _folder_result(root)
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual(["Coding principles code_decomposition_review_lines is not a supported integer"],
                             result["errors"])
            self.assertEqual([], result["warnings"])
            self.assertEqual(original, policy.read_bytes())

    def test_examples_do_not_supply_or_duplicate_the_declaration(self) -> None:
        examples = (
            "```md\ncode_decomposition_review_lines: 1\n```\n",
            "> code_decomposition_review_lines: 1\n",
            "    code_decomposition_review_lines: 1\n",
            "\tcode_decomposition_review_lines: 1\n",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            for example in examples:
                for retain in (False, True):
                    with self.subTest(example=example, retain=retain):
                        _policy(policy, ("code_decomposition_review_lines: 7\n" if retain else "") + example)
                        result = _folder_result(root)
                        self.assertEqual("PASSED" if retain else "FAILED", result["status"], result)
                        self.assertEqual([], result["warnings"])

    def test_declared_coding_role_path_controls_the_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared, policy = _fixture(root)
            _policy(policy, "code_decomposition_review_lines: 7")
            replacement = policy.with_name("replacement.md")
            _policy(replacement, "code_decomposition_review_lines: 6")
            agents = root / declared["constitution"]
            write(agents, agents.read_text(encoding="utf-8").replace(
                "coding_principles=" + declared["coding_principles"],
                "coding_principles=" + replacement.relative_to(root).as_posix()))
            result = _folder_result(root)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(1, len(result["warnings"]), result)
            self.assertIn("6-line decomposition review trigger", result["warnings"][0])
            self.assertIn("code_decomposition_review_lines: 7", policy.read_text(encoding="utf-8"))

    def test_foundation_path_and_read_failures_reach_the_folder_check(self) -> None:
        for case in ("missing", "hardlink", "invalid_utf8", "wrong_case", "traversal", "nonregular", "read_denied"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared, policy = _fixture(root)
                _policy(policy, "code_decomposition_review_lines: 7")
                if case in {"wrong_case", "traversal"}:
                    agents = root / declared["constitution"]
                    alternative = declared["coding_principles"].upper() if case == "wrong_case" else "../outside.md"
                    write(agents, agents.read_text(encoding="utf-8").replace(
                        "coding_principles=" + declared["coding_principles"], "coding_principles=" + alternative))
                elif case == "invalid_utf8":
                    write(policy, b"\xff")
                elif case != "read_denied":
                    original = policy.read_bytes()
                    policy.unlink()
                    if case == "hardlink":
                        source = policy.with_suffix(".source")
                        write(source, original)
                        os.link(source, policy)
                    elif case == "nonregular":
                        policy.mkdir()
                original_open = Path.open

                def open_source(candidate, *args, **kwargs):
                    if case == "read_denied" and candidate == policy:
                        raise PermissionError("coding source denied")
                    return original_open(candidate, *args, **kwargs)

                with patch.object(Path, "open", open_source):
                    result = _folder_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(result["errors"], result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)
                self.assertEqual([], result["warnings"])
                expected = {"hardlink": "alias", "invalid_utf8": "Invalid UTF-8",
                            "wrong_case": "non-canonical", "traversal": "invalid non-canonical",
                            "read_denied": "coding source denied", "nonregular": "not a file",
                            "missing": "missing"}[case]
                self.assertTrue(any(expected in error for error in result["errors"]), result)

    def test_docs_project_docs_and_research_ignore_coding_declaration_validity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            shutil.copytree(REPOSITORY_ROOT / "docs", root / "docs", dirs_exist_ok=True)
            write(root / "README.md", (REPOSITORY_ROOT / "README.md").read_bytes())
            _policy(policy, "code_decomposition_review_lines: 7")
            request = {"repo_root": root, "governance_root": root}
            before = {mode: run_checks({**request, "mode": mode}) for mode in ("docs", "project_docs")}
            corpus = resolve_documents(request)
            for result in (*before.values(), corpus):
                self.assertEqual("PASSED", result["status"], result)
            _policy(policy, "code_decomposition_review_lines: invalid")
            for mode, result in before.items():
                self.assertEqual(result, run_checks({**request, "mode": mode}))
            self.assertEqual(corpus, resolve_documents(request))
            self.assertEqual("FAILED", _folder_result(root)["status"])

    def test_policy_value_is_not_a_new_public_request_override(self) -> None:
        request = {"code_decomposition_review_lines": 6}
        original = dict(request)
        result = run_checks(request)
        self.assertEqual("FAILED_VALIDATION", result["status"], result)
        self.assertEqual([], result["checks"])
        self.assertIn("unsupported request key(s)", result["errors"][0])
        self.assertEqual(original, request)


if __name__ == "__main__":
    unittest.main()
