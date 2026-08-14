from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from scripts.check_governance_core import _git_capture
from scripts.check_governance_core._docs_checks import check_docs, check_project_docs
from scripts.check_governance_core._documents import DocumentStore, routed_markdown_corpus
from scripts.check_governance_core._folder_architecture import check_folder_architecture
from scripts.check_governance_core._governance_checks import (
    GovernanceContract,
    check_governance,
    resolve_governance_contract,
)
from scripts.check_governance_core._manifest import validate_manifest
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._python_safety import check_python_safety
from scripts.check_governance_core._repository_checks import check_repository


@dataclass(frozen=True)
class CheckContext:
    repo_root: Path
    governance_root: Path
    governance_rel: str
    store: DocumentStore
    inventory: RepositoryInventory
    contract: GovernanceContract
    strict_safety: bool


Check = Callable[[CheckContext], tuple[list[str], list[str]]]


def _governance(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_governance(context.governance_root, context.store, context.contract), []


def _manifest(context: CheckContext) -> tuple[list[str], list[str]]:
    _data, errors = validate_manifest(
        context.governance_root,
        context.store,
        context.inventory,
        context.contract.root_authorities,
    )
    return errors, []


def _docs(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_docs(context.repo_root, context.governance_root, context.store, context.inventory)


def _project_docs(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_project_docs(
        context.repo_root,
        context.governance_root,
        context.governance_rel,
        context.store,
        context.inventory,
    ), []


def _repository(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_repository(
        context.repo_root,
        context.store,
        context.inventory,
        enforce_tracked_ignored=context.repo_root == context.governance_root,
    ), []


def _folder_architecture(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_folder_architecture(context.governance_root, context.store, context.inventory)


def _python_safety(context: CheckContext) -> tuple[list[str], list[str]]:
    return check_python_safety(
        context.repo_root,
        context.inventory,
        fail_on_warnings=context.strict_safety,
        reviewed_popen_paths=frozenset(
            {Path(inspect.getfile(_git_capture)).resolve()}
        ),
    )


CHECK_REGISTRY: tuple[tuple[str, Check], ...] = (
    ("governance", _governance),
    ("manifest", _manifest),
    ("docs", _docs),
    ("project_docs", _project_docs),
    ("repository", _repository),
    ("folder_architecture", _folder_architecture),
    ("python_safety", _python_safety),
)

MODE_CHECKS = {
    "full": tuple(check_id for check_id, _check in CHECK_REGISTRY),
    "docs": ("docs",),
    "project_docs": ("project_docs",),
}


def _resolve_roots(request: dict[str, object]) -> tuple[Path, Path, str, RepositoryInventory]:
    script_root = Path(__file__).resolve().parent
    governance_value = request.get("governance_root")
    repo_value = request.get("repo_root")
    governance_request = Path(str(governance_value)).expanduser() if governance_value else script_root.parent.parent
    repo_request = Path(str(repo_value)).expanduser() if repo_value else governance_request
    if repo_value is None and governance_request.name == ".governance":
        raise ValueError("repo_root is required for a vendored .governance checkout")
    inventory = RepositoryInventory(repo_request)
    if inventory.root_error:
        raise ValueError(inventory.root_error)
    assert inventory.repository_root is not None
    repo_root = inventory.repository_root
    governance_root, governance_error = inventory.resolve_scan_root(governance_request)
    if governance_error:
        raise ValueError(f"governance_root validation failed: {governance_error}")
    assert governance_root is not None
    relative = governance_root.relative_to(repo_root).as_posix()
    return repo_root, governance_root, "" if relative in {"", "."} else relative, inventory


def execute(request: dict[str, object]) -> dict[str, object]:
    mode = request.get("mode", "full")
    if mode not in MODE_CHECKS:
        raise ValueError(f"mode must be one of {', '.join(MODE_CHECKS)}")
    if request.get("fail_on_safety_warnings") and mode != "full":
        raise ValueError("fail_on_safety_warnings is valid only in full mode")
    repo_root, governance_root, governance_rel, inventory = _resolve_roots(request)
    store = DocumentStore()
    inventory.tree_entries(repo_root if mode == "full" else repo_root / "docs")
    contract = resolve_governance_contract(governance_root, store, inventory)
    context = CheckContext(
        repo_root=repo_root,
        governance_root=governance_root,
        governance_rel=governance_rel,
        store=store,
        inventory=inventory,
        contract=contract,
        strict_safety=bool(request.get("fail_on_safety_warnings", False)),
    )
    selected = set(MODE_CHECKS[str(mode)])
    records: list[dict[str, object]] = []
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for check_id, check in CHECK_REGISTRY:
        if check_id not in selected:
            continue
        try:
            errors, warnings = check(context)
        except Exception as exc:
            errors = [f"{check_id} check failed unexpectedly: {type(exc).__name__}: {exc}"]
            warnings = []
        records.append(
            {
                "id": check_id,
                "status": "FAILED" if errors else "PASSED",
                "errors": errors,
                "warnings": warnings,
            }
        )
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    planned = [check_id for check_id, _check in CHECK_REGISTRY if check_id in selected]
    failed = [str(record["id"]) for record in records if record["status"] == "FAILED"]
    executed = [str(record["id"]) for record in records if record["status"] == "PASSED"]
    return {
        "api_version": 1,
        "status": "FAILED" if all_errors else "PASSED",
        "repo_root": str(repo_root),
        "governance_root": str(governance_root),
        "checks": records,
        "planned": planned,
        "eligible": planned,
        "executed": executed,
        "skipped": [],
        "failed": failed,
        "errors": all_errors,
        "warnings": all_warnings,
    }


def resolve_documents_request(request: dict[str, object]) -> dict[str, object]:
    """Resolve the complete canonical governance-document router topology."""

    _repo_root, governance_root, _governance_rel, inventory = _resolve_roots(request)
    store = DocumentStore()
    agents_path, agents_validation_error = inventory.validate_file(governance_root / "AGENTS.md")
    if agents_validation_error:
        return {"api_version": 1, "status": "FAILED", "documents": [], "errors": [agents_validation_error]}
    assert agents_path is not None
    _agents_text, agents_error = store.read_text(agents_path)
    if agents_error:
        return {"api_version": 1, "status": "FAILED", "documents": [], "errors": [agents_error]}
    markdown, markdown_error = inventory.markdown_files(governance_root / "docs/agents")
    if markdown_error:
        return {"api_version": 1, "status": "FAILED", "documents": [], "errors": [markdown_error]}
    leaves, errors = routed_markdown_corpus(
        governance_root,
        store,
        markdown,
        reserved_paths=(agents_path,),
    )
    if errors:
        return {"api_version": 1, "status": "FAILED", "documents": [], "errors": errors}
    return {
        "api_version": 1,
        "status": "PASSED",
        "documents": ["AGENTS.md", *leaves],
        "errors": [],
    }
