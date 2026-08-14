from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.check_governance_core._documents import DocumentStore, resolve_declared_file
from scripts.check_governance_core._inventory import RepositoryInventory


OWNER_SECTION = "Assigned-Lead Authority Routing Procedure (Hard Gate)"
ROOT_AUTHORITY_LABEL = "Read and follow these authorities:"
_CONTRACT_WITNESS = re.compile(
    r"<!--\s*governance-root-contract:\s*authorities=([0-9]+)\s+sha256=([0-9a-f]{64})\s*-->"
)


@dataclass(frozen=True)
class GovernanceContract:
    root_authorities: tuple[str, ...]
    canonical_delegation: str
    errors: tuple[str, ...]


def governance_contract_digest(authorities: tuple[str, ...], delegation: str) -> str:
    canonical = "\0".join((*authorities, delegation)).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def resolve_governance_contract(
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> GovernanceContract:
    path, validation_error = inventory.validate_file(governance_root / "AGENTS.md")
    if validation_error:
        return GovernanceContract((), "", (validation_error,))
    assert path is not None
    document, read_error = store.markdown(path)
    if read_error:
        return GovernanceContract((), "", (read_error,))
    assert document is not None
    section = document.section(OWNER_SECTION, level=2)
    if section is None:
        return GovernanceContract((), "", (f"AGENTS.md must contain exactly one ## {OWNER_SECTION} section",))

    errors: list[str] = []
    lines = list(section.operative_lines)
    labels = [index for index, (_line_no, line) in enumerate(lines) if line.strip() == ROOT_AUTHORITY_LABEL]
    authorities: list[str] = []
    if len(labels) != 1:
        errors.append(f"AGENTS.md {OWNER_SECTION} must contain exactly one {ROOT_AUTHORITY_LABEL!r} label")
    else:
        for _line_no, line in lines[labels[0] + 1 :]:
            stripped = line.strip()
            match = re.fullmatch(r"- `([^`]+)`", stripped)
            if match:
                authorities.append(match.group(1))
                continue
            if stripped:
                break
        if not authorities:
            errors.append("AGENTS.md root-authority block must contain at least one backtick-delimited path")

    quotes = section.blockquotes()
    delegation = quotes[0] if len(quotes) == 1 else ""
    if len(quotes) != 1 or not quotes[0]:
        errors.append("AGENTS.md assigned-lead owner section must contain exactly one operative blockquote")

    witness_lines = [line.strip() for _line_no, line in lines if "governance-root-contract:" in line]
    witnesses = [match for line in witness_lines if (match := _CONTRACT_WITNESS.fullmatch(line))]
    if len(witness_lines) != 1 or len(witnesses) != 1:
        errors.append("AGENTS.md assigned-lead owner section must contain exactly one valid governance-root-contract witness")
    elif authorities and delegation:
        expected_count = int(witnesses[0].group(1))
        expected_digest = witnesses[0].group(2)
        if len(authorities) != expected_count:
            errors.append(
                "AGENTS.md root-authority membership count does not match its owner witness: "
                f"expected {expected_count}, found {len(authorities)}"
            )
        actual_digest = governance_contract_digest(tuple(authorities), delegation)
        if actual_digest != expected_digest:
            errors.append("AGENTS.md root-authority order or canonical delegation does not match its owner witness")

    seen: set[str] = set()
    seen_targets: list[Path] = []
    for value in authorities:
        key = value.casefold()
        if key in seen:
            errors.append(f"AGENTS.md root-authority block contains duplicate path: {value}")
        seen.add(key)
        _candidate, path_error = resolve_declared_file(governance_root, value)
        if path_error:
            errors.append(f"AGENTS.md root authority {path_error}")
            continue
        assert _candidate is not None
        if any(_candidate.samefile(target) for target in seen_targets):
            errors.append(f"AGENTS.md root authority aliases an earlier path: {value}")
        seen_targets.append(_candidate)
    return GovernanceContract(tuple(authorities), delegation, tuple(errors))


def check_governance(governance_root: Path, store: DocumentStore, contract: GovernanceContract) -> list[str]:
    errors = list(contract.errors)
    for required in ("agents-manifest.yaml", "docs/agents/agents_index.md"):
        if not (governance_root / required).is_file():
            errors.append(f"Missing governance authority surface: {required}")
    return errors
