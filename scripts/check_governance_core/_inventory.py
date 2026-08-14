from __future__ import annotations

import os
import stat
import time
from dataclasses import dataclass
from pathlib import Path

from scripts.check_governance_core._git_capture import bounded_capture


NON_CONTENT_DIRS = {".git"}
MAX_PYTHON_FILES = 10_000
MAX_MARKDOWN_FILES = 10_000
MAX_VISITED_ENTRIES = 50_000
MAX_PYTHON_BYTES = 64 * 1024 * 1024
MAX_MARKDOWN_BYTES = 64 * 1024 * 1024
MAX_INVENTORY_SECONDS = 5.0


@dataclass(frozen=True)
class InventoryEntry:
    path: Path
    is_directory: bool
    is_symlink: bool
    size: int


class RepositoryInventory:
    """Own deterministic, cached repository file enumeration for one run."""

    def __init__(self, repository_root: Path) -> None:
        self._requested_root = _absolute_lexical(repository_root)
        self.repository_root, self.root_error = _validate_original_directory(
            self._requested_root,
            label="repository root",
        )
        self._tracked: dict[Path, tuple[tuple[str, ...], str | None]] = {}
        self._tracked_ignored: dict[Path, tuple[tuple[str, ...], str | None]] = {}
        self._trees: dict[Path, tuple[tuple[InventoryEntry, ...], str | None]] = {}
        self._families: dict[tuple[Path, str], tuple[tuple[Path, ...], str | None]] = {}

    def tracked_paths(self, root: Path) -> tuple[tuple[str, ...], str | None]:
        root, root_error = self.resolve_scan_root(root)
        if root_error:
            return (), root_error
        assert root is not None
        if root in self._tracked:
            return self._tracked[root]
        if not (root / ".git").exists():
            result = ((), f"Repository checks require a Git worktree: {root}")
        else:
            result = self._git_paths(root, ["ls-files", "-z"], "tracked files")
        self._tracked[root] = result
        return result

    def tracked_ignored_paths(self, root: Path) -> tuple[tuple[str, ...], str | None]:
        root, root_error = self.resolve_scan_root(root)
        if root_error:
            return (), root_error
        assert root is not None
        if root not in self._tracked_ignored:
            self._tracked_ignored[root] = self._git_paths(
                root,
                ["ls-files", "-c", "-i", "--exclude-per-directory=.gitignore", "-z"],
                "tracked ignored files",
            )
        return self._tracked_ignored[root]

    def validate_file(self, path: Path) -> tuple[Path | None, str | None]:
        """Validate one exactly spelled, contained, non-aliased repository file."""

        requested = _absolute_lexical(path)
        parent, parent_error = self.resolve_scan_root(requested.parent)
        if parent_error:
            return None, parent_error
        assert parent is not None
        try:
            exact = next((child for child in parent.iterdir() if child.name == requested.name), None)
            if exact is None:
                return None, f"Repository file is missing or noncanonical: {requested}"
            metadata = exact.stat(follow_symlinks=False)
            if exact.is_symlink() or _has_reparse_attribute(metadata) or metadata.st_nlink > 1:
                return None, f"Repository file must not be an alias: {requested}"
            if not exact.is_file():
                return None, f"Repository path is not a file: {requested}"
            return exact.resolve(strict=True), None
        except OSError as exc:
            return None, f"Unable to validate repository file {requested}: {exc}"

    def python_files(self, root: Path) -> tuple[tuple[Path, ...], str | None]:
        return self._file_family(
            root,
            suffix=".py",
            label="Python",
            max_files=MAX_PYTHON_FILES,
            max_bytes=MAX_PYTHON_BYTES,
        )

    def markdown_files(self, root: Path) -> tuple[tuple[Path, ...], str | None]:
        return self._file_family(
            root,
            suffix=".md",
            label="Markdown",
            max_files=MAX_MARKDOWN_FILES,
            max_bytes=MAX_MARKDOWN_BYTES,
        )

    def _file_family(
        self,
        root: Path,
        *,
        suffix: str,
        label: str,
        max_files: int,
        max_bytes: int,
    ) -> tuple[tuple[Path, ...], str | None]:
        root, root_error = self.resolve_scan_root(root)
        if root_error:
            return (), root_error
        assert root is not None
        cache_key = (root, suffix)
        if cache_key in self._families:
            return self._families[cache_key]
        entries, tree_error = self._tree_entries(root)
        if tree_error:
            result = ((), tree_error)
        else:
            files: list[Path] = []
            total_bytes = 0
            for entry in entries:
                if entry.is_directory or entry.path.suffix.lower() != suffix:
                    continue
                if entry.is_symlink:
                    result = ((), f"{label} inventory does not permit file symlinks or aliases: {entry.path}")
                    break
                files.append(entry.path)
                total_bytes += entry.size
                if len(files) > max_files or total_bytes > max_bytes:
                    result = (
                        (),
                        f"{label} inventory exceeded its limit ({max_files} files or {max_bytes} bytes)",
                    )
                    break
            else:
                result = (tuple(files), None)
        self._families[cache_key] = result
        return result

    def tree_entries(self, root: Path) -> tuple[tuple[InventoryEntry, ...], str | None]:
        """Return one bounded deterministic tree snapshot, or an explicit all-or-nothing error."""

        root, root_error = self.resolve_scan_root(root)
        if root_error:
            return (), root_error
        assert root is not None
        return self._tree_entries(root)

    def resolve_scan_root(self, root: Path) -> tuple[Path | None, str | None]:
        if self.root_error:
            return None, self.root_error
        assert self.repository_root is not None
        requested = _absolute_lexical(root)
        try:
            relative = requested.relative_to(self._requested_root)
        except ValueError:
            return None, f"Repository inventory root is outside the declared repository: {requested}"
        current = self._requested_root
        for part in relative.parts:
            current /= part
            try:
                if _is_directory_alias(current):
                    return None, f"Repository inventory root must not traverse a directory alias: {current}"
            except OSError as exc:
                return None, f"Unable to validate repository inventory root {current}: {exc}"
        if not requested.is_dir():
            return None, f"Repository inventory root is not a directory: {requested}"
        try:
            resolved = requested.resolve(strict=True)
            resolved.relative_to(self.repository_root)
        except (OSError, ValueError) as exc:
            return None, f"Repository inventory root escapes the declared repository: {requested} ({exc})"
        return resolved, None

    def _tree_entries(self, root: Path) -> tuple[tuple[InventoryEntry, ...], str | None]:
        if root in self._trees:
            return self._trees[root]
        ancestor = next(
            (
                candidate
                for candidate, (_entries, error) in self._trees.items()
                if error is None and (candidate == root or candidate in root.parents)
            ),
            None,
        )
        if ancestor is not None:
            ancestor_entries = self._trees[ancestor][0]
            root_is_represented = ancestor == root or any(
                entry.path == root and entry.is_directory for entry in ancestor_entries
            )
            if root_is_represented:
                entries = tuple(
                    entry
                    for entry in ancestor_entries
                    if root in entry.path.parents
                )
                result = (entries, None)
                self._trees[root] = result
                return result
        started = time.monotonic()
        visited = 0
        collected: list[InventoryEntry] = []
        pending = [root]
        try:
            while pending:
                if time.monotonic() - started > MAX_INVENTORY_SECONDS:
                    result = ((), f"Repository tree inventory exceeded {MAX_INVENTORY_SECONDS:.1f} seconds")
                    break
                current = pending.pop()
                scanned: list[os.DirEntry[str]] = []
                with os.scandir(current) as iterator:
                    for item in iterator:
                        visited += 1
                        if visited > MAX_VISITED_ENTRIES:
                            result = ((), f"Repository tree inventory exceeded {MAX_VISITED_ENTRIES} entries")
                            break
                        if time.monotonic() - started > MAX_INVENTORY_SECONDS:
                            result = ((), f"Repository tree inventory exceeded {MAX_INVENTORY_SECONDS:.1f} seconds")
                            break
                        scanned.append(item)
                    else:
                        scanned.sort(key=lambda item: (item.name.casefold(), item.name))
                        child_directories: list[Path] = []
                        for item in scanned:
                            candidate = current / item.name
                            try:
                                candidate.relative_to(root)
                            except ValueError:
                                result = ((), f"Repository tree path escapes root: {candidate}")
                                break
                            is_symlink = item.is_symlink()
                            follows_to_directory = is_symlink and item.is_dir(follow_symlinks=True)
                            is_directory = item.is_dir(follow_symlinks=False)
                            if follows_to_directory or (is_directory and _is_directory_alias(candidate)):
                                result = (
                                    (),
                                    f"Repository tree does not permit directory symlinks or aliases: {candidate}",
                                )
                                break
                            if is_directory:
                                if item.name in NON_CONTENT_DIRS:
                                    continue
                                try:
                                    candidate.resolve().relative_to(root)
                                except ValueError:
                                    result = ((), f"Repository tree directory escapes root: {candidate}")
                                    break
                                collected.append(InventoryEntry(candidate, True, False, 0))
                                child_directories.append(candidate)
                                continue
                            metadata = item.stat(follow_symlinks=False)
                            is_alias = is_symlink or _has_reparse_attribute(metadata) or metadata.st_nlink > 1
                            collected.append(InventoryEntry(candidate, False, is_alias, metadata.st_size))
                        else:
                            pending.extend(reversed(child_directories))
                            continue
                    break
            else:
                result = (tuple(collected), None)
        except OSError as exc:
            result = ((), f"Unable to enumerate repository tree: {exc}")
        self._trees[root] = result
        return result

    @staticmethod
    def _git_paths(
        root: Path,
        arguments: list[str],
        label: str,
    ) -> tuple[tuple[str, ...], str | None]:
        stdout, stderr, returncode, failure = bounded_capture(
            ["git", "-C", str(root), *arguments],
            label=label,
        )
        if failure is None and returncode:
            detail = stderr[:1000].decode("utf-8", errors="replace")
            failure = f"Unable to enumerate {label} with git ls-files: {detail}"
        if failure is not None:
            return (), failure
        paths = tuple(
            sorted(
                (raw.decode("utf-8", errors="surrogateescape") for raw in stdout.split(b"\0") if raw),
                key=lambda value: (value.casefold(), value),
            )
        )
        return paths, None


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _validate_original_directory(path: Path, *, label: str) -> tuple[Path | None, str | None]:
    anchor = Path(path.anchor)
    current = anchor
    try:
        for part in path.parts[1:]:
            current /= part
            if _is_directory_alias(current):
                return None, f"{label} must not traverse a directory alias: {current}"
        if not path.is_dir():
            return None, f"{label} is not a directory: {path}"
        return path.resolve(strict=True), None
    except OSError as exc:
        return None, f"Unable to validate {label} {path}: {exc}"


def _is_directory_alias(path: Path) -> bool:
    """Reject symlinks and Windows reparse-point directory aliases on Python 3.11+."""

    return path.is_symlink() or _has_reparse_attribute(path.stat(follow_symlinks=False))


def _has_reparse_attribute(metadata: os.stat_result) -> bool:
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)
