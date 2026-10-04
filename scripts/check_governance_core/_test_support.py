from __future__ import annotations

from pathlib import Path

from scripts.check_governance_core._docs_checks import (
    DOCS_POLICY_PATH, _documentation_line_limit, _required_project_paths,
)
from scripts.check_governance_core._documents import parse_markdown, router_filename
from scripts.check_governance_core._engine import DEFAULT_GOVERNANCE_ROOT
from scripts.check_governance_core import run_checks


REPOSITORY_ROOT = DEFAULT_GOVERNANCE_ROOT


def write(path: Path, value: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        with path.open("wb") as handle:
            handle.write(value)
    else:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(value)


def live_orchestration_text() -> str:
    return (REPOSITORY_ROOT / "Orchestration.md").read_text(encoding="utf-8")


def live_principles_section() -> str:
    text = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    document = parse_markdown(text)
    title = "Fundamental Principles (Highest Repository Authority)"
    section = document.section(title, level=2)
    if section is None:
        raise ValueError("Live AGENTS.md must declare one Fundamental Principles section")
    return f"## {title}\n\n{section.text}\n"


def install_root_authorities(root: Path) -> None:
    write(
        root / "AGENTS.md",
        "# Agent\n\n<!-- orchestration-authority: Orchestration.md -->\n\n"
        + live_principles_section(),
    )
    write(root / "Orchestration.md", live_orchestration_text())


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


def live_foundations() -> tuple[str, dict[str, str]]:
    result = run_checks({"repo_root": str(REPOSITORY_ROOT), "governance_root": str(REPOSITORY_ROOT)})
    governance = next((record for record in result.get("checks", []) if record["id"] == "governance"), None)
    if governance is None or governance["status"] != "PASSED":
        errors = governance["errors"] if governance is not None else result["errors"]
        raise ValueError("Live foundation validation failed: " + "; ".join(errors))
    document = parse_markdown((REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    section = document.section("Mandatory Foundations", level=2)
    assert section is not None
    # Only the public checker validates membership; the parsed markers are mutation data.
    values, _errors = section.markers("foundation-authority:")
    declared = dict(value.split("=", 1) for value in values)
    return "## Mandatory Foundations\n" + section.text + "\n", declared


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
