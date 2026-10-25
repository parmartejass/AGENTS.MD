from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass
from functools import cached_property


_STATEMENT_CONTAINERS = (ast.stmt, ast.excepthandler, ast.match_case)


@dataclass(frozen=True)
class Binding:
    """One module-level name binding; ``value`` is the bound expression when the target is the bare name."""

    name: str
    line: int
    value: ast.expr | None


@dataclass(frozen=True)
class PythonModule:
    tree: ast.Module
    imports: tuple[ast.Import | ast.ImportFrom, ...]

    @cached_property
    def bindings(self) -> tuple[Binding, ...]:
        """Module-level name bindings, indexed on first use and reused by every consumer."""

        return _module_bindings(self.tree)


def _import_statements(tree: ast.Module) -> tuple[ast.Import | ast.ImportFrom, ...]:
    """Return import statements in ``ast.walk`` order without descending into expressions.

    Expressions never contain statements, so a breadth-first walk over statement containers
    keeps the same relative order while skipping most nodes.
    """

    found: list[ast.Import | ast.ImportFrom] = []
    pending: deque[ast.AST] = deque([tree])
    while pending:
        node = pending.popleft()
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            found.append(node)
        pending.extend(child for child in ast.iter_child_nodes(node) if isinstance(child, _STATEMENT_CONTAINERS))
    return tuple(found)


def _module_bindings(tree: ast.Module) -> tuple[Binding, ...]:
    """Index top-level definitions, imports and assignment targets (chained, annotated with a value, augmented)."""

    found: list[Binding] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.append(Binding(node.name, node.lineno, None))
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            if isinstance(node, ast.AnnAssign) and node.value is None:
                continue  # an annotation alone binds nothing
            value = None if isinstance(node, ast.AugAssign) else node.value
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                found.extend(Binding(leaf.id, node.lineno, value if leaf is target else None)
                             for leaf in ast.walk(target) if isinstance(leaf, ast.Name))
        elif isinstance(node, ast.Import):
            found.extend(Binding(alias.asname or alias.name.split(".", 1)[0], node.lineno, None) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            found.extend(Binding(alias.asname or alias.name, node.lineno, None) for alias in node.names)
    return tuple(found)


def parse_python(text: str, filename: str) -> tuple[PythonModule | None, SyntaxError | None]:
    """Parse one decoded Python source and index its import statements, or return the syntax error."""

    try:
        tree = ast.parse(text, filename=filename)
    except SyntaxError as exc:
        return None, exc
    return PythonModule(tree, _import_statements(tree)), None
