from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.check_governance_core import _git_capture, _inventory
from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._folder_architecture import check_folder_architecture
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._repository_checks import check_repository


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(value)


class PythonInventoryClassificationTests(unittest.TestCase):
    def test_bounded_capture_does_not_block_closing_a_live_reader_pipe(self) -> None:
        class BlockingPipe:
            def read(self, _size: int) -> bytes:
                _git_capture.time.sleep(1)
                return b""

            def close(self) -> None:
                raise AssertionError("live reader pipe must not be closed synchronously")

        class Process:
            def __init__(self) -> None:
                self.stdout = BlockingPipe()
                self.stderr = io.BytesIO()
                self.returncode = None

            def poll(self) -> int | None:
                return self.returncode

            def kill(self) -> None:
                raise OSError("kill denied")

            def wait(self, *, timeout: float) -> int:
                raise subprocess.TimeoutExpired("git", timeout)

        with patch.object(_git_capture, "TIMEOUT_SECONDS", 0.01), patch.object(
            _git_capture, "CLEANUP_SECONDS", 0.01
        ), patch.object(_git_capture.subprocess, "Popen", return_value=Process()):
            started = _git_capture.time.monotonic()
            _stdout, _stderr, _returncode, error = _git_capture.bounded_capture(
                ["git"], label="tracked files"
            )
            elapsed = _git_capture.time.monotonic() - started

        self.assertLess(elapsed, 0.5)
        self.assertIn("kill denied", error or "")
        self.assertIn("left open because its reader is still active", error or "")

    def test_excluded_descendant_root_is_scanned_instead_of_reusing_empty_slice(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            hidden = root / ".tmp_hidden"
            source = hidden / "unsafe.py"
            _write(source, "print('unsafe')\n")
            inventory = RepositoryInventory(root)
            inventory.tree_entries(root)
            files, error = inventory.python_files(hidden)

        self.assertIsNone(error)
        self.assertEqual((source,), files)

    def test_pipe_capture_never_reads_or_retains_beyond_its_cap(self) -> None:
        class TrackingPipe(io.BytesIO):
            def __init__(self, value: bytes) -> None:
                super().__init__(value)
                self.requests: list[int] = []

            def read(self, size: int = -1) -> bytes:
                self.requests.append(size)
                return super().read(size)

        pipe = TrackingPipe(b"0123456789")
        output = bytearray()
        failures: list[str] = []
        failed = _git_capture.threading.Event()
        with patch.object(_git_capture, "READ_CHUNK_BYTES", 3):
            _git_capture._read_bounded_pipe(
                pipe,
                limit=4,
                label="stdout",
                output=output,
                failure=failures,
                failed=failed,
            )

        self.assertEqual(b"0123", bytes(output))
        self.assertLessEqual(max(pipe.requests), 3)
        self.assertEqual(["Git inventory stdout exceeded 4 bytes"], failures)

    def test_directory_exclusions_do_not_hide_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / ".tmp_unsafe.py"
            _write(source, "print('unsafe')\n")
            files, error = RepositoryInventory(root).python_files(root)

        self.assertIsNone(error)
        self.assertEqual((source,), files)

    def test_complete_inventory_includes_formerly_excluded_content_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python_sources = tuple(
                root / directory / "unsafe.py"
                for directory in ("build", "dist", "node_modules", ".tmp_hidden")
            )
            for source in python_sources:
                _write(source, "print('unsafe')\n")
            markdown = root / "docs/build/hidden.md"
            _write(markdown, "# Hidden\n")
            inventory = RepositoryInventory(root)

            files, python_error = inventory.python_files(root)
            markdown_files, markdown_error = inventory.markdown_files(root / "docs")

        self.assertIsNone(python_error)
        self.assertIsNone(markdown_error)
        self.assertEqual(set(python_sources), set(files))
        self.assertEqual((markdown,), markdown_files)

    def test_original_repository_root_alias_is_rejected_before_enumeration(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            real_alias_check = _inventory._is_directory_alias
            with patch.object(
                _inventory,
                "_is_directory_alias",
                side_effect=lambda path: path == root or real_alias_check(path),
            ), patch.object(
                Path,
                "is_dir",
                side_effect=AssertionError("directory type must not be followed before alias validation"),
            ), patch.object(_inventory.os, "scandir") as scandir:
                inventory = RepositoryInventory(root)
                files, error = inventory.python_files(root)

        self.assertEqual((), files)
        self.assertIn("repository root must not traverse a directory alias", error or "")
        scandir.assert_not_called()

    def test_scan_root_outside_declared_repository_is_rejected_before_enumeration(self) -> None:
        with tempfile.TemporaryDirectory() as repository_temp, tempfile.TemporaryDirectory() as outside_temp:
            root = Path(repository_temp)
            outside = Path(outside_temp)
            inventory = RepositoryInventory(root)
            with patch.object(_inventory.os, "scandir") as scandir:
                files, error = inventory.python_files(outside)

        self.assertEqual((), files)
        self.assertIn("outside the declared repository", error or "")
        scandir.assert_not_called()

    def test_non_python_directory_symlink_is_rejected(self) -> None:
        class Entry:
            name = "linked_directory"

            def is_symlink(self) -> bool:
                return True

            def is_dir(self, *, follow_symlinks: bool) -> bool:
                return follow_symlinks

        class Scan:
            def __enter__(self) -> list[Entry]:
                return [Entry()]

            def __exit__(self, *_args: object) -> None:
                pass

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(_inventory.os, "scandir", return_value=Scan()):
                files, error = RepositoryInventory(root).python_files(root)

        self.assertEqual((), files)
        self.assertIn("directory symlinks", error or "")

    def test_non_python_file_symlink_does_not_block_python_inventory(self) -> None:
        class Entry:
            name = "README-link.md"

            def is_symlink(self) -> bool:
                return True

            def is_dir(self, *, follow_symlinks: bool) -> bool:
                return False

            def stat(self, *, follow_symlinks: bool) -> SimpleNamespace:
                return SimpleNamespace(st_size=0)

        class Scan:
            def __enter__(self) -> list[Entry]:
                return [Entry()]

            def __exit__(self, *_args: object) -> None:
                pass

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(_inventory.os, "scandir", return_value=Scan()):
                files, error = RepositoryInventory(root).python_files(root)

        self.assertEqual((), files)
        self.assertIsNone(error)


class ScopeAndRepositoryHygieneTests(unittest.TestCase):
    def test_example_markers_cannot_authorize_python_roots(self) -> None:
        examples = (
            "```md\n<!-- governance-core-python-root: rogue -->\n```\n",
            "> <!-- governance-core-python-root: rogue -->\n",
            "    <!-- governance-core-python-root: rogue -->\n",
        )
        for example in examples:
            with self.subTest(example=example), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _write(
                    root / "docs/project/architecture/architecture.md",
                    "<!-- governance-core-python-root: scripts -->\n" + example,
                )
                _write(root / "scripts/example/example_main.py", "VALUE = 1\n")
                _write(root / "rogue/bypass.py", "VALUE = 1\n")
                errors, _warnings = check_folder_architecture(
                    root,
                    DocumentStore(),
                    RepositoryInventory(root),
                )
                self.assertTrue(any("rogue/bypass.py" in error for error in errors), errors)

    def test_python_root_markers_require_exact_case(self) -> None:
        for marker in ("Scripts", "x-bookmarks import"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _write(
                    root / "docs/project/architecture/architecture.md",
                    f"<!-- governance-core-python-root: {marker} -->\n",
                )
                _write(root / "scripts/example/example_main.py", "VALUE = 1\n")
                _write(root / "X-Bookmarks Import/fetch.py", "VALUE = 1\n")
                errors, _warnings = check_folder_architecture(
                    root,
                    DocumentStore(),
                    RepositoryInventory(root),
                )
                self.assertTrue(any("noncanonical" in error for error in errors), errors)

    def test_folder_architecture_uses_exact_owner_declared_python_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _write(
                root / "docs/project/architecture/architecture.md",
                "<!-- governance-core-python-root: scripts -->\n"
                "<!-- governance-core-python-root: X-Bookmarks Import -->\n",
            )
            _write(root / "scripts/example/example_main.py", "VALUE = 1\n")
            allowed = root / "X-Bookmarks Import/fetch.py"
            outside = root / "outside.py"
            similar = root / "X-Bookmarks Import-copy/fetch.py"
            _write(allowed, "VALUE = 1\n")
            _write(outside, "VALUE = 1\n")
            _write(similar, "VALUE = 1\n")

            errors, _warnings = check_folder_architecture(
                root,
                DocumentStore(),
                RepositoryInventory(root),
            )

        self.assertTrue(any("outside.py" in error for error in errors), errors)
        self.assertTrue(any("X-Bookmarks Import-copy/fetch.py" in error for error in errors), errors)
        self.assertFalse(any("X-Bookmarks Import/fetch.py" in error for error in errors), errors)

    @unittest.skipIf(shutil.which("git") is None, "git is unavailable")
    def test_repository_rejects_tracked_x_data_without_overmatching_adjacent_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            prohibited = root / "X-Bookmarks Import/data/bookmarks.json"
            adjacent = root / "X-Bookmarks Import/database/fixture.json"
            _write(root / ".gitignore", "X-Bookmarks Import/data/\n")
            _write(prohibited, "{}\n")
            _write(adjacent, "{}\n")
            subprocess.run(
                ["git", "add", ".gitignore", adjacent.relative_to(root)],
                cwd=root,
                check=True,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "add", "-f", prohibited.relative_to(root)],
                cwd=root,
                check=True,
                capture_output=True,
                timeout=10,
            )

            errors = check_repository(
                root,
                DocumentStore(),
                RepositoryInventory(root),
                enforce_tracked_ignored=True,
            )

        self.assertTrue(any("Tracked local-only/ignored file" in error for error in errors), errors)
        self.assertFalse(any("database/fixture.json" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
