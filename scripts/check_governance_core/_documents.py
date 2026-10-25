from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

from scripts.check_governance_core._python_modules import PythonModule, parse_python


_HEADING = re.compile(r"^[ ]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$")
# CommonMark leaf-block starts that end the previous block inside a paragraph run.
_BLOCK_START = re.compile(r"^[ \t]*(?:[-*+][ \t]|[0-9]{1,9}[.)][ \t]|\||>)")
_NUMBERED_FOLDER = re.compile(r"^[0-9]{2}-(?P<name>.+)$")
_DATED_FOLDER = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$")
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
# Root authority and docs-tree locations, relative to their root; every handler reuses these.
CONSTITUTION_PATH = "AGENTS.md"
ORCHESTRATION_PATH = "Orchestration.md"
DOCS_ROOT = Path("docs")
AGENTS_DOCS_ROOT = DOCS_ROOT / "agents"
PROJECT_DOCS_ROOT = DOCS_ROOT / "project"
SKILL_FILENAME = "SKILL.md"


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line: int


@dataclass(frozen=True)
class FencedBlock:
    info: str
    lines: tuple[str, ...]
    closed: bool


@dataclass(frozen=True)
class MarkdownDocument:
    text: str
    operative_lines: tuple[tuple[int, str], ...]
    headings: tuple[Heading, ...]
    fences: tuple[FencedBlock, ...] = ()

    def section(self, title: str, *, level: int | None = None) -> "MarkdownDocument | None":
        matches = [
            heading
            for heading in self.headings
            if heading.title == title and (level is None or heading.level == level)
        ]
        if len(matches) != 1:
            return None
        start = matches[0]
        end_line = len(self.text.splitlines()) + 1
        for heading in self.headings:
            if heading.line > start.line and heading.level <= start.level:
                end_line = heading.line
                break
        body = "\n".join(
            line for line_no, line in self.operative_lines if start.line < line_no < end_line
        )
        return parse_markdown(body)

    def markers(self, token: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return operative ``<!-- token value -->`` marker values and malformed-line errors.

        The grammar is exact: single spaces around the token and a value without
        surrounding whitespace. Blockquoted lines are non-operative examples, like
        fenced and indented code.
        """

        pattern = re.compile(rf"<!-- {re.escape(token)} (\S(?:.*\S)?) -->")
        values: list[str] = []
        errors: list[str] = []
        for _number, line in self.operative_lines:
            if token not in line or is_quoted(line):
                continue
            match = pattern.fullmatch(line.strip())
            if match is None:
                errors.append(f"malformed {token.rstrip(':')} marker: {line.strip()!r}")
            else:
                values.append(match.group(1))
        return tuple(values), tuple(errors)

    def declaration_value(self, key: str) -> str | None:
        """Return the value of the one operative ``key: value`` line, or None when absent, repeated or malformed."""

        declarations = [
            line for _number, line in self.operative_lines
            if line.strip().startswith(key)
        ]
        match = re.fullmatch(rf"{re.escape(key)}: (\S+)", declarations[0]) if len(declarations) == 1 else None
        return match.group(1) if match else None

    def positive_integer_declaration(self, key: str, owner_label: str) -> tuple[int | None, list[str]]:
        value = self.declaration_value(key)
        if value is None or re.fullmatch(r"[1-9][0-9]*", value) is None:
            return None, [f"{owner_label} must declare exactly one positive {key}"]
        try:
            return int(value), []
        except ValueError:
            return None, [f"{owner_label} {key} is not a supported integer"]


class DocumentStore:
    def __init__(self) -> None:
        self._resolved: dict[Path, Path] = {}
        self._text: dict[Path, tuple[str | None, str | None]] = {}
        self._markdown: dict[Path, tuple[MarkdownDocument | None, str | None]] = {}
        self._python: dict[tuple[Path, str], tuple[PythonModule | None, SyntaxError | None]] = {}

    def read_text(self, path: Path) -> tuple[str | None, str | None]:
        resolved = self._resolve(path)
        if resolved in self._text:
            return self._text[resolved]
        try:
            with resolved.open("r", encoding="utf-8", newline="") as handle:
                value = handle.read()
            result: tuple[str | None, str | None] = (value, None)
        except FileNotFoundError:
            result = (None, f"Missing required file: {path}")
        except UnicodeDecodeError as exc:
            result = (None, f"Invalid UTF-8 in {path}: byte {exc.start}")
        except OSError as exc:
            result = (None, f"Unable to read {path}: {exc}")
        self._text[resolved] = result
        return result

    def markdown(self, path: Path) -> tuple[MarkdownDocument | None, str | None]:
        resolved = self._resolve(path)
        if resolved in self._markdown:
            return self._markdown[resolved]
        text, error = self.read_text(path)
        result = (parse_markdown(text), None) if text is not None else (None, error)
        self._markdown[resolved] = result
        return result

    def python_module(self, path: Path, text: str) -> tuple[PythonModule | None, SyntaxError | None]:
        """Parse one decoded Python source once per run; consumers share the tree and its import index."""

        key = (self._resolve(path), text)
        if key not in self._python:
            self._python[key] = parse_python(text, str(path))
        return self._python[key]

    def _resolve(self, path: Path) -> Path:
        if path not in self._resolved:
            self._resolved[path] = path.resolve()
        return self._resolved[path]


def is_quoted(line: str) -> bool:
    """Blockquoted lines are non-operative examples, like fenced and indented code."""

    return line.lstrip().startswith(">")


def parse_markdown(text: str) -> MarkdownDocument:
    """Parse once: CommonMark fences (a closing fence repeats the opening character, at least as long, with no
    info string; a backtick info string has no backtick), indented code, operative lines and headings."""

    operative: list[tuple[int, str]] = []
    headings: list[Heading] = []
    fences: list[FencedBlock] = []
    opening: tuple[str, int, str] | None = None
    body: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        fence = _FENCE.match(line)
        if fence and opening is None and not (fence.group(1)[0] == "`" and "`" in fence.group(2)):
            opening, body = (fence.group(1)[0], len(fence.group(1)), fence.group(2).strip()), []
            continue
        if opening is not None:
            if fence and fence.group(1)[0] == opening[0] and len(fence.group(1)) >= opening[1] and not fence.group(2).strip():
                fences.append(FencedBlock(opening[2], tuple(body), True))
                opening = None
            else:
                body.append(line)
            continue
        if line.startswith("    ") or line.startswith("\t"):
            continue
        operative.append((line_no, line))
        match = _HEADING.match(line)
        if match:
            headings.append(Heading(len(match.group(1)), match.group(2).strip(), line_no))
    if opening is not None:
        fences.append(FencedBlock(opening[2], tuple(body), False))
    return MarkdownDocument(text, tuple(operative), tuple(headings), tuple(fences))


def paragraphs(lines: Iterable[tuple[int, str]]) -> tuple[tuple[tuple[int, str], ...], ...]:
    """Split numbered lines into runs of consecutive non-blank lines; a blank or skipped line ends a run."""

    runs: list[tuple[tuple[int, str], ...]] = []
    run: list[tuple[int, str]] = []
    for line_no, line in lines:
        if run and (not line.strip() or line_no != run[-1][0] + 1):
            runs.append(tuple(run))
            run = []
        if line.strip():
            run.append((line_no, line))
    return (*runs, tuple(run)) if run else tuple(runs)


def blocks(lines: Iterable[tuple[int, str]]) -> tuple[tuple[tuple[int, str], ...], ...]:
    """Split paragraph runs at each heading, list item, table row or blockquote, so wrapped lines stay joined."""

    result: list[tuple[tuple[int, str], ...]] = []
    for run in paragraphs(lines):
        start = 0
        for index in range(1, len(run) + 1):
            if index == len(run) or any(pattern.match(run[index][1]) for pattern in (_BLOCK_START, _HEADING)) \
                    or _HEADING.match(run[index - 1][1]):
                result.append(run[start:index])
                start = index
    return tuple(result)


def authority_name(folder_name: str) -> str:
    numbered = _NUMBERED_FOLDER.match(folder_name)
    if numbered:
        return numbered.group("name")
    if _DATED_FOLDER.match(folder_name):
        return "evidence"
    return folder_name


def router_filename(folder_name: str) -> str:
    return f"{authority_name(folder_name)}_index.md"


def primary_leaf_filename(folder_name: str) -> str:
    return "evidence.md" if _DATED_FOLDER.match(folder_name) else f"{authority_name(folder_name)}.md"


def normalize_link(raw_target: str) -> str | None:
    target = unquote(raw_target.strip())
    if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith(("//", "/")):
        return None
    target = target.split("?", 1)[0].split("#", 1)[0].replace("\\", "/")
    while target.startswith("./"):
        target = target[2:]
    parts = [part for part in target.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts):
        return None
    return "/".join(parts) or None


def router_targets(document: MarkdownDocument) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    targets: list[str] = []
    content = [(line_no, line) for line_no, line in document.operative_lines if line.strip()]
    if not content or not _HEADING.match(content[0][1]):
        return targets, ["Router must begin with a Markdown heading."]
    for line_no, line in content[1:]:
        stripped = line.strip()
        if not stripped.startswith("- "):
            errors.append(f"line {line_no}: router must remain routing-only (title and route bullets)")
            continue
        if "Required when:" not in stripped:
            errors.append(f"line {line_no}: route is missing 'Required when:'")
        match = _LINK.search(stripped)
        if not match:
            errors.append(f"line {line_no}: route is missing a Markdown link")
            continue
        target = normalize_link(match.group(1))
        if target is None:
            errors.append(f"line {line_no}: invalid or out-of-bounds route target {match.group(1)!r}")
            continue
        targets.append(target)
    return targets, errors


def frontmatter_end(lines: list[str]) -> int:
    """Return the number of leading lines a closed ``---`` frontmatter block occupies, or 0."""

    if not lines or lines[0].strip() != "---":
        return 0
    return next((index + 1 for index in range(1, len(lines)) if lines[index].strip() == "---"), 0)


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    end = frontmatter_end(lines)
    values: dict[str, str] = {}
    for line in lines[1:end - 1] if end else ():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip() or "<nested>"
    return values


def declared_doc_types(policy_text: str) -> tuple[str, ...]:
    """Read the allowed doc_type domain from the docs-policy owner example."""

    matches = re.findall(r"^[ ]{0,3}doc_type:\s*([a-z]+(?:\|[a-z]+)+)\s*$", policy_text, re.MULTILINE)
    if not matches:
        return ()
    values = tuple(dict.fromkeys(matches[0].split("|")))
    return values if all(match.split("|") == list(values) for match in matches) else ()
