from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._folder_architecture import check_folder_architecture
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import install_foundations, write
from scripts.check_governance_core import run_checks


_write = write
ARCHITECTURE = "docs/project/architecture/architecture.md"
ENTRY = "__all__ = [\"main\", \"run\"]\n\nfrom scripts.pkg._impl import run\n\n\ndef main(argv):\n    return run(argv)\n"
LAUNCHER = "import sys\n\nfrom scripts.pkg import main\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main(sys.argv[1:]))\n"


def _policy(path: Path, declaration: str) -> None:
    write(path, "---\ndoc_type: policy\nssot_owner: fixture\nupdate_trigger: fixture changes\n"
          "---\n\n# Coding fixture\n\n" + declaration + "\n")


def _fixture(root: Path, markers: str = "<!-- governance-core-python-root: scripts -->\n") -> tuple[dict[str, str], Path]:
    declared = install_foundations(root)
    write(root / ARCHITECTURE, markers)
    write(root / "scripts/example/__init__.py", "__all__ = []\n")
    _policy(root / declared["coding_principles"], "code_decomposition_review_lines: 400")
    return declared, root / declared["coding_principles"]


def _folder_result(root: Path, *, strict: bool = False) -> dict:
    result = run_checks({"repo_root": root, "governance_root": root, "fail_on_safety_warnings": strict})
    return next(record for record in result["checks"] if record["id"] == "folder_architecture")


def _conformant_package(root: Path) -> None:
    write(root / "scripts/pkg/__init__.py", ENTRY)
    write(root / "scripts/pkg/__main__.py", LAUNCHER)
    write(root / "scripts/pkg/_impl.py", "from scripts.check_governance_core import run_checks\n\n\ndef run(argv):\n    return 0\n")
    write(root / "scripts/pkg/test_impl.py", "from scripts.pkg._impl import run\n")


class PackageStructureTests(unittest.TestCase):
    def test_native_package_entry_is_required_below_declared_roots(self) -> None:
        cases = {
            "scripts/reporting/helper.py": "missing its native public entrypoint: scripts/reporting/__init__.py",
            "scripts/group/sub/__init__.py": "missing its native public entrypoint: scripts/group/__init__.py",
            "scripts/tool.py": "inside a package below its declared source root: scripts/tool.py",
            "scripts/__init__.py": "must contain packages, not be one: scripts/__init__.py",
        }
        for relative, expected in cases.items():
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _declared, policy = _fixture(root)
                _policy(policy, "code_decomposition_review_lines: 400")
                write(root / relative, "VALUE = 1\n")
                result = _folder_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any(expected in error for error in result["errors"]), result)

    def test_nested_packages_pass_and_hidden_or_cache_folders_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _declared, policy = _fixture(root)
            _policy(policy, "code_decomposition_review_lines: 400")
            for relative, body in (("scripts/example/child/__init__.py", "__all__ = []\n"),
                                   ("scripts/example/child/_worker.py", "VALUE = 1\n"),
                                   ("scripts/example/.cache/tool.py", "VALUE = 1\n"),
                                   ("scripts/example/__pycache__/stale.py", "VALUE = 1\n")):
                write(root / relative, body)
            result = _folder_result(root)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual([], result["warnings"])


