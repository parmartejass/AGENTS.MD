from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import unquote


_HEADING = re.compile(r"^[ ]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$")
_NUMBERED_FOLDER = re.compile(r"^[0-9]{2}-(?P<name>.+)$")
_DATED_FOLDER = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$")
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MAX_ROUTED_DOCUMENTS = 10_000


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line: int


@dataclass(frozen=True)
class MarkdownDocument:
    text: str
    operative_lines: tuple[tuple[int, str], ...]
    headings: tuple[Heading, ...]

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

    def blockquotes(self) -> tuple[str, ...]:
        values: list[str] = []
        for _line_no, line in self.operative_lines:
            match = re.match(r"^[ ]{0,3}>[ ]?(.*)$", line)
            if match:
                values.append(match.group(1).strip())
        return tuple(values)


class DocumentStore:
    def __init__(self) -> None:
        self._text: dict[Path, tuple[str | None, str | None]] = {}
        self._markdown: dict[Path, tuple[MarkdownDocument | None, str | None]] = {}

    def read_text(self, path: Path) -> tuple[str | None, str | None]:
        resolved = path.resolve()
        if resolved in self._text:
            return self._text[resolved]
        try:
            value = resolved.read_text(encoding="utf-8")
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
        resolved = path.resolve()
        if resolved in self._markdown:
            return self._markdown[resolved]
        text, error = self.read_text(path)
        result = (parse_markdown(text), None) if text is not None else (None, error)
        self._markdown[resolved] = result
        return result


def parse_markdown(text: str) -> MarkdownDocument:
    operative: list[tuple[int, str]] = []
    headings: list[Heading] = []
    fence_char: str | None = None
    fence_length = 0
    for line_no, line in enumerate(text.splitlines(), start=1):
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence_char is not None or line.startswith("    ") or line.startswith("\t"):
            continue
        operative.append((line_no, line))
        match = _HEADING.match(line)
        if match:
            headings.append(Heading(len(match.group(1)), match.group(2).strip(), line_no))
    return MarkdownDocument(text, tuple(operative), tuple(headings))


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


