from __future__ import annotations

import ast
import tokenize
from dataclasses import dataclass
from pathlib import Path

from scripts.check_governance_core._inventory import RepositoryInventory


@dataclass(frozen=True)
class SafetyIssue:
    path: Path
    line: int
    column: int
    severity: str
    rule: str
    message: str

    def format(self, root: Path) -> str:
        try:
            path = self.path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            path = str(self.path)
        return f"{path}:{self.line}:{self.column} {self.rule} {self.message}"


def _subprocess_aliases(tree: ast.AST) -> tuple[set[str], dict[str, str]]:
    modules = {"subprocess"}
    functions: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                if alias.name in {"run", "call", "check_call", "check_output", "Popen"}:
                    functions[alias.asname or alias.name] = alias.name
    return modules, functions


class _Visitor(ast.NodeVisitor):
    def __init__(
        self,
        path: Path,
        modules: set[str],
        functions: dict[str, str],
        reviewed_popen_paths: frozenset[Path],
    ) -> None:
        self.path = path
        self.modules = modules
        self.functions = functions
        self.reviewed_popen_paths = reviewed_popen_paths
        self.issues: list[SafetyIssue] = []
        self.context_calls: set[int] = set()

    def _add(self, node: ast.AST, severity: str, rule: str, message: str) -> None:
        self.issues.append(
            SafetyIssue(
                self.path,
                int(getattr(node, "lineno", 1)),
                int(getattr(node, "col_offset", 0)) + 1,
                severity,
                rule,
                message,
            )
        )

    def visit_With(self, node: ast.With) -> None:  # noqa: N802
        for item in node.items:
            self.context_calls.update(id(value) for value in ast.walk(item.context_expr) if isinstance(value, ast.Call))
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:  # noqa: N802
        for item in node.items:
            self.context_calls.update(id(value) for value in ast.walk(item.context_expr) if isinstance(value, ast.Call))
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        if node.type is None:
            self._add(node, "ERROR", "BARE_EXCEPT", "Bare except hides failures.")
            return
        if isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
            meaningful = [
                value
                for value in node.body
                if not (
                    isinstance(value, ast.Expr)
                    and isinstance(value.value, ast.Constant)
                    and isinstance(value.value.value, str)
                )
            ]
            silent = not meaningful or (
                len(meaningful) == 1
                and (
                    isinstance(meaningful[0], (ast.Pass, ast.Continue, ast.Break))
                    or (
                        isinstance(meaningful[0], ast.Expr)
                        and isinstance(meaningful[0].value, ast.Constant)
                        and meaningful[0].value.value is Ellipsis
                    )
                )
            )
            if silent:
                self._add(node, "ERROR", "SILENT_EXCEPT", f"except {node.type.id} must not be silent.")
                return
            if len(meaningful) == 1 and isinstance(meaningful[0], ast.Return) and _literalish(meaningful[0].value):
                self._add(node, "WARN", "EXCEPT_RETURN_LITERAL", "Broad exception returns only a literal sentinel.")
                return
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self._add(node, "ERROR", "PRINT_CALL", "Use module-level logging; print() is prohibited.")
        subprocess_call = self._subprocess_call(node)
        if subprocess_call in {"run", "call", "check_call", "check_output"} and not any(
            keyword.arg == "timeout" for keyword in node.keywords
        ):
            self._add(node, "ERROR", "SUBPROCESS_TIMEOUT", f"subprocess.{subprocess_call}() requires timeout=.")
        elif subprocess_call == "Popen" and self.path.resolve() not in self.reviewed_popen_paths:
            self._add(node, "WARN", "SUBPROCESS_POPEN", "Popen requires direct lifecycle review.")
        if id(node) not in self.context_calls:
            if _file_open(node):
                self._add(node, "WARN", "FILE_OPEN_WITHOUT_WITH", "File open is not managed by a context manager.")
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"write_text", "write_bytes"}:
                self._add(node, "WARN", "NON_ATOMIC_WRITE", "Path write is not atomic.")
        self.generic_visit(node)

    def _subprocess_call(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self.modules:
            return node.func.attr
        if isinstance(node.func, ast.Name):
            return self.functions.get(node.func.id)
        return None


def _literalish(value: ast.expr | None) -> bool:
    return value is None or isinstance(value, ast.Constant) or (
        isinstance(value, ast.Tuple) and all(_literalish(item) for item in value.elts)
    ) or (
        isinstance(value, (ast.List, ast.Set)) and not value.elts
    ) or (
        isinstance(value, ast.Dict) and not value.keys
    ) or (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == "set"
        and not value.args
        and not value.keywords
    )


def _file_open(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name) and node.func.id == "open":
        return True
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "open":
        return False
    if any(
        keyword.arg in {"encoding", "newline", "errors", "buffering"}
        for keyword in node.keywords
    ):
        return True
    return bool(
        node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    )


def _scan(path: Path, reviewed_popen_paths: frozenset[Path]) -> list[SafetyIssue]:
    try:
        with tokenize.open(path) as handle:
            tree = ast.parse(handle.read(), filename=str(path))
    except (OSError, UnicodeDecodeError) as exc:
        return [SafetyIssue(path, 1, 1, "ERROR", "READ_FAILED", str(exc))]
    except SyntaxError as exc:
        return [SafetyIssue(path, exc.lineno or 1, exc.offset or 1, "ERROR", "SYNTAX_ERROR", exc.msg)]
    modules, functions = _subprocess_aliases(tree)
    visitor = _Visitor(path, modules, functions, reviewed_popen_paths)
    visitor.visit(tree)
    return visitor.issues


def check_python_safety(
    root: Path,
    inventory: RepositoryInventory,
    *,
    fail_on_warnings: bool,
    reviewed_popen_paths: frozenset[Path] = frozenset(),
) -> tuple[list[str], list[str]]:
    files, inventory_error = inventory.python_files(root)
    if inventory_error:
        return [inventory_error], []
    issues = [issue for path in files for issue in _scan(path, reviewed_popen_paths)]
    issues.sort(key=lambda issue: (issue.path.as_posix().casefold(), issue.line, issue.column, issue.rule))
    errors = [issue.format(root) for issue in issues if issue.severity == "ERROR"]
    warnings = [issue.format(root) for issue in issues if issue.severity == "WARN"]
    if fail_on_warnings:
        errors.extend(f"strict warning: {warning}" for warning in warnings)
    return errors, warnings
