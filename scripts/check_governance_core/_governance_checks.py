from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from scripts.check_governance_core._documents import DocumentStore, MarkdownDocument, resolve_declared_file
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._orchestration import validate_orchestration_contract


CONSTITUTION_PATH = "AGENTS.md"
ORCHESTRATION_PATH = "Orchestration.md"
ROOT_AUTHORITIES = (CONSTITUTION_PATH, ORCHESTRATION_PATH)
_AUTHORITY_MARKER = re.compile(r"<!--\s*orchestration-authority:\s*([^>]+?)\s*-->")
_PRINCIPLES_START = "<!-- fundamental-principles:start -->"
_PRINCIPLES_END = "<!-- fundamental-principles:end -->"
_PRINCIPLES_RANGE = re.compile(r"`### FP-([0-9]{2})` through `### FP-([0-9]{2})`")
_PRINCIPLE_HEADING = re.compile(r"### FP-([0-9]{2})")


@dataclass(frozen=True)
class GovernanceContract:
    root_authorities: tuple[str, ...]
    errors: tuple[str, ...]


def resolve_governance_contract(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> GovernanceContract:
    agents_path, validation_error = inventory.validate_file(governance_root / CONSTITUTION_PATH)
    if validation_error:
        return GovernanceContract(ROOT_AUTHORITIES, (validation_error,))
    assert agents_path is not None
    document, read_error = store.markdown(agents_path)
    if read_error:
        return GovernanceContract(ROOT_AUTHORITIES, (read_error,))
    assert document is not None

    marker_lines = [
        line.strip()
        for _line_no, line in document.operative_lines
        if "orchestration-authority:" in line
    ]
    markers = [match for line in marker_lines if (match := _AUTHORITY_MARKER.fullmatch(line))]
    if len(marker_lines) != 1 or len(markers) != 1:
        return GovernanceContract(
            ROOT_AUTHORITIES,
            ("AGENTS.md must contain exactly one operative orchestration-authority marker",),
        )
    declared = markers[0].group(1).strip()
    if declared != ORCHESTRATION_PATH:
        return GovernanceContract(
            ROOT_AUTHORITIES,
            (f"AGENTS.md orchestration authority must be exactly {ORCHESTRATION_PATH}",),
        )

    orchestration_path, validation_error = inventory.validate_file(
        governance_root / ORCHESTRATION_PATH
    )
    if validation_error:
        return GovernanceContract(ROOT_AUTHORITIES, (validation_error,))
    assert orchestration_path is not None
    orchestration_text, read_error = store.read_text(orchestration_path)
    if read_error:
        return GovernanceContract(ROOT_AUTHORITIES, (read_error,))
    assert orchestration_text is not None
    return GovernanceContract(
        ROOT_AUTHORITIES, tuple(validate_orchestration_contract(orchestration_text))
    )



@dataclass(frozen=True)
class FoundationContract:
    role_paths: tuple[tuple[str, str], ...]
    errors: tuple[str, ...]

    @property
    def authorities(self) -> tuple[str, ...]:
        return tuple(path for _role, path in self.role_paths)

    def path_for(self, role: str) -> str:
        return dict(self.role_paths)[role]


_FOUNDATION_SECTION = "Mandatory Foundations"
_FOUNDATION_ROLES = frozenset({"constitution", "orchestration", "coding_principles", "docs_policy"})
_FOUNDATION_MARKER = re.compile(r"<!-- foundation-authority: ([a-z_]+)=([^<>]+) -->")


def _foundation_lines(document: MarkdownDocument) -> tuple[list[str], list[str]]:
    lines = [line for _number, line in document.operative_lines if not line.lstrip().startswith(">")]
    return (
        [line for line in lines if line.lstrip().startswith("foundation_contract_version")],
        [line for line in lines if "<!-- foundation-authority" in line],
    )


def _foundation_declarations(document: MarkdownDocument) -> tuple[dict[str, str], list[str]]:
    """Parse only the AGENTS-owned membership schema; paths have no defaults."""

    prefix = "AGENTS.md Mandatory Foundations: "
    section = document.section(_FOUNDATION_SECTION, level=2)
    if section is None:
        return {}, [prefix + "restore exactly one canonical owner section"]
    versions, marker_lines = _foundation_lines(document)
    errors: list[str] = []
    if (versions, marker_lines) != _foundation_lines(section):
        errors.append(prefix + "place all operative declarations inside the owner section")
    if versions != ["foundation_contract_version: 1"]:
        errors.append(prefix + "declare exactly one supported foundation_contract_version: 1")
    declared: dict[str, str] = {}
    seen_paths: set[str] = set()
    for line in marker_lines:
        marker = _FOUNDATION_MARKER.fullmatch(line)
        if marker is None:
            errors.append(prefix + f"malformed foundation-authority marker: {line!r}")
            continue
        role, path = marker.groups()
        if role not in _FOUNDATION_ROLES:
            errors.append(prefix + f"unsupported foundation role: {role}")
        elif role in declared:
            errors.append(prefix + f"duplicate foundation role: {role}")
        else:
            declared[role] = path
        if path.casefold() in seen_paths:
            errors.append(prefix + f"duplicate foundation path: {path}")
        seen_paths.add(path.casefold())
    missing = sorted(_FOUNDATION_ROLES - declared.keys())
    if missing:
        errors.append(prefix + "missing required foundation role(s): " + ", ".join(missing))
    return ({} if errors else declared), errors


def resolve_foundations(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
    contract: GovernanceContract,
) -> FoundationContract:
    """Resolve unconditional startup owners separately from the research corpus."""

    if contract.errors:
        return FoundationContract((), contract.errors)
    agents_path, error = inventory.validate_file(governance_root / CONSTITUTION_PATH)
    if error:
        return FoundationContract((), (error,))
    assert agents_path is not None
    document, error = store.markdown(agents_path)
    if error:
        return FoundationContract((), (error,))
    assert document is not None
    declared, errors = _foundation_declarations(document)
    if errors:
        return FoundationContract((), tuple(errors))
    for role, expected in zip(("constitution", "orchestration"), contract.root_authorities):
        if declared[role] != expected:
            errors.append(f"AGENTS.md foundation {role} must identify its existing owner: {expected}")
    for role, value in declared.items():
        if Path(value).suffix.lower() != ".md":
            errors.append(f"AGENTS.md foundation {role} must identify a Markdown file: {value}")
            continue
        path, error = resolve_declared_file(governance_root, value)
        if error is None:
            assert path is not None
            path, error = inventory.validate_file(governance_root / value)
        if error is None:
            assert path is not None
            _text, error = store.read_text(path)
        if error:
            errors.append(f"AGENTS.md foundation {role}: {error}")
    return FoundationContract(() if errors else tuple(declared.items()), tuple(errors))


def _validate_principles(document: MarkdownDocument) -> list[str]:
    """Check the AGENTS-owned shape, without asserting exact text or compliance."""

    prefix = "AGENTS.md Fundamental Principles: "
    section = document.section("Fundamental Principles (Highest Repository Authority)", level=2)
    if section is None:
        return [prefix + "restore exactly one canonical owner section"]
    markers = {
        marker: [number for number, line in document.operative_lines if line == marker]
        for marker in (_PRINCIPLES_START, _PRINCIPLES_END)
    }
    if any(len(numbers) != 1 for numbers in markers.values()):
        return [prefix + "restore exactly one standalone operative start/end block"]
    start = markers[_PRINCIPLES_START][0]
    end = markers[_PRINCIPLES_END][0]
    section_lines = section.text.splitlines()
    if start >= end or _PRINCIPLES_START not in section_lines or _PRINCIPLES_END not in section_lines:
        return [prefix + "place the start/end block in order inside its owner section"]
    declarations = _PRINCIPLES_RANGE.findall("\n".join(section_lines[:section_lines.index(_PRINCIPLES_START)]))
    if len(declarations) != 1:
        return [prefix + "restore one owner-declared `### FP-NN` through `### FP-NN` range"]
    first, last = map(int, declarations[0])
    if first > last:
        return [prefix + "restore an ascending owner-declared identifier range"]
    lines = document.text.splitlines()
    operative = {number for number, _line in document.operative_lines}
    if any(number not in operative and lines[number - 1].strip() for number in range(start + 1, end)):
        return [prefix + "restore operative headings and paragraphs; code examples cannot define principles"]
    body_start, body_end = start, end - 1
    while body_start < body_end and not lines[body_start].strip():
        body_start += 1
    while body_end > body_start and not lines[body_end - 1].strip():
        body_end -= 1
    parts = re.split(r"\n(?:[ \t]*\n)+", "\n".join(lines[body_start:body_end]))
    expected = list(range(first, last + 1))
    if len(parts) != len(expected) * 2:
        return [prefix + "restore every declared identifier with exactly one blank-line-delimited MUST paragraph"]
    for identifier, heading, paragraph in zip(expected, parts[::2], parts[1::2]):
        match = _PRINCIPLE_HEADING.fullmatch(heading)
        if match is None or int(match.group(1)) != identifier:
            return [prefix + f"restore consecutive unique headings; expected ### FP-{identifier:02d}"]
        if not paragraph.startswith("MUST ") or not paragraph[5:].strip():
            return [prefix + f"restore one paragraph beginning MUST for FP-{identifier:02d}"]
    return []


def check_governance(
    governance_root: Path,
    contract: GovernanceContract,
    store: DocumentStore,
    inventory: RepositoryInventory,
    foundations: FoundationContract,
) -> list[str]:
    errors = list(contract.errors)
    if not errors:
        agents_path, validation_error = inventory.validate_file(governance_root / CONSTITUTION_PATH)
        if validation_error:
            errors.append(validation_error)
        else:
            assert agents_path is not None
            document, read_error = store.markdown(agents_path)
            if read_error:
                errors.append(read_error)
            else:
                assert document is not None
                errors.extend(_validate_principles(document))
    for required in ("agents-manifest.yaml", "docs/agents/agents_index.md"):
        if not (governance_root / required).is_file():
            errors.append(f"Missing governance authority surface: {required}")
    return list(dict.fromkeys((*errors, *foundations.errors)))
