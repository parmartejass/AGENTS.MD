from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.check_governance_core._docs_checks import (
    DOCS_POLICY_PATH, _documentation_line_limit, _required_project_paths,
)
from scripts.check_governance_core._documents import (
    AGENTS_DOCS_ROOT, CONSTITUTION_PATH, ORCHESTRATION_PATH, DocumentStore, parse_markdown, router_filename,
)
from scripts.check_governance_core._engine import DEFAULT_GOVERNANCE_ROOT
from scripts.check_governance_core._governance_checks import resolve_governance_contract
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core import run_checks


REPOSITORY_ROOT = DEFAULT_GOVERNANCE_ROOT
# Per-process memo of validated live foundations per root; reused only while every declared foundation file
# keeps the file state it had when validated.
_LIVE_FOUNDATIONS: dict[Path, tuple[tuple[tuple[int, ...], ...], str, dict[str, str]]] = {}
_CONTRACT_BLOCK = re.compile(r"(?ms)^```orchestration-contract\s*$\n(?P<body>.*?)^```\s*$")


def write(path: Path, value: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        with path.open("wb") as handle:
            handle.write(value)
    else:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(value)


def live_orchestration_text() -> str:
    return (REPOSITORY_ROOT / ORCHESTRATION_PATH).read_text(encoding="utf-8")


def live_principles_section() -> str:
    text = (REPOSITORY_ROOT / CONSTITUTION_PATH).read_text(encoding="utf-8")
    document = parse_markdown(text)
    title = "Fundamental Principles (Highest Repository Authority)"
    section = document.section(title, level=2)
    if section is None:
        raise ValueError("Live AGENTS.md must declare one Fundamental Principles section")
    return f"## {title}\n\n{section.text}\n"


def install_root_authorities(root: Path) -> None:
    write(
        root / CONSTITUTION_PATH,
        f"# Agent\n\n<!-- orchestration-authority: {ORCHESTRATION_PATH} -->\n\n"
        + live_principles_section(),
    )
    write(root / ORCHESTRATION_PATH, live_orchestration_text())


def install_docs_policy(root: Path) -> Path:
    write(root / DOCS_POLICY_PATH, (REPOSITORY_ROOT / DOCS_POLICY_PATH).read_bytes())
    return root / DOCS_POLICY_PATH


def docs_fixture(root: Path, governance_root: Path | None = None) -> tuple[Path, int]:
    """Install a minimal valid docs tree and README for docs and project-doc mode fixtures."""

    governance = governance_root or root
    install_root_authorities(governance)
    policy_path = install_docs_policy(governance)
    document = parse_markdown(policy_path.read_text(encoding="utf-8"))
    limit, errors = _documentation_line_limit(document)
    required, branch_errors = _required_project_paths(document)
    assert limit is not None and not errors and not branch_errors
    for relative in required:
        path = root / relative
        write(path, "# Router\n" if path.name.endswith("_index.md") else
              "---\ndoc_type: reference\nssot_owner: fixture\nupdate_trigger: fixture changes\n---\n\n# Fixture\n")
    for docs in {root / "docs", governance / "docs"}:
        directories = [docs, *(path for path in docs.rglob("*") if path.is_dir())]
        for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
            router = directory / router_filename(directory.name)
            children = sorted((path for path in directory.iterdir() if path != router), key=lambda path: path.name)
            links = [f"{path.name}/{router_filename(path.name)}" if path.is_dir() else path.name for path in children]
            write(router, "# Router\n\n" + "".join(f"- [{link}]({link}) - fixture. Required when: testing.\n" for link in links))
    write(root / "README.md", "# Fixture\n\nAGENTS.md docs/project/project_index.md\n\n## Checks\n"
          "python3 -B -m scripts.check_governance_core\n")
    return policy_path, limit


def docs_result(root: Path, governance: Path | None = None, mode: str = "docs"):
    return run_checks({"repo_root": root, "governance_root": governance or root, "mode": mode})


def _foundation_states(declared: dict[str, str]) -> tuple[tuple[int, ...], ...] | None:
    states = []
    for relative in (CONSTITUTION_PATH, *sorted(declared.values())):
        try:
            state = (REPOSITORY_ROOT / relative).stat()
        except OSError:
            return None
        states.append((state.st_dev, state.st_ino, state.st_size, state.st_mtime_ns, state.st_ctime_ns))
    return tuple(states)


def live_foundations() -> tuple[str, dict[str, str]]:
    """Return live membership after public validation; a changed state of any declared foundation re-validates."""

    cached = _LIVE_FOUNDATIONS.get(REPOSITORY_ROOT)
    if cached is not None and cached[0] == _foundation_states(cached[2]):
        return cached[1], dict(cached[2])
    result = run_checks({"repo_root": str(REPOSITORY_ROOT), "governance_root": str(REPOSITORY_ROOT)})
    governance = next((record for record in result.get("checks", []) if record["id"] == "governance"), None)
    if governance is None or governance["status"] != "PASSED":
        errors = governance["errors"] if governance is not None else result["errors"]
        raise ValueError("Live foundation validation failed: " + "; ".join(errors))
    document = parse_markdown((REPOSITORY_ROOT / CONSTITUTION_PATH).read_text(encoding="utf-8"))
    section = document.section("Mandatory Foundations", level=2)
    assert section is not None
    # Only the public checker validates membership; the parsed markers are mutation data.
    values, _errors = section.markers("foundation-authority:")
    declared = dict(value.split("=", 1) for value in values)
    rendered = "## Mandatory Foundations\n" + section.text + "\n"
    states = _foundation_states(declared)
    if states is not None:
        _LIVE_FOUNDATIONS[REPOSITORY_ROOT] = (states, rendered, declared)
    return rendered, dict(declared)


def install_foundations(root: Path) -> dict[str, str]:
    """Install full-check fixture authorities from their live membership owner."""

    section, declared = live_foundations()
    install_root_authorities(root)
    constitution = root / declared["constitution"]
    write(constitution, constitution.read_text(encoding="utf-8") + "\n" + section)
    for role, relative in declared.items():
        if role != "constitution":
            write(root / relative, (REPOSITORY_ROOT / relative).read_bytes())
    return declared


def orchestration_fixture(root: Path) -> None:
    install_root_authorities(root)
    write(root / AGENTS_DOCS_ROOT / router_filename(AGENTS_DOCS_ROOT.name), "# Agents\n")


def orchestration_contract_block(root: Path) -> re.Match[str]:
    match = _CONTRACT_BLOCK.search((root / ORCHESTRATION_PATH).read_text(encoding="utf-8"))
    assert match is not None
    return match


def orchestration_payload(root: Path) -> dict[str, object]:
    value = json.loads(orchestration_contract_block(root).group("body"))
    assert isinstance(value, dict)
    return value


def write_orchestration_payload(root: Path, value: dict[str, object]) -> None:
    path = root / ORCHESTRATION_PATH
    rendered = "```orchestration-contract\n" + json.dumps(value, indent=2) + "\n```"
    write(path, _CONTRACT_BLOCK.sub(lambda _match: rendered, path.read_text(encoding="utf-8"), count=1))


def orchestration_contract_errors(root: Path) -> tuple[str, ...]:
    return resolve_governance_contract(root, DocumentStore(), RepositoryInventory(root)).errors
