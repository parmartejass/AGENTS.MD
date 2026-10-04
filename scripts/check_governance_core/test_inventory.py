from __future__ import annotations

import io
import logging
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.check_governance_core import _git_capture, _inventory
from scripts.check_governance_core._test_support import docs_fixture, write as _write
from scripts.check_governance_core._docs_checks import check_docs
from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._repository_checks import check_repository


logger = logging.getLogger(__name__)


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


class CachedFamilyRevalidationTests(unittest.TestCase):
    def test_cached_ancestor_metadata_is_checked_before_any_document_read(self) -> None:
        cases = ((kind, cached) for kind in ("valid", "reparse", "symlink", "io_error") for cached in (False, True))
        for kind, cached in cases:
            with self.subTest(kind=kind, cached=cached), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                scan_root = root / "nested"
                ancestor = scan_root / "middle"
                source = ancestor / "child/cached.md"
                _write(source, "unchanged leaf\n")
                inventory, store = RepositoryInventory(root), DocumentStore()
                if cached:
                    self.assertIsNone(inventory.tree_entries(root)[1])
                    self.assertEqual(((source,), None), inventory.markdown_files(scan_root))
                    self.assertEqual(([], []), check_docs(root, root, store, inventory))
                real_stat = Path.stat
                leaf_metadata, leaf_resolution = source.stat(), source.resolve(strict=True)

                def metadata(path, *args, **kwargs):
                    value = real_stat(path, *args, **kwargs)
                    if path != ancestor or kwargs.get("follow_symlinks", True):
                        return value
                    if kind == "io_error":
                        raise PermissionError("ancestor metadata denied")
                    fields = {name: getattr(value, name) for name in dir(value) if name.startswith("st_")}
                    if kind == "reparse":
                        fields["st_file_attributes"] = getattr(value, "st_file_attributes", 0) | stat.FILE_ATTRIBUTE_REPARSE_POINT
                    elif kind == "symlink":
                        fields["st_mode"] = stat.S_IFLNK
                    return SimpleNamespace(**fields)

                with patch.object(Path, "stat", new=metadata), patch.object(store, "read_text", wraps=store.read_text) as read:
                    self.assertEqual(leaf_metadata, source.stat())
                    self.assertEqual(leaf_resolution, source.resolve(strict=True))
                    errors, warnings = check_docs(root, root, store, inventory)
                    self.assertEqual([], warnings)
                    if kind == "valid":
                        self.assertEqual([], errors)
                        self.assertTrue(read.called)
                    else:
                        read.assert_not_called()
                        diagnostic = "ancestor metadata denied" if kind == "io_error" else "alias"
                        self.assertTrue(any(diagnostic in error for error in errors), errors)
                        for files, error in (inventory.markdown_files(scan_root), inventory.markdown_files(root)):
                            self.assertEqual((), files)
                            self.assertIn(diagnostic, error or "")
                        resolved, error = inventory.validate_file(source)
                        self.assertIsNone(resolved)
                        self.assertIn(diagnostic, error or "")
                if kind != "valid":
                    self.assertEqual((), inventory.markdown_files(scan_root)[0])

    def test_cached_family_revalidates_alias_type_identity_and_resolution(self) -> None:
        for kind in ("hardlink", "directory", "special", "identity", "ancestor_alias", "case"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                source = root / "cached.md"
                _write(source, "cached original\n")
                inventory, store = RepositoryInventory(root), DocumentStore()
                self.assertEqual(([], []), check_docs(root, root, store, inventory))
                real_stat, real_resolve = Path.stat, Path.resolve
                if kind in {"hardlink", "directory", "identity"}:
                    previous = root / "previous.txt"
                    source.replace(previous)
                    if kind == "hardlink":
                        os.link(previous, source)
                    elif kind == "directory":
                        source.mkdir()
                    else:
                        _write(source, "replacement\n")

                def metadata(path, *args, **kwargs):
                    value = real_stat(path, *args, **kwargs)
                    if path == source and kind == "special":
                        return SimpleNamespace(st_mode=stat.S_IFIFO, st_nlink=1, st_file_attributes=0)
                    return value

                def resolved(path, *args, **kwargs):
                    if path == source and kind in {"ancestor_alias", "case"}:
                        return root.parent / source.name if kind == "ancestor_alias" else root / "CACHED.md"
                    return real_resolve(path, *args, **kwargs)

                with patch.object(Path, "stat", new=metadata), patch.object(Path, "resolve", new=resolved), patch.object(
                    store, "read_text", side_effect=AssertionError("invalid cached member must fail before any read")
                ):
                    errors, warnings = check_docs(root, root, store, inventory)
                self.assertEqual([], warnings)
                self.assertTrue(errors, kind)
                self.assertFalse(any("unexpectedly" in error for error in errors), errors)

    def test_family_uses_current_metadata_for_byte_limits_and_io_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "growing.md"
            _write(source, "x")
            inventory = RepositoryInventory(root)
            inventory.tree_entries(root)
            _write(source, "longer content")
            with patch("scripts.check_governance_core._inventory.MAX_MARKDOWN_BYTES", 1):
                files, error = inventory.markdown_files(root)
            self.assertEqual((), files)
            self.assertIn("exceeded", error or "")
            inventory = RepositoryInventory(root)
            inventory.tree_entries(root)
            real_stat = Path.stat

            def denied(path, *args, **kwargs):
                if path == source:
                    raise PermissionError("fixture denied")
                return real_stat(path, *args, **kwargs)

            with patch.object(Path, "stat", new=denied):
                files, error = inventory.markdown_files(root)
            self.assertEqual((), files)
            self.assertIn("fixture denied", error or "")

    def test_inventory_hardlink_metadata_witness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "source.txt"
            alias = root / "alias.md"
            _write(target, "sanitized metadata witness\n")
            os.link(target, alias)
            with os.scandir(root) as entries:
                entry = next(item for item in entries if item.name == alias.name)
                directory_links = entry.stat(follow_symlinks=False).st_nlink
            direct_links = alias.stat(follow_symlinks=False).st_nlink
            files, error = RepositoryInventory(root).markdown_files(root)
            logger.warning("Hardlink metadata witness: DirEntry.st_nlink=%s Path.st_nlink=%s inventory_files=%s inventory_error=%s", directory_links, direct_links, len(files), error)
            self.assertGreater(direct_links, 1)
            self.assertEqual((), files)
            self.assertIn("alias", error or "")


class RepositoryHygieneTests(unittest.TestCase):
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
