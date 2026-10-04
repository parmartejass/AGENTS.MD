from __future__ import annotations

import ast
from pathlib import Path

from scripts.check_governance_core._documents import DocumentStore


_PACKAGE_ENTRY = "__init__.py"
_LAUNCHER = "__main__.py"
_INTERNAL_MODULE_PREFIXES = ("_", "test")


def _is_dunder(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _is_private(name: str) -> bool:
    return name.startswith("_") and not _is_dunder(name)


def module_name_errors(path: Path, relative: str) -> list[str]:
    """Private internals are ``_``-prefixed modules; ``test*`` modules are test-runner internals."""

    if path.name in {_PACKAGE_ENTRY, _LAUNCHER} or path.stem.startswith(_INTERNAL_MODULE_PREFIXES):
        return []
    return [f"Python module inside a package must be a private `_` module or a `test*` module: {relative}"]


def parse_module(path: Path, relative: str, store: DocumentStore) -> tuple[ast.Module | None, list[str]]:
    text, read_error = store.read_text(path)
    if read_error:
        return None, [read_error]
    assert text is not None
    try:
        return ast.parse(text, filename=str(path)), []
    except SyntaxError as exc:
        return None, [f"Python module cannot be parsed for packaged-folder witnesses: {relative}:{exc.lineno or 1}: {exc.msg}"]


def _bound_public_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for leaf in ast.walk(target):
                    if isinstance(leaf, ast.Name):
                        names.add(leaf.id)
        elif isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            names.update(alias.asname or alias.name for alias in node.names)
    return {name for name in names if not name.startswith("_")}


def entry_errors(tree: ast.Module, relative: str) -> list[str]:
    """``__init__.py`` declares ``__all__`` once; every public binding is listed; every entry is bound."""

    declarations = [
        node for node in tree.body
        if isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "__all__"
    ]
    if len(declarations) != 1:
        return [f"Package entry must declare `__all__` exactly once at module level: {relative}"]
    value = declarations[0].value
    if not isinstance(value, (ast.List, ast.Tuple)) or any(
        not isinstance(item, ast.Constant) or not isinstance(item.value, str) or not item.value for item in value.elts
    ):
        return [f"Package entry `__all__` must be a list or tuple of non-empty string literals: {relative}"]
    declared = [item.value for item in value.elts if isinstance(item, ast.Constant)]
    errors: list[str] = []
    if len(set(declared)) != len(declared):
        errors.append(f"Package entry `__all__` must not repeat a member: {relative}")
    bound = _bound_public_names(tree)
    for name in sorted(set(declared) - bound):
        errors.append(f"Package entry `__all__` names an unbound member {name!r}: {relative}")
    for name in sorted(bound - set(declared)):
        errors.append(f"Package entry binds public name {name!r} outside `__all__`; prefix it with `_` or declare it: {relative}")
    return errors


def _delegating_call(node: ast.stmt) -> ast.Call | None:
    if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) \
            and node.exc.func.id == "SystemExit" and len(node.exc.args) == 1 and isinstance(node.exc.args[0], ast.Call):
        return node.exc.args[0]
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) \
                and call.func.value.id == "sys" and call.func.attr == "exit" \
                and len(call.args) == 1 and isinstance(call.args[0], ast.Call):
            return call.args[0]
        return call
    return None


def _is_main_guard(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.If) and not node.orelse
        and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__" and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq)
        and len(node.test.comparators) == 1 and isinstance(node.test.comparators[0], ast.Constant)
        and node.test.comparators[0].value == "__main__"
    )


def launcher_errors(tree: ast.Module, relative: str, package: str) -> list[str]:
    """``__main__.py`` holds only imports and one guarded delegation to a member imported from its package entry."""

    error = f"Package launcher must only import and delegate to its package entry under the `__main__` guard: {relative}"
    entry_members: set[str] = set()
    guards: list[ast.If] = []
    for index, node in enumerate(tree.body):
        if index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.Import):
            continue
        if isinstance(node, ast.ImportFrom):
            if node.level == 1 and node.module is None or node.level == 0 and node.module == package:
                entry_members.update(alias.asname or alias.name for alias in node.names)
            continue
        if _is_main_guard(node):
            guards.append(node)
            continue
        return [error]
    if len(guards) != 1 or len(guards[0].body) != 1:
        return [error]
    call = _delegating_call(guards[0].body[0])
    if call is None or not isinstance(call.func, ast.Name) or call.func.id not in entry_members:
        return [error]
    return []


def _imports(tree: ast.Module, path: Path, bases: tuple[Path, ...]) -> list[tuple[int, Path, str, tuple[str, ...]]]:
    """Yield (line, import base directory, prefix dots, dotted segments) for every import statement."""

    found: list[tuple[int, Path, str, tuple[str, ...]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.extend((node.lineno, base, "", tuple(alias.name.split("."))) for base in bases)
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            if node.level:
                ancestors = (path.parent, *path.parent.parents)
                if node.level - 1 >= len(ancestors):
                    continue
                level_bases: tuple[Path, ...] = (ancestors[node.level - 1],)
            else:
                level_bases = bases
            for base in level_bases:
                found.append((node.lineno, base, "." * node.level, module))
                found.extend((node.lineno, base, "." * node.level, module + (alias.name,)) for alias in node.names)
    return found


def deep_import_errors(tree: ast.Module, path: Path, bases: tuple[Path, ...], relative: str) -> list[str]:
    """A private module may be imported only by modules of its own package folder."""

    errors: list[str] = []
    reported: set[tuple[int, Path]] = set()
    for line, base, dots, segments in _imports(tree, path, bases):
        private_index = next((index for index, segment in enumerate(segments) if _is_private(segment)), None)
        if private_index is None:
            continue
        owner = base.joinpath(*segments[:private_index])
        if not (owner / _PACKAGE_ENTRY).is_file() or path.parent == owner or (line, owner) in reported:
            continue
        reported.add((line, owner))
        errors.append(f"Deep import of private module {dots}{'.'.join(segments)} from outside its package: {relative}:{line}")
    return errors


def interface_errors(
    path: Path, root: Path, import_bases: tuple[Path, ...], relative: str, store: DocumentStore,
) -> list[str]:
    """Run every AST witness that applies to one module below an enforced source root.

    Absolute imports resolve against each declared root's parent, the directory
    ``python -m <root>.<package>`` runs from; relative imports resolve from the module.
    """

    errors = module_name_errors(path, relative)
    tree, parse_errors = parse_module(path, relative, store)
    if tree is None:
        return errors + parse_errors
    if path.name == _PACKAGE_ENTRY:
        errors.extend(entry_errors(tree, relative))
    elif path.name == _LAUNCHER:
        errors.extend(launcher_errors(tree, relative, ".".join(path.relative_to(root.parent).parent.parts)))
    errors.extend(deep_import_errors(tree, path, import_bases, relative))
    return errors
