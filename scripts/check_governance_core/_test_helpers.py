from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def copy_vendored_governance_for_wrappers(source_root: Path, governance_root: Path) -> None:
    (governance_root / "scripts").mkdir(parents=True)
    for script_name in (
        "_governance_paths.ps1",
        "_python_check_runner.ps1",
        "check_agents_manifest.ps1",
        "check_docs_ssot.ps1",
        "check_project_docs.ps1",
    ):
        shutil.copy2(source_root / "scripts" / script_name, governance_root / "scripts" / script_name)
    shutil.copytree(source_root / "scripts/check_governance_core", governance_root / "scripts/check_governance_core")


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
