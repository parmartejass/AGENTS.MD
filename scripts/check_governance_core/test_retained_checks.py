from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._docs_checks import check_docs
from scripts.check_governance_core._folder_architecture import check_folder_architecture
from scripts.check_governance_core._inventory import RepositoryInventory, _is_directory_alias
from scripts.check_governance_core import _git_capture, _inventory
from scripts.check_governance_core._python_safety import check_python_safety
from scripts.check_governance_core._repository_checks import check_repository
from scripts.check_governance_core.check_governance_core_main import run_checks


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(value)


class RetainedCheckTests(unittest.TestCase):
    def test_folder_architecture_requires_one_feature_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(root / "scripts/reporting/helper.py", "VALUE = 1\n")
            errors, warnings = check_folder_architecture(root, DocumentStore(), RepositoryInventory(root))
            self.assertEqual([], warnings)
            self.assertTrue(any("reporting_main.py" in error for error in errors), errors)

    def test_python_safety_retains_error_and_warning_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(
                root / "unsafe.py",
                "import subprocess\nprint('x')\nsubprocess.run(['x'])\n",
            )
            errors, warnings = check_python_safety(root, RepositoryInventory(root), fail_on_warnings=False)
            self.assertEqual([], warnings)
            self.assertTrue(any("PRINT_CALL" in error for error in errors), errors)
            self.assertTrue(any("SUBPROCESS_TIMEOUT" in error for error in errors), errors)

    def test_python_safety_strict_mode_promotes_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(root / "warning.py", "from pathlib import Path\nPath('x').write_text('unsafe')\n")
            errors, warnings = check_python_safety(root, RepositoryInventory(root), fail_on_warnings=True)
            self.assertTrue(any("NON_ATOMIC_WRITE" in warning for warning in warnings), warnings)
            self.assertTrue(any(error.startswith("strict warning:") for error in errors), errors)

    def test_unreviewed_popen_remains_a_strict_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(root / "warning.py", "import subprocess\nsubprocess.Popen(['x'])\n")
            errors, warnings = check_python_safety(root, RepositoryInventory(root), fail_on_warnings=True)
            self.assertTrue(any("SUBPROCESS_POPEN" in warning for warning in warnings), warnings)
            self.assertTrue(any(error.startswith("strict warning:") for error in errors), errors)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_python_safety_scans_untracked_files_in_git_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            _write(root / "untracked.py", "print('unsafe')\n")
            errors, _warnings = check_python_safety(root, RepositoryInventory(root), fail_on_warnings=False)
            self.assertTrue(any("PRINT_CALL" in error for error in errors), errors)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_public_api_rejects_governance_root_outside_repository(self) -> None:
        governance_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, timeout=10)
            _write(repo_root / "unsafe.py", "print('unsafe target')\n")
            _write(repo_root / "README.md", "# Test\n")
            result = run_checks({"repo_root": str(repo_root), "governance_root": str(governance_root)})
            self.assertEqual("FAILED_VALIDATION", result["status"], result)
            self.assertEqual([], result["checks"])
            self.assertTrue(any("outside the declared repository" in error for error in result["errors"]), result)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_unicode_tracked_secret_path_is_not_hidden_by_git_quoting(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            secret = root / "é/.env"
            _write(secret, "TOKEN=example\n")
            subprocess.run(["git", "add", secret.relative_to(root).as_posix()], cwd=root, check=True, capture_output=True, timeout=10)
            errors = check_repository(root, DocumentStore(), RepositoryInventory(root))
            self.assertTrue(any("Tracked secret-like file" in error for error in errors), errors)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_git_inventory_stops_at_the_output_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            _write(root / "tracked.txt", "x\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True, timeout=10)
            with patch.object(_git_capture, "MAX_STDOUT_BYTES", 1):
                paths, error = RepositoryInventory(root).tracked_paths(root)
            self.assertEqual((), paths)
            self.assertIn("exceeded", error or "")

    def test_git_inventory_reports_process_start_failure(self) -> None:
        with patch.object(_git_capture.subprocess, "Popen", side_effect=OSError("process denied")):
            paths, error = RepositoryInventory._git_paths(
                Path("."), ["ls-files", "-z"], "tracked files"
            )

        self.assertEqual((), paths)
        self.assertIn("process denied", error or "")

    def test_bounded_capture_preserves_primary_and_cleanup_failures(self) -> None:
        class Process:
            def __init__(self) -> None:
                self.stdout = io.BytesIO(b"overflow")
                self.stderr = io.BytesIO()
                self.returncode = None

            def poll(self) -> None:
                return None

            def kill(self) -> None:
                raise OSError("kill denied")

            def wait(self, *, timeout: float) -> None:
                raise subprocess.TimeoutExpired("git", timeout)

        with patch.object(_git_capture, "MAX_STDOUT_BYTES", 1), patch.object(
            _git_capture.subprocess, "Popen", return_value=Process()
        ):
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )

        self.assertIn("stdout exceeded 1 bytes", error or "")
        self.assertIn("cleanup also failed", error or "")
        self.assertIn("kill denied", error or "")
        self.assertIn("reap failed", error or "")

    def test_bounded_capture_closes_pipes_after_partial_reader_start_failure(self) -> None:
        class Pipe(io.BytesIO):
            pass

        class Process:
            def __init__(self) -> None:
                self.stdout = Pipe()
                self.stderr = Pipe()
                self.returncode = None

            def poll(self) -> int | None:
                return self.returncode

            def kill(self) -> None:
                self.returncode = -9

            def wait(self, *, timeout: float) -> int:
                self.returncode = -9
                return self.returncode

        real_thread = _git_capture.threading.Thread
        starts = 0

        class PartialStartThread(real_thread):
            def start(self) -> None:
                nonlocal starts
                starts += 1
                if starts == 2:
                    raise RuntimeError("thread unavailable")
                super().start()

        process = Process()
        with patch.object(_git_capture.subprocess, "Popen", return_value=process), patch.object(
            _git_capture.threading, "Thread", PartialStartThread
        ):
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )

        self.assertIn("thread unavailable", error or "")
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_git_inventory_real_subprocess_is_reaped_after_normal_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            _write(root / "tracked.txt", "x\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True, timeout=10)
            paths, error = RepositoryInventory._git_paths(
                root, ["ls-files", "-z"], "tracked files"
            )

        self.assertIsNone(error)
        self.assertEqual(("tracked.txt",), paths)

    def test_python_inventory_reports_scandir_permission_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(_inventory.os, "scandir", side_effect=PermissionError("denied")):
                files, error = RepositoryInventory(root).python_files(root)

        self.assertEqual((), files)
        self.assertIn("denied", error or "")

    def test_python_inventory_entry_limit_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(_inventory, "MAX_VISITED_ENTRIES", 0):
                _write(root / "ordinary.txt", "x\n")
                files, error = RepositoryInventory(root).python_files(root)
        self.assertEqual((), files)
        self.assertIn("exceeded 0 entries", error or "")

    def test_markdown_byte_limit_ignores_unrelated_large_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(root / "guide.md", "x\n")
            _write(root / "unrelated.bin", "x" * 100)
            with patch.object(_inventory, "MAX_MARKDOWN_BYTES", 2):
                files, error = RepositoryInventory(root).markdown_files(root)

        self.assertIsNone(error)
        self.assertEqual((root / "guide.md",), files)

    def test_docs_check_rejects_markdown_alias_before_opening_it(self) -> None:
        class Entry:
            name = "outside.md"

            def is_symlink(self) -> bool:
                return True

            def is_dir(self, *, follow_symlinks: bool) -> bool:
                return False

            def stat(self, *, follow_symlinks: bool) -> SimpleNamespace:
                return SimpleNamespace(st_size=0, st_file_attributes=0)

        class Scan:
            def __enter__(self) -> list[Entry]:
                return [Entry()]

            def __exit__(self, *_args: object) -> None:
                pass

        class TrackingStore(DocumentStore):
            def __init__(self) -> None:
                super().__init__()
                self.opened: list[Path] = []

            def read_text(self, path: Path) -> tuple[str | None, str | None]:
                self.opened.append(path)
                return super().read_text(path)

        governance_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "docs").mkdir()
            store = TrackingStore()
            with patch.object(_inventory.os, "scandir", return_value=Scan()):
                errors, warnings = check_docs(root, governance_root, store, RepositoryInventory(root))

        self.assertEqual([], warnings)
        self.assertTrue(any("Markdown inventory does not permit" in error for error in errors), errors)
        self.assertFalse(any(path.name == "outside.md" for path in store.opened), store.opened)

    def test_tree_inventory_snapshot_is_cached(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(root / "ordinary.txt", "x\n")
            inventory = RepositoryInventory(root)
            real_scandir = _inventory.os.scandir
            with patch.object(_inventory.os, "scandir", wraps=real_scandir) as scandir:
                first = inventory.tree_entries(root)
                calls_after_first = scandir.call_count
                second = inventory.tree_entries(root)

        self.assertEqual(first, second)
        self.assertGreater(calls_after_first, 0)
        self.assertEqual(calls_after_first, scandir.call_count)

    def test_tree_inventory_ancestor_snapshot_serves_descendant_without_rescan(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = root / "docs"
            _write(docs / "guide.md", "# Guide\n")
            inventory = RepositoryInventory(root)
            real_scandir = _inventory.os.scandir
            with patch.object(_inventory.os, "scandir", wraps=real_scandir) as scandir:
                root_entries, root_error = inventory.tree_entries(root)
                calls_after_root = scandir.call_count
                docs_entries, docs_error = inventory.tree_entries(docs)

        self.assertIsNone(root_error)
        self.assertIsNone(docs_error)
        self.assertTrue(any(entry.path.name == "guide.md" for entry in root_entries))
        self.assertEqual((docs / "guide.md",), tuple(entry.path for entry in docs_entries))
        self.assertEqual(calls_after_root, scandir.call_count)

    def test_tree_inventory_rejects_mocked_junction_before_descent(self) -> None:
        class Entry:
            name = "junction"

            def is_symlink(self) -> bool:
                return False

            def is_dir(self, *, follow_symlinks: bool) -> bool:
                return True

        class Scan:
            def __enter__(self) -> list[Entry]:
                return [Entry()]

            def __exit__(self, *_args: object) -> None:
                pass

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(_inventory.os, "scandir", return_value=Scan()), patch.object(
                _inventory,
                "_is_directory_alias",
                side_effect=lambda path: path.parent == root,
            ) as alias_check:
                entries, error = RepositoryInventory(root).tree_entries(root)

        self.assertEqual((), entries)
        self.assertIn("directory symlinks or aliases", error or "")
        self.assertIn(root / "junction", [call.args[0] for call in alias_check.call_args_list])

    def test_python_inventory_sorts_alias_errors(self) -> None:
        class Entry:
            def __init__(self, name: str) -> None:
                self.name = name

            def is_dir(self, *, follow_symlinks: bool) -> bool:
                return True

            def is_symlink(self) -> bool:
                return False

        class Scan:
            def __init__(self, names: tuple[str, ...]) -> None:
                self.entries = [Entry(name) for name in names]

            def __enter__(self) -> list[Entry]:
                return self.entries

            def __exit__(self, *_args: object) -> None:
                pass

        orders = (("z_alias", "a_alias"), ("a_alias", "z_alias"))
        errors: list[str | None] = []
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for order in orders:
                with patch.object(_inventory.os, "scandir", return_value=Scan(order)), patch.object(
                    _inventory,
                    "_is_directory_alias",
                    side_effect=lambda path: path.parent == root,
                ):
                    _files, error = RepositoryInventory(root).python_files(root)
                    errors.append(error)
        self.assertEqual(errors[0], errors[1])
        self.assertIn("a_alias", errors[0] or "")

    def test_windows_reparse_directory_is_an_alias_on_python_311(self) -> None:
        class FakePath:
            def stat(self, *, follow_symlinks: bool) -> SimpleNamespace:
                self.follow_symlinks = follow_symlinks
                return SimpleNamespace(st_file_attributes=0x400)

            def is_symlink(self) -> bool:
                return False

        path = FakePath()
        self.assertTrue(_is_directory_alias(path))  # type: ignore[arg-type]
        self.assertFalse(path.follow_symlinks)


if __name__ == "__main__":
    unittest.main()
