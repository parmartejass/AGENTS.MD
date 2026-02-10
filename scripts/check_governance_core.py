#!/usr/bin/env python3
"""
Cross-platform governance checks.

This script mirrors the core PowerShell checks:
1) check_agents_manifest.ps1
2) check_docs_ssot.ps1
3) check_project_docs.ps1
4) check_repo_hygiene.ps1
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

logger = logging.getLogger(__name__)
_GIT_LS_FILES_TIMEOUT_SEC = 30


def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _resolve_path(path: str | None, default: Path) -> Path:
    if not path:
        return default.resolve()
    return Path(path).expanduser().resolve()


def _context(
    repo_root_arg: str | None, governance_root_arg: str | None, script_root: Path
) -> Tuple[Path, Path, str]:
    governance_root = _resolve_path(governance_root_arg, script_root.parent)
    repo_root = _resolve_path(repo_root_arg, governance_root)

    if not governance_root.is_dir():
        raise RuntimeError(f"Governance root does not exist or is not a directory: {governance_root}")
    if not repo_root.is_dir():
        raise RuntimeError(f"Repo root does not exist or is not a directory: {repo_root}")

    if repo_root_arg is None and governance_root.name == ".governance":
        raise RuntimeError(
            "RepoRoot is required when running from a vendored governance submodule. "
            "Use --repo-root <target repo root> (for example: --repo-root .)."
        )

    try:
        rel_path = governance_root.relative_to(repo_root)
        rel = "." if str(rel_path) == "." else rel_path.as_posix()
    except ValueError:
        rel = os.path.relpath(governance_root, repo_root).replace("\\", "/")

    governance_rel = "" if rel in {".", ""} else rel
    return repo_root, governance_root, governance_rel


def _check_agents_manifest(governance_root: Path) -> List[str]:
    errors: List[str] = []
    manifest = governance_root / "agents-manifest.yaml"
    if not manifest.is_file():
        return [f"Missing agents-manifest.yaml at governance root: {manifest}"]

    lines = manifest.read_text(encoding="utf-8").splitlines()
    in_path_list = False
    path_list_indent = 0
    path_list_key: str | None = None

    in_profiles = False
    profiles_indent = 0
    profile_key_indent: int | None = None
    current_profile: str | None = None

    paths_by_list: Dict[str, List[str]] = {}

    for idx, line in enumerate(lines, start=1):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))

        if in_profiles:
            if indent <= profiles_indent and re.match(r"^[A-Za-z0-9_]+:\s*", trimmed):
                in_profiles = False
                profiles_indent = 0
                profile_key_indent = None
                current_profile = None
            else:
                m = re.match(r"^([A-Za-z0-9_]+):\s*$", trimmed)
                if m:
                    if profile_key_indent is None:
                        if indent > profiles_indent:
                            profile_key_indent = indent
                            current_profile = m.group(1)
                    elif indent == profile_key_indent:
                        current_profile = m.group(1)

        if not in_profiles:
            m_profiles = re.match(r"^(\s*)profiles:\s*$", line)
            if m_profiles:
                in_profiles = True
                profiles_indent = len(m_profiles.group(1))
                profile_key_indent = None
                current_profile = None

        if in_path_list:
            is_list_item = trimmed.startswith("- ")
            is_new_key = (not is_list_item) and indent <= path_list_indent and re.match(
                r"^[A-Za-z0-9_]+:\s*", trimmed
            )
            if is_new_key:
                in_path_list = False
                path_list_indent = 0
                path_list_key = None

        if not in_path_list:
            m_key = re.match(r"^(\s*)(default_inject|fallback_inject|inject):\s*$", line)
            if m_key:
                in_path_list = True
                path_list_indent = len(m_key.group(1))
                key = m_key.group(2)
                if key == "inject" and in_profiles and current_profile:
                    path_list_key = f"profiles.{current_profile}.inject"
                else:
                    path_list_key = key
                continue

        if not in_path_list:
            continue

        if not trimmed.startswith("- "):
            continue

        dq = re.match(r'^-\s+"([^"]+)"\s*$', trimmed)
        sq = re.match(r"^-\s+'([^']+)'\s*$", trimmed)
        if dq:
            value = dq.group(1)
        elif sq:
            value = sq.group(1)
        else:
            errors.append(f"Unquoted path in {path_list_key} at line {idx}: {trimmed}")
            continue

        if not value.strip():
            errors.append(f"Empty path value in {path_list_key} at line {idx}")
            continue

        assert path_list_key is not None
        paths_by_list.setdefault(path_list_key, []).append(value)

    default_inject = paths_by_list.get("default_inject", [])
    if not default_inject:
        errors.append("Missing or empty default_inject list in agents-manifest.yaml")
    elif "AGENTS.md" not in default_inject:
        errors.append("default_inject must include AGENTS.md")

    all_paths: Set[str] = set()
    for list_key, values in paths_by_list.items():
        seen: Set[str] = set()
        for value in values:
            if value in seen:
                errors.append(f"Duplicate path in {list_key}: {value}")
            else:
                seen.add(value)
                all_paths.add(value)

    for rel in sorted(all_paths):
        if not (governance_root / rel).exists():
            errors.append(f"Manifest references missing path: {rel}")

    return errors


def _check_docs_ssot(repo_root: Path, governance_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return errors, ["No docs/ folder found. Skipping docs SSOT checks."]

    policy_path = governance_root / "docs/agents/25-docs-ssot-policy.md"
    if not policy_path.is_file():
        return errors + [
            f"docs/agents/25-docs-ssot-policy.md missing in governance root: {policy_path}"
        ], warnings

    policy_lines = policy_path.read_text(encoding="utf-8").splitlines()
    enum_line = next((ln for ln in policy_lines if re.match(r"^doc_type:\s*.+\|.+", ln)), None)
    if not enum_line:
        return errors + [
            "Doc header enum not found in docs/agents/25-docs-ssot-policy.md "
            "(expected 'doc_type: ...|...')."
        ], warnings

    allowed_doc_types = {p.strip() for p in re.sub(r"^doc_type:\s*", "", enum_line).split("|") if p.strip()}

    for md_file in docs_root.rglob("*.md"):
        rel = md_file.relative_to(docs_root).as_posix()
        if rel == "index.md" or re.match(r"^[^/]+/index\.md$", rel):
            continue

        head = md_file.read_text(encoding="utf-8").splitlines()[:25]
        doc_type_line = next((ln for ln in head if ln.startswith("doc_type:")), None)
        if doc_type_line is None:
            errors.append(f"Missing doc header (doc_type) in: {md_file}")
        else:
            doc_type = re.sub(r"^doc_type:\s*", "", doc_type_line).strip()
            if doc_type not in allowed_doc_types:
                errors.append(f"Invalid doc_type '{doc_type}' in: {md_file}")

        if not any(ln.startswith("ssot_owner:") for ln in head):
            errors.append(f"Missing doc header (ssot_owner) in: {md_file}")
        if not any(ln.startswith("update_trigger:") for ln in head):
            errors.append(f"Missing doc header (update_trigger) in: {md_file}")

    for doc_file in docs_root.rglob("*"):
        if not doc_file.is_file():
            continue
        rel = doc_file.relative_to(docs_root).as_posix()
        if "/generated/" in f"/{rel}/":
            continue
        text = doc_file.read_text(encoding="utf-8", errors="replace")
        if re.search(r"defaults?:\s*$|default value", text, flags=re.IGNORECASE | re.MULTILINE):
            warnings.append(
                "Docs mention defaults/default value. Ensure docs reference config keys by identifier, "
                "not copied literal values."
            )
            break

    return errors, warnings


def _check_project_docs(repo_root: Path, governance_rel_path: str) -> List[str]:
    errors: List[str] = []
    required_files = [
        "README.md",
        "docs/project/index.md",
        "docs/project/goal.md",
        "docs/project/rules.md",
        "docs/project/architecture.md",
        "docs/project/learning.md",
    ]
    for rel in required_files:
        if not (repo_root / rel).is_file():
            errors.append(f"Missing required file: {rel}")

    governance_prefix = f"{governance_rel_path.rstrip('/')}/" if governance_rel_path else ""

    readme = repo_root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        required_refs = [
            "docs/project/index.md",
            "AGENTS.md",
            f"{governance_prefix}scripts/check_docs_ssot.ps1",
            f"{governance_prefix}scripts/check_agents_manifest.ps1",
            f"{governance_prefix}scripts/check_project_docs.ps1",
            f"{governance_prefix}scripts/check_repo_hygiene.ps1",
            f"{governance_prefix}scripts/check_change_records.ps1",
            f"{governance_prefix}scripts/check_python_safety.py",
        ]
        for ref in required_refs:
            if ref not in readme_text:
                errors.append(f"README.md must reference: {ref}")

    proj_index = repo_root / "docs/project/index.md"
    if proj_index.is_file():
        index_text = proj_index.read_text(encoding="utf-8")
        for ref in [
            "docs/project/goal.md",
            "docs/project/rules.md",
            "docs/project/architecture.md",
            "docs/project/learning.md",
        ]:
            if ref not in index_text:
                errors.append(f"docs/project/index.md must reference {ref}")

    return errors


def _check_repo_hygiene(repo_root: Path) -> List[str]:
    errors: List[str] = []
    if not (repo_root / ".git").exists():
        return [f"Repo root does not appear to be a git repository: {repo_root}"]

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
            timeout=_GIT_LS_FILES_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        return ["git is required for hygiene checks."]
    except subprocess.TimeoutExpired:
        return [
            f"git ls-files timed out after {_GIT_LS_FILES_TIMEOUT_SEC}s for repo root: {repo_root}"
        ]
    except subprocess.CalledProcessError:
        return [f"git ls-files failed for repo root: {repo_root}"]

    for raw in result.stdout.splitlines():
        path = raw.strip()
        if not path:
            continue
        norm = path.replace("\\", "/")

        if re.search(r"(^|/)__pycache__(/|$)", norm):
            errors.append(f"Tracked Python cache dir/file: {path}")
            continue
        if norm.endswith(".pyc") or norm.endswith(".pyo"):
            errors.append(f"Tracked Python bytecode: {path}")
            continue
        if re.search(r"(^|/)\.DS_Store$", norm) or re.search(r"(^|/)Thumbs\.db$", norm):
            errors.append(f"Tracked OS noise file: {path}")
            continue
        if norm.startswith("templates/python-dual-entry/tests/output/") and (
            norm != "templates/python-dual-entry/tests/output/.gitkeep"
        ):
            errors.append(f"Tracked template output file (should be generated/ignored): {path}")

    return errors


def main(argv: Sequence[str]) -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(
        description="Run cross-platform governance checks for manifest/docs/project-docs/hygiene."
    )
    parser.add_argument("--repo-root", help="Target repo root (default: governance root).")
    parser.add_argument(
        "--governance-root",
        help="Governance root that contains AGENTS.md and agents-manifest.yaml "
        "(default: parent of this script).",
    )
    args = parser.parse_args(argv)

    script_root = Path(__file__).resolve().parent
    try:
        repo_root, governance_root, governance_rel = _context(
            args.repo_root, args.governance_root, script_root
        )
    except RuntimeError as err:
        logger.error("ERROR: %s", err)
        return 1

    total_errors = 0

    manifest_errors = _check_agents_manifest(governance_root)
    if manifest_errors:
        for issue in manifest_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(manifest_errors)
    else:
        logger.info("Agents manifest checks passed.")

    docs_errors, docs_warnings = _check_docs_ssot(repo_root, governance_root)
    if docs_errors:
        for issue in docs_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(docs_errors)
    else:
        logger.info("Docs SSOT checks passed.")
    for warn in docs_warnings:
        logger.warning("WARNING: %s", warn)

    project_errors = _check_project_docs(repo_root, governance_rel)
    if project_errors:
        for issue in project_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(project_errors)
    else:
        logger.info("Project docs checks passed.")

    hygiene_errors = _check_repo_hygiene(repo_root)
    if hygiene_errors:
        for issue in hygiene_errors:
            logger.error("ERROR: %s", issue)
        total_errors += len(hygiene_errors)
    else:
        logger.info("Repo hygiene checks passed.")

    if total_errors > 0:
        logger.error("Governance core checks failed: %s issue(s).", total_errors)
        return 1

    logger.info("Governance core checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
