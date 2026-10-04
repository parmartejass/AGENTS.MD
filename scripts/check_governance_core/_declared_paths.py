from __future__ import annotations

from pathlib import Path, PurePosixPath


_UNSAFE_PATH_CHARS = frozenset('<>"|?*')


def canonical_relative(value: str) -> PurePosixPath | None:
    """Return the parts of an exactly spelled, safe, contained relative path, or None."""

    declared = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or ":" in value
        or declared.is_absolute()
        or declared.as_posix() != value
        or any(
            part in {"", ".", ".."}
            or part != part.strip()
            or part != part.rstrip(" .")
            or any(char in _UNSAFE_PATH_CHARS or ord(char) < 32 for char in part)
            for part in declared.parts
        )
    ):
        return None
    return declared


def _resolve_declared(root: Path, value: str, *, directory: bool) -> tuple[Path | None, str | None]:
    declared = canonical_relative(value)
    if declared is None:
        return None, f"invalid non-canonical relative path: {value!r}"
    current = root.resolve()
    for part in declared.parts:
        try:
            exact = next((child for child in current.iterdir() if child.name == part), None)
        except OSError as exc:
            return None, f"unable to inspect declared path {value!r}: {exc}"
        if exact is None:
            return None, f"declared path is missing or has non-canonical spelling: {value}"
        if exact.is_symlink():
            return None, f"declared path must not traverse a symlink: {value}"
        current = exact
    resolved = current.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None, f"declared path escapes its owner root: {value}"
    if directory and not resolved.is_dir():
        return None, f"declared path is not a directory: {value}"
    if not directory and not resolved.is_file():
        return None, f"declared path is not a file: {value}"
    return resolved, None


def resolve_declared_file(root: Path, value: str) -> tuple[Path | None, str | None]:
    """Resolve an exactly spelled, contained owner-declared relative file path."""

    return _resolve_declared(root, value, directory=False)


def resolve_declared_directory(root: Path, value: str) -> tuple[Path | None, str | None]:
    """Resolve an exactly spelled, contained owner-declared relative directory path."""

    return _resolve_declared(root, value, directory=True)
