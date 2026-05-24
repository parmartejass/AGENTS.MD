from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from _issues import Issue


@dataclass(frozen=True)
class TreeSpec:
    tree_root: str
    parent_main: str
    module_prefix: str
    child_dirs: tuple[str, ...]


def _read_text_file(path: Path, rel_path: str, issues: list[Issue]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        issues.append(Issue(path=rel_path, message=f"Failed to read file for architecture check: {exc}"))
        return None


def _parse_python_module(root: Path, path: Path, issues: list[Issue]) -> ast.Module | None:
    rel_path = path.relative_to(root).as_posix()
    raw = _read_text_file(path, rel_path, issues)
    if raw is None:
        return None
    try:
        return ast.parse(raw, filename=str(path))
    except SyntaxError as exc:
        issues.append(Issue(path=rel_path, message=f"Could not parse Python for architecture check: {exc}"))
        return None


def _resolve_relative_import_targets(path: Path, tree_root: Path, module_prefix: str, node: ast.ImportFrom) -> list[str]:
    parent_parts = list(path.relative_to(tree_root).parent.parts)
    current_package_parts = [module_prefix, *parent_parts]
    ascend = node.level - 1
    if len(current_package_parts) - ascend < 1:
        return []

    base_parts = current_package_parts[: len(current_package_parts) - ascend]
    if node.module is not None:
        return [".".join([*base_parts, *node.module.split(".")])]
    return [".".join([*base_parts, alias.name]) for alias in node.names]


def check_parent_only_imports(root: Path, spec: TreeSpec, issues: list[Issue]) -> None:
    tree_root = root / spec.tree_root
    parent_main = root / spec.parent_main
    if not tree_root.is_dir() or not parent_main.is_file():
        return

    child_prefixes = {child: f"{spec.module_prefix}.{child}" for child in spec.child_dirs}

    for file_path in sorted(tree_root.rglob("*.py")):
        rel_path = file_path.relative_to(root).as_posix()
        if file_path == parent_main:
            owner = "parent"
        else:
            relative_parts = file_path.relative_to(tree_root).parts
            if not relative_parts:
                continue
            owner = relative_parts[0]
            if owner not in spec.child_dirs:
                continue

        tree = _parse_python_module(root, file_path, issues)
        if tree is None:
            continue

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module is not None:
                    imports.append(node.module)
                elif node.level > 0:
                    imports.extend(_resolve_relative_import_targets(file_path, tree_root, spec.module_prefix, node))

        for imported in imports:
            matched_child = next(
                (
                    child
                    for child, prefix in child_prefixes.items()
                    if imported == prefix or imported.startswith(prefix + ".")
                ),
                None,
            )
            if matched_child is None or owner == "parent" or owner == matched_child:
                continue
            issues.append(
                Issue(
                    path=rel_path,
                    message=(
                        f"Cross-child import detected ({owner} -> {matched_child}). "
                        "Only the parent entrypoint may connect feature folders."
                    ),
                )
            )
