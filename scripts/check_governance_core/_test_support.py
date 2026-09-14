from __future__ import annotations

from pathlib import Path

from scripts.check_governance_core._documents import parse_markdown
from scripts.check_governance_core.check_governance_core_main import run_checks


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


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
    relative = Path("docs/agents/25-docs-ssot-policy/docs-ssot-policy.md")
    write(root / relative, (REPOSITORY_ROOT / relative).read_bytes())
    return root / relative


def live_foundations() -> tuple[str, dict[str, str]]:
    result = run_checks({"repo_root": str(REPOSITORY_ROOT), "governance_root": str(REPOSITORY_ROOT)})
    governance = next((record for record in result.get("checks", []) if record["id"] == "governance"), None)
    if governance is None or governance["status"] != "PASSED":
        errors = governance["errors"] if governance is not None else result["errors"]
        raise ValueError("Live foundation validation failed: " + "; ".join(errors))
    document = parse_markdown((REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    section = document.section("Mandatory Foundations", level=2)
    assert section is not None
    # Only the public checker validates membership; these literals are mutation data.
    prefix = "<!-- foundation-authority: "
    declared = dict(
        line.removeprefix(prefix).removesuffix(" -->").split("=", 1)
        for _number, line in section.operative_lines if line.startswith(prefix)
    )
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
