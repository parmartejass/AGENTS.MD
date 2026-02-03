from __future__ import annotations

import argparse
import ast
import logging
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    col: int
    severity: str  # "ERROR" | "WARN"
    rule: str
    message: str

    def format(self, *, repo_root: Path) -> str:
        try:
            display_path = self.path.resolve().relative_to(repo_root.resolve())
        except Exception:
            display_path = self.path
        return f"{self.severity} {display_path}:{self.line}:{self.col} {self.rule} {self.message}"


def _configure_logging(*, verbose: bool) -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def _iter_python_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.py"):
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: str(p).lower())


def _read_python_source(path: Path) -> str:
    with tokenize.open(path) as handle:
        return handle.read()


def _collect_subprocess_aliases(tree: ast.AST) -> tuple[set[str], dict[str, str]]:
    module_aliases: set[str] = {"subprocess"}
    function_aliases: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    module_aliases.add(alias.asname or alias.name)

        if isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                imported_name = alias.name
                if imported_name in {"run", "call", "check_call", "check_output", "Popen"}:
                    function_aliases[alias.asname or imported_name] = imported_name

    return module_aliases, function_aliases


class _SafetyVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        path: Path,
        repo_root: Path,
        subprocess_modules: set[str],
        subprocess_functions: dict[str, str],
    ) -> None:
        self._path = path
        self._repo_root = repo_root
        self._subprocess_modules = subprocess_modules
        self._subprocess_functions = subprocess_functions
        self._issues: list[Issue] = []
        self._calls_in_with_context: set[int] = set()

    @property
    def issues(self) -> list[Issue]:
        return self._issues

    def _add_issue(self, *, node: ast.AST, severity: str, rule: str, message: str) -> None:
        lineno = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0) + 1
        self._issues.append(
            Issue(
                path=self._path,
                line=int(lineno),
                col=int(col),
                severity=severity,
                rule=rule,
                message=message,
            )
        )

    def _mark_calls_in_context_expr(self, expr: ast.AST) -> None:
        for node in ast.walk(expr):
            if isinstance(node, ast.Call):
                self._calls_in_with_context.add(id(node))

    def visit_With(self, node: ast.With) -> None:  # noqa: N802
        for item in node.items:
            self._mark_calls_in_context_expr(item.context_expr)
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:  # noqa: N802
        for item in node.items:
            self._mark_calls_in_context_expr(item.context_expr)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        if node.type is None:
            self._add_issue(
                node=node,
                severity="ERROR",
                rule="BARE_EXCEPT",
                message="Bare `except:` hides errors; catch specific exceptions and log/raise.",
            )
            return

        if isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
            if self._is_silent_except_body(node.body):
                self._add_issue(
                    node=node,
                    severity="ERROR",
                    rule="SILENT_EXCEPT",
                    message=f"`except {node.type.id}` must not be silent; log context and/or raise a domain error.",
                )
                return
            if self._is_literal_return_except_body(node.body):
                self._add_issue(
                    node=node,
                    severity="WARN",
                    rule="EXCEPT_RETURN_LITERAL",
                    message=(
                        f"`except {node.type.id}` that only returns a literal/sentinel can hide failures; "
                        "acceptable only when the sentinel is part of the function's explicit contract and callers handle it. "
                        "Otherwise log context and/or raise a domain error."
                    ),
                )
                return

        self.generic_visit(node)

    @staticmethod
    def _is_silent_except_body(body: list[ast.stmt]) -> bool:
        meaningful = [stmt for stmt in body if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))]
        if len(meaningful) != 1:
            return False
        return isinstance(meaningful[0], ast.Pass)

    @staticmethod
    def _is_literal_return_except_body(body: list[ast.stmt]) -> bool:
        meaningful = [stmt for stmt in body if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))]
        if len(meaningful) != 1:
            return False
        stmt = meaningful[0]
        if not isinstance(stmt, ast.Return):
            return False
        return _SafetyVisitor._is_literalish_expr(stmt.value)

    @staticmethod
    def _is_literalish_expr(expr) -> bool:
        if expr is None:
            return True
        if isinstance(expr, ast.Constant):
            return True
        if isinstance(expr, ast.Tuple):
            return all(_SafetyVisitor._is_literalish_expr(elt) for elt in expr.elts)
        return False

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self._add_issue(
                node=node,
                severity="ERROR",
                rule="PRINT_CALL",
                message="Use module-level logging; `print()` is forbidden.",
            )

        subprocess_call = self._resolve_subprocess_call(node)
        if subprocess_call in {"run", "call", "check_call", "check_output"}:
            if not self._call_has_keyword(node, "timeout"):
                self._add_issue(
                    node=node,
                    severity="ERROR",
                    rule="SUBPROCESS_TIMEOUT",
                    message=f"subprocess.{subprocess_call}() must include a bounded `timeout=`.",
                )
        elif subprocess_call == "Popen":
            self._add_issue(
                node=node,
                severity="WARN",
                rule="SUBPROCESS_POPEN",
                message="Prefer subprocess.run(..., timeout=...); if using Popen, ensure communicate/wait is time-bounded and pipes are closed.",
            )

        if id(node) not in self._calls_in_with_context:
            if self._is_file_open_call(node):
                self._add_issue(
                    node=node,
                    severity="WARN",
                    rule="FILE_OPEN_WITHOUT_WITH",
                    message="File opened without a context manager; prefer `with ...:` or ensure close() in finally.",
                )
            if self._is_path_write_call(node):
                self._add_issue(
                    node=node,
                    severity="WARN",
                    rule="NON_ATOMIC_WRITE",
                    message="Path.write_text/write_bytes are not atomic; prefer a temp+replace pattern when overwriting important files.",
                )

        self.generic_visit(node)

    def _resolve_subprocess_call(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id in self._subprocess_modules:
                return node.func.attr

        if isinstance(node.func, ast.Name):
            imported = self._subprocess_functions.get(node.func.id)
            if imported is not None:
                return imported

        return None

    @staticmethod
    def _call_has_keyword(node: ast.Call, keyword: str) -> bool:
        for kw in node.keywords:
            if kw.arg is None:
                continue
            if kw.arg == keyword:
                return True
        return False

    @staticmethod
    def _is_file_open_call(node: ast.Call) -> bool:
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            return True

        if isinstance(node.func, ast.Attribute) and node.func.attr == "open":
            fileish_keywords = {"encoding", "newline", "errors", "buffering"}
            if any((kw.arg in fileish_keywords) for kw in node.keywords if kw.arg is not None):
                return True
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                return True

        return False

    @staticmethod
    def _is_path_write_call(node: ast.Call) -> bool:
        return isinstance(node.func, ast.Attribute) and node.func.attr in {"write_text", "write_bytes"}


def _scan_file(*, path: Path, repo_root: Path) -> list[Issue]:
    try:
        source = _read_python_source(path)
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError) as exc:
        return [
            Issue(
                path=path,
                line=1,
                col=1,
                severity="ERROR",
                rule="READ_FAILED",
                message=str(exc),
            )
        ]
    except SyntaxError as exc:
        return [
            Issue(
                path=path,
                line=exc.lineno or 1,
                col=(exc.offset or 0) + 1,
                severity="ERROR",
                rule="SYNTAX_ERROR",
                message=exc.msg,
            )
        ]

    subprocess_modules, subprocess_functions = _collect_subprocess_aliases(tree)
    visitor = _SafetyVisitor(
        path=path,
        repo_root=repo_root,
        subprocess_modules=subprocess_modules,
        subprocess_functions=subprocess_functions,
    )
    visitor.visit(tree)
    return visitor.issues


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Lightweight Python safety checks (no deps).")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repo root to scan (defaults to the parent of scripts/).",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit non-zero when warnings are present.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    _configure_logging(verbose=bool(args.verbose))

    repo_root = args.root.resolve()
    if not repo_root.exists():
        logger.error("ERROR %s:1:1 ROOT_MISSING Root does not exist.", repo_root)
        return 2

    python_files = _iter_python_files(repo_root)
    if not python_files:
        logger.info("No Python files found under: %s", repo_root)
        return 0

    issues: list[Issue] = []
    for path in python_files:
        issues.extend(_scan_file(path=path, repo_root=repo_root))

    issues.sort(key=lambda i: (str(i.path).lower(), i.line, i.col, i.severity, i.rule))

    errors = 0
    warnings = 0
    for issue in issues:
        if issue.severity == "ERROR":
            errors += 1
        else:
            warnings += 1
        logger.info(issue.format(repo_root=repo_root))

    logger.info("Summary: %s error(s), %s warning(s)", errors, warnings)

    if errors > 0:
        return 1
    if warnings > 0 and args.fail_on_warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