def routed_markdown_corpus(
    governance_root: Path,
    store: DocumentStore,
    available_markdown: Iterable[Path],
    *,
    reserved_paths: Iterable[Path] = (),
) -> tuple[tuple[str, ...], list[str]]:
    """Resolve terminal Markdown leaves from the canonical agents router topology."""

    docs_root = governance_root / "docs/agents"
    start = docs_root / router_filename(docs_root.name)
    available_by_key: dict[str, Path] = {}
    directory_keys: set[str] = set()
    for path in available_markdown:
        try:
            key = path.relative_to(governance_root).as_posix()
        except ValueError:
            continue
        available_by_key[key] = path
        current = path.parent
        while current == docs_root or docs_root in current.parents:
            directory_keys.add(current.relative_to(governance_root).as_posix())
            if current == docs_root:
                break
            current = current.parent
    folded_directory_keys = {key.casefold() for key in directory_keys}
    errors: list[str] = []
    leaves: list[str] = []
    visited_routers: set[Path] = set()
    active_routers: set[Path] = set()
    visited_leaves: set[Path] = set()
    identities: dict[tuple[int, int], Path] = {}

    def register_identity(path: Path) -> bool:
        try:
            metadata = path.stat(follow_symlinks=False)
        except OSError as exc:
            errors.append(f"Unable to inspect routed governance document {path}: {exc}")
            return False
        identity = (metadata.st_dev, metadata.st_ino)
        prior = identities.get(identity)
        if prior is not None and prior != path:
            errors.append(f"Governance document aliases another routed path: {path} -> {prior}")
            return False
        identities[identity] = path
        return True

    for reserved in reserved_paths:
        register_identity(reserved)

    def visit(router: Path) -> None:
        if router in active_routers:
            errors.append(f"Governance docs router cycle detected at {router}")
            return
        if router in visited_routers:
            errors.append(f"Governance docs router is referenced more than once: {router}")
            return
        router_key = router.relative_to(governance_root).as_posix()
        canonical_router = available_by_key.get(router_key)
        if canonical_router is None:
            errors.append(f"Governance docs router is missing or aliased: {router}")
            return
        router = canonical_router
        if not register_identity(router):
            return
        if len(visited_routers) + len(visited_leaves) >= MAX_ROUTED_DOCUMENTS:
            errors.append(f"Governance docs topology exceeded {MAX_ROUTED_DOCUMENTS} Markdown documents")
            return
        visited_routers.add(router)
        active_routers.add(router)
        document, read_error = store.markdown(router)
        if read_error:
            errors.append(read_error)
            active_routers.remove(router)
            return
        assert document is not None
        targets, route_errors = router_targets(document)
        errors.extend(f"{router}: {error}" for error in route_errors)
        seen_targets: set[str] = set()
        for value in targets:
            key = value.casefold()
            if key in seen_targets:
                errors.append(f"{router}: duplicate route target {value}")
                continue
            seen_targets.add(key)
            relative = PurePosixPath(value)
            candidate = router.parent.joinpath(*relative.parts)
            try:
                candidate.relative_to(docs_root)
            except ValueError:
                errors.append(f"{router}: route target escapes governance docs root: {value}")
                continue
            candidate_key = candidate.relative_to(governance_root).as_posix()
            if candidate_key in directory_keys:
                visit(candidate / router_filename(candidate.name))
                continue
            if candidate_key.casefold() in folded_directory_keys:
                errors.append(f"{router}: route target has noncanonical spelling: {value}")
                continue
            if candidate.suffix.lower() != ".md":
                if candidate.is_dir():
                    errors.append(
                        f"{router}: directory route is missing its canonical child router: {value}"
                    )
                elif not candidate.exists():
                    errors.append(f"{router}: route target does not exist: {value}")
                continue
            canonical_candidate = available_by_key.get(candidate_key)
            if canonical_candidate is None:
                errors.append(
                    f"{router}: Markdown route target is missing, aliased, unreadable, or noncanonical: {value}"
                )
                continue
            candidate = canonical_candidate
            if candidate.name == router_filename(candidate.parent.name):
                visit(candidate)
                continue
            if candidate in visited_leaves:
                errors.append(f"Governance document is routed more than once: {candidate}")
                continue
            if not register_identity(candidate):
                continue
            _leaf, read_error = store.markdown(candidate)
            if read_error:
                errors.append(read_error)
                continue
            visited_leaves.add(candidate)
            leaves.append(candidate.relative_to(governance_root).as_posix())
        active_routers.remove(router)

    visit(start)
    return tuple(leaves), errors


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip() or "<nested>"
    return {}


def declared_doc_types(policy_text: str) -> tuple[str, ...]:
    """Read the allowed doc_type domain from the docs-policy owner example."""

    matches = re.findall(r"^[ ]{0,3}doc_type:\s*([a-z]+(?:\|[a-z]+)+)\s*$", policy_text, re.MULTILINE)
    if not matches:
        return ()
    values = tuple(dict.fromkeys(matches[0].split("|")))
    return values if all(match.split("|") == list(values) for match in matches) else ()


def code_paths(lines: Iterable[str], *, prefix: str) -> tuple[str, ...]:
    values: list[str] = []
    pattern = re.compile(r"`([^`]+)`")
    for line in lines:
        for value in pattern.findall(line):
            if value.startswith(prefix):
                values.append(value)
    return tuple(values)


def resolve_declared_file(root: Path, value: str) -> tuple[Path | None, str | None]:
    """Resolve an exactly spelled, contained owner-declared relative file path."""

    declared = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or ":" in value
        or declared.is_absolute()
        or declared.as_posix() != value
        or any(part in {"", ".", ".."} or part != part.rstrip(" .") for part in declared.parts)
    ):
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
    if not resolved.is_file():
        return None, f"declared path is not a file: {value}"
    return resolved, None
