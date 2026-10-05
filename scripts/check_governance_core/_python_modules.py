from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass


_STATEMENT_CONTAINERS = (ast.stmt, ast.excepthandler, ast.match_case)


@dataclass(frozen=True)
class PythonModule:
    tree: ast.Module
    imports: tuple[ast.Import | ast.ImportFrom, ...]


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


def parse_python(text: str, filename: str) -> tuple[PythonModule | None, SyntaxError | None]:
    """Parse one decoded Python source and index its import statements, or return the syntax error."""

    try:
        tree = ast.parse(text, filename=filename)
    except SyntaxError as exc:
        return None, exc
    return PythonModule(tree, _import_statements(tree)), None
