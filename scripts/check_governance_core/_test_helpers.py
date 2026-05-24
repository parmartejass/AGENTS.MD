from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def write_minimal_change_record(repo_root: Path) -> None:
    record = {
        "change_id": "CR-test",
        "change_type": "chore",
        "summary": "Temporary test record.",
        "verification_commands": ["test command"],
        "invariants": ["test invariant"],
        "witnesses": [
            {
                "invariant_id": "INV-test",
                "signal": "test signal",
                "record_location": "test output",
                "pass_criteria": "test passes",
            }
        ],
        "ssot_owner_paths": ["tmp/test-owner"],
    }
    write_text(
        repo_root / "docs/project/change-records/test-record.json",
        json.dumps(record, indent=2) + "\n",
    )


def copy_vendored_governance_for_wrappers(source_root: Path, governance_root: Path) -> None:
    (governance_root / "scripts").mkdir(parents=True)
    for script_name in (
        "_governance_paths.ps1",
        "_python_check_runner.ps1",
        "check_agents_manifest.ps1",
        "check_change_records.ps1",
        "check_docs_ssot.ps1",
        "check_project_docs.ps1",
    ):
        shutil.copy2(source_root / "scripts" / script_name, governance_root / "scripts" / script_name)
    shutil.copytree(source_root / "scripts/check_governance_core", governance_root / "scripts/check_governance_core")
    shutil.copytree(source_root / "docs/agents/schemas", governance_root / "docs/agents/schemas")


def run_powershell_script(
    powershell: str | None,
    script_path: Path,
    *args: str,
    cwd: Path,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            powershell or "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            *args,
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