class OwnerDeclaredRootTests(unittest.TestCase):
    def test_example_markers_cannot_authorize_python_roots(self) -> None:
        examples = (
            "```md\n<!-- governance-core-python-root: rogue -->\n```\n",
            "> <!-- governance-core-python-root: rogue -->\n",
            "    <!-- governance-core-python-root: rogue -->\n",
        )
        for example in examples:
            with self.subTest(example=example), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = install_foundations(root)
                _write(
                    root / "docs/project/architecture/architecture.md",
                    "<!-- governance-core-python-root: scripts -->\n" + example,
                )
                _write(root / "scripts/example/__init__.py", "__all__ = []\n")
                _write(root / "rogue/bypass.py", "VALUE = 1\n")
                errors, _warnings = check_folder_architecture(
                    root,
                    root,
                    DocumentStore(),
                    RepositoryInventory(root),
                    coding_policy_path=root / declared["coding_principles"],
                )
                self.assertTrue(any("rogue/bypass.py" in error for error in errors), errors)

    def test_python_root_markers_require_exact_case(self) -> None:
        for marker in ("Scripts", "x-bookmarks import"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = install_foundations(root)
                _write(
                    root / "docs/project/architecture/architecture.md",
                    f"<!-- governance-core-python-root: {marker} -->\n",
                )
                _write(root / "scripts/example/__init__.py", "__all__ = []\n")
                _write(root / "X-Bookmarks Import/fetch.py", "VALUE = 1\n")
                errors, _warnings = check_folder_architecture(
                    root,
                    root,
                    DocumentStore(),
                    RepositoryInventory(root),
                    coding_policy_path=root / declared["coding_principles"],
                )
                self.assertTrue(any("non-canonical" in error for error in errors), errors)

    def test_folder_architecture_uses_exact_owner_declared_python_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = install_foundations(root)
            _write(
                root / "docs/project/architecture/architecture.md",
                "<!-- governance-core-python-root: scripts -->\n"
                "<!-- governance-core-python-root: X-Bookmarks Import -->\n"
                "<!-- governance-core-python-package-exception: X-Bookmarks Import -->\n",
            )
            _write(root / "scripts/example/__init__.py", "__all__ = []\n")
            allowed = root / "X-Bookmarks Import/fetch.py"
            outside = root / "outside.py"
            similar = root / "X-Bookmarks Import-copy/fetch.py"
            _write(allowed, "VALUE = 1\n")
            _write(outside, "VALUE = 1\n")
            _write(similar, "VALUE = 1\n")

            errors, warnings = check_folder_architecture(
                root,
                root,
                DocumentStore(),
                RepositoryInventory(root),
                coding_policy_path=root / declared["coding_principles"],
            )

        self.assertTrue(any("outside.py" in error for error in errors), errors)
        self.assertTrue(any("X-Bookmarks Import-copy/fetch.py" in error for error in errors), errors)
        self.assertFalse(any("X-Bookmarks Import/fetch.py" in error for error in errors), errors)
        self.assertEqual(1, sum("declared packaged-folder exception" in warning
                                and warning.endswith(": X-Bookmarks Import") for warning in warnings), warnings)

    def test_packaged_folder_exceptions_must_name_declared_roots_once(self) -> None:
        cases = {
            "undeclared": "<!-- governance-core-python-package-exception: elsewhere -->\n",
            "duplicate": "<!-- governance-core-python-package-exception: scripts -->\n" * 2,
            "malformed": "<!-- governance-core-python-package-exception: -->\n",
        }
        for name, marker in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = install_foundations(root)
                _write(root / "docs/project/architecture/architecture.md",
                       "<!-- governance-core-python-root: scripts -->\n" + marker)
                _write(root / "scripts/example/__init__.py", "__all__ = []\n")
                errors, _warnings = check_folder_architecture(
                    root, root, DocumentStore(), RepositoryInventory(root),
                    coding_policy_path=root / declared["coding_principles"],
                )
                self.assertTrue(any("packaged-folder exception" in error for error in errors), errors)

    def test_nested_declared_roots_are_rejected_in_either_order(self) -> None:
        for order in (("scripts", "scripts/example"), ("scripts/example", "scripts")):
            with self.subTest(order=order), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root, "".join(f"<!-- governance-core-python-root: {value} -->\n" for value in order))
                result = _folder_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual(
                    ["Declared governance-core Python roots must not nest: 'scripts/example' is inside 'scripts'"],
                    [error for error in result["errors"] if "must not nest" in error],
                )

    def test_vendored_host_roots_resolve_against_each_record(self) -> None:
        cases = {
            "declared": ("<!-- governance-core-python-root: app -->\n", True, None),
            "python_free_host": ("", False, None),
            "pack_root_redeclared": (
                "<!-- governance-core-python-root: .governance/scripts -->\n<!-- governance-core-python-root: app -->\n",
                True, "'.governance/scripts' in {host} lies inside the governance root; its owner is {pack}",
            ),
            "outside_host_roots": ("", True, "outside the Python source roots declared in {host}: app/feature/__init__.py"),
            "missing_host_record": (None, False, "Missing required file: {host}"),
            "nested_across_records": (
                "<!-- governance-core-python-root: vendor -->\n", False,
                "must not nest: 'vendor/.governance/scripts' is inside 'vendor'",
            ),
        }
        for name, (markers, host_python, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                repo = Path(temp)
                governance = repo / ("vendor/.governance" if name == "nested_across_records" else ".governance")
                install_foundations(governance)
                write(governance / ARCHITECTURE, "<!-- governance-core-python-root: scripts -->\n")
                write(governance / "scripts/pack/__init__.py", "__all__ = []\n")
                if markers is not None:
                    write(repo / ARCHITECTURE, markers)
                if host_python:
                    write(repo / "app/feature/__init__.py", "__all__ = []\n")
                result = run_checks({"repo_root": repo, "governance_root": governance})
                record = next(item for item in result["checks"] if item["id"] == "folder_architecture")
                if expected is None:
                    self.assertEqual("PASSED", record["status"], record)
                    self.assertEqual([], record["warnings"])
                    continue
                message = expected.format(host=repo / ARCHITECTURE, pack=governance / ARCHITECTURE)
                self.assertEqual("FAILED", record["status"], record)
                self.assertEqual(1, sum(message in error for error in record["errors"]), (message, record))
                self.assertFalse(any("unexpectedly" in error for error in record["errors"]), record)

    def test_coinciding_roots_read_one_record_once_without_duplicate_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared, _policy = _fixture(root, "<!-- governance-core-python-root: scripts -->\n"
                                                "<!-- governance-core-python-root: lab -->\n"
                                                "<!-- governance-core-python-package-exception: lab -->\n")
            write(root / "lab/tool.py", "VALUE = 1\n")
            store = DocumentStore()
            reads: list[Path] = []
            original = store.markdown

            def counted(path: Path):
                reads.append(path)
                return original(path)

            with patch.object(store, "markdown", new=counted):
                errors, warnings = check_folder_architecture(
                    root, root, store, RepositoryInventory(root),
                    coding_policy_path=root / declared["coding_principles"],
                )
            self.assertEqual([], errors)
            self.assertEqual(1, len(warnings), warnings)
            self.assertEqual(1, reads.count(root / ARCHITECTURE), reads)


class PackageInterfaceTests(unittest.TestCase):
    def test_conformant_package_passes_every_interface_witness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fixture(root)
            _conformant_package(root)
            result = _folder_result(root)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual([], result["warnings"])

    def test_interface_defects_fail_with_one_explicit_error_each(self) -> None:
        cases = {
            "public_module": ("scripts/pkg/helper.py", "VALUE = 1\n", "must be a private `_` module or a `test*` module"),
            "missing_all": ("scripts/pkg/__init__.py", "from scripts.pkg._impl import run\n", "declare `__all__` exactly once"),
            "duplicate_all": ("scripts/pkg/__init__.py", "__all__ = []\n__all__ = []\n", "declare `__all__` exactly once"),
            "non_string_all": ("scripts/pkg/__init__.py", "__all__ = [1]\n", "non-empty string literals"),
            "repeated_member": ("scripts/pkg/__init__.py", "__all__ = [\"run\", \"run\"]\nfrom scripts.pkg._impl import run\n", "must not repeat"),
            "unbound_member": ("scripts/pkg/__init__.py", "__all__ = [\"run\", \"ghost\"]\nfrom scripts.pkg._impl import run\n", "unbound member 'ghost'"),
            "leaked_name": ("scripts/pkg/__init__.py", "__all__ = [\"run\"]\nimport sys\nfrom scripts.pkg._impl import run\n", "binds public name 'sys' outside `__all__`"),
            "launcher_logic": ("scripts/pkg/__main__.py", "from scripts.pkg import main\nimport sys\nVALUE = 1\nif __name__ == \"__main__\":\n    raise SystemExit(main(sys.argv[1:]))\n", "must only import and delegate"),
            "launcher_private": ("scripts/pkg/__main__.py", "import sys\nfrom scripts.pkg._impl import run\nif __name__ == \"__main__\":\n    raise SystemExit(run(sys.argv[1:]))\n", "must only import and delegate"),
            "launcher_unguarded": ("scripts/pkg/__main__.py", "import sys\nfrom scripts.pkg import main\nmain(sys.argv[1:])\n", "must only import and delegate"),
            "deep_absolute": ("scripts/example/_other.py", "from scripts.pkg._impl import run\n", "Deep import of private module scripts.pkg._impl from outside its package: scripts/example/_other.py:1"),
            "deep_from_package": ("scripts/example/_other.py", "from scripts.pkg import _impl\n", "Deep import of private module scripts.pkg._impl"),
            "deep_relative_parent": ("scripts/pkg/child/__init__.py", "__all__ = []\nfrom .._impl import run\n", "Deep import of private module"),
            "syntax_error": ("scripts/pkg/_broken.py", "def (\n", "cannot be parsed for packaged-folder witnesses"),
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fixture(root)
            _conformant_package(root)
            self.assertEqual("PASSED", _folder_result(root)["status"])
            for name, (relative, body, expected) in cases.items():
                with self.subTest(name=name):
                    original = (root / relative).read_bytes() if (root / relative).exists() else None
                    write(root / relative, body)
                    result = _folder_result(root)
                    if original is None:
                        (root / relative).unlink()
                    else:
                        write(root / relative, original)
                    self.assertEqual("FAILED", result["status"], result)
                    matching = [error for error in result["errors"] if expected in error]
                    self.assertEqual(1, len(matching), (expected, result["errors"]))
                    self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)
            self.assertEqual("PASSED", _folder_result(root)["status"])

    def test_launcher_forms_and_same_package_private_imports_are_accepted(self) -> None:
        launchers = (
            "from scripts.pkg import main\nimport sys\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n",
            "\"\"\"Launcher.\"\"\"\nfrom . import main\nif __name__ == \"__main__\":\n    main([])\n",
        )
        for launcher in launchers:
            with self.subTest(launcher=launcher[:30]), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                _conformant_package(root)
                write(root / "scripts/pkg/__main__.py", launcher)
                write(root / "scripts/pkg/_more.py", "from scripts.pkg import _impl\nfrom ._impl import run\nfrom . import _impl as again\n")
                result = _folder_result(root)
                self.assertEqual("PASSED", result["status"], result)

    def test_exception_roots_skip_interface_witnesses(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fixture(root, "<!-- governance-core-python-root: scripts -->\n<!-- governance-core-python-root: lab -->\n"
                           "<!-- governance-core-python-package-exception: lab -->\n")
            write(root / "lab/tool.py", "from scripts.example import _nothing\n")
            result = _folder_result(root)
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(1, len(result["warnings"]), result)


if __name__ == "__main__":
    unittest.main()
