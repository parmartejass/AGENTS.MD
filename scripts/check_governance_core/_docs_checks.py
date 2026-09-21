from __future__ import annotations

import re
from pathlib import Path

from scripts.check_governance_core._documents import (
    DocumentStore,
    MarkdownDocument,
    declared_doc_types,
    frontmatter,
    primary_leaf_filename,
    router_filename,
    router_targets,
)
from scripts.check_governance_core._inventory import RepositoryInventory


def _policy_document(
    governance_root: Path, store: DocumentStore, inventory: RepositoryInventory,
) -> tuple[MarkdownDocument | None, list[str]]:
    path, error = inventory.validate_file(
        governance_root / "docs/agents/governance/documentation/documentation.md"
    )
    if error:
        return None, [error]
    assert path is not None
    document, error = store.markdown(path)
    return document, [error] if error else []


def _documentation_line_limit(document: MarkdownDocument) -> tuple[int | None, list[str]]:
    return document.positive_integer_declaration("documentation_line_limit", "Docs policy")

def _physical_lines(text: str) -> int:
    return text.count("\n") + int(bool(text) and not text.endswith("\n"))


def _router(store: DocumentStore, path: Path) -> tuple[list[str], list[str]]:
    document, read_error = store.markdown(path)
    if read_error:
        return [], [read_error]
    assert document is not None
    targets, errors = router_targets(document)
    return targets, [f"{path}: {error}" for error in errors]


def check_docs(
    repo_root: Path,
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return [f"Missing required docs directory: {docs_root}"], []
    markdown_files, markdown_error = inventory.markdown_files(repo_root)
    if markdown_error:
        return [markdown_error], []
    policy, policy_errors = _policy_document(governance_root, store, inventory)
    errors.extend(policy_errors)
    allowed_doc_types = declared_doc_types(policy.text if policy else "")
    if not allowed_doc_types:
        errors.append("Docs policy does not declare one consistent doc_type domain")
    limit, limit_errors = _documentation_line_limit(policy) if policy else (None, [])
    errors.extend(limit_errors)
    for path in markdown_files:
        text, read_error = store.read_text(path)
        if read_error:
            errors.append(read_error)
        elif text is not None and limit is not None and _physical_lines(text) > limit:
            errors.append(f"{path}: documentation exceeds owner-declared {limit}-line limit ({_physical_lines(text)} physical lines)")

    tree, inventory_error = inventory.tree_entries(docs_root)
    if inventory_error:
        return [inventory_error, *errors], []
    entries = tree
    children_by_parent: dict[Path, list] = {}
    for entry in entries:
        children_by_parent.setdefault(entry.path.parent, []).append(entry)
    directories = [docs_root, *(entry.path for entry in entries if entry.is_directory and entry.path != docs_root)]
    for directory in directories:
        router_name = router_filename(directory.name)
        router_path = directory / router_name
        targets, route_errors = _router(store, router_path)
        errors.extend(route_errors)
        if route_errors and not router_path.is_file():
            continue
        direct_children = [
            entry
            for entry in children_by_parent.get(directory, ())
            if entry.path.name != router_name
            and not entry.path.name.startswith(".")
        ]
        leaves = [
            entry.path
            for entry in direct_children
            if not entry.is_directory
            and entry.path.suffix.lower() == ".md"
            and entry.path.name != "SKILL.md"
        ]
        if leaves:
            expected = primary_leaf_filename(directory.name)
            if expected not in {item.name for item in leaves}:
                errors.append(f"{directory}: missing canonical public leaf {expected!r}")
        for child in direct_children:
            accepted = {child.path.name}
            if child.is_directory:
                accepted.add(f"{child.path.name}/{router_filename(child.path.name)}")
            if not any(target in accepted for target in targets):
                errors.append(f"{router_path}: missing route for direct child {child.path.name!r}")
        allowed_targets = {
            target
            for child in direct_children
            for target in (
                {child.path.name, f"{child.path.name}/{router_filename(child.path.name)}"}
                if child.is_directory
                else {child.path.name}
            )
        }
        for target in targets:
            if target not in allowed_targets:
                errors.append(f"{router_path}: route target is not a direct child contract: {target}")

    for path in (entry.path for entry in entries if not entry.is_directory and entry.path.suffix.lower() == ".md"):
        if path.name in {router_filename(path.parent.name), "SKILL.md"}:
            continue
        text, read_error = store.read_text(path)
        if read_error:
            errors.append(read_error)
            continue
        assert text is not None
        header = frontmatter(text)
        for field in ("doc_type", "ssot_owner", "update_trigger"):
            if not header.get(field):
                errors.append(f"{path}: missing non-empty frontmatter field {field}")
        if header.get("doc_type") and header["doc_type"] not in allowed_doc_types:
            errors.append(f"{path}: unsupported doc_type {header['doc_type']!r}")
    return errors, []


def _required_project_paths(policy: MarkdownDocument) -> tuple[tuple[str, ...], list[str]]:
    section = policy.section("Required project-doc branches", level=2)
    if section is None:
        return (), ["Docs policy must declare exactly one Required project-doc branches section"]
    branches: list[str] = []
    seen: set[str] = set()
    errors: list[str] = []
    for _number, line in section.operative_lines:
        if not line.strip():
            continue
        match = re.fullmatch(r"- `([^`]+/)`: .+", line)
        value = match.group(1)[:-1] if match else ""
        if not value or any(char in value for char in '/\\:<>"|?*') or any(ord(char) < 32 for char in value) or value != value.strip() or value != value.rstrip(" .") or value in {".", ".."}:
            errors.append(f"Docs policy has invalid required project branch: {line!r}")
        elif value.casefold() in seen:
            errors.append(f"Docs policy has duplicate required project branch: {value}")
        else:
            branches.append(value)
            seen.add(value.casefold())
    if not branches:
        errors.append("Docs policy must declare at least one required project branch")
    project = Path("docs/project")
    paths = [str(project / router_filename(project.name)).replace("\\", "/")]
    for branch in branches:
        paths.extend((project / branch / name).as_posix() for name in (router_filename(branch), primary_leaf_filename(branch)))
    return (() if errors else tuple(paths)), errors


def check_project_docs(
    repo_root: Path,
    governance_root: Path,
    governance_rel: str,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> list[str]:
    errors: list[str] = []
    docs_root = repo_root / "docs"
    _markdown_files, markdown_error = inventory.markdown_files(docs_root)
    if markdown_error:
        return [markdown_error]
    policy, policy_errors = _policy_document(governance_root, store, inventory)
    if policy_errors:
        return policy_errors
    assert policy is not None
    required, declaration_errors = _required_project_paths(policy)
    errors.extend(declaration_errors)
    for relative in required:
        _path, error = inventory.validate_file(repo_root / relative)
        if error:
            errors.append(f"Missing or invalid required project doc: {relative}: {error}")

    readme_path, readme_validation_error = inventory.validate_file(repo_root / "README.md")
    if readme_validation_error:
        errors.append(readme_validation_error)
        readme = None
        readme_error = None
    else:
        assert readme_path is not None
        readme, readme_error = store.read_text(readme_path)
    if readme_error:
        errors.append(readme_error)
    elif readme is not None:
        assert readme is not None
        prefix = f"{governance_rel.rstrip('/')}/" if governance_rel else ""
        for reference in (
            "AGENTS.md",
            "docs/project/project_index.md",
            f"{prefix}scripts/check_governance_core/check_governance_core_main.py",
        ):
            if reference.casefold() not in readme.casefold():
                errors.append(f"README.md must reference {reference}")
        if "## Checks" not in readme:
            errors.append("README.md must contain a Checks section")

    project_root = repo_root / "docs/project"
    project_router = project_root / router_filename(project_root.name)
    project_targets, route_errors = _router(store, project_router)
    errors.extend(route_errors)
    if project_root.is_dir():
        tree, inventory_error = inventory.tree_entries(docs_root)
        if inventory_error:
            return [*errors, inventory_error]
        entries = tuple(
            entry for entry in tree if entry.path == project_root or project_root in entry.path.parents
        )
        for branch in (
            entry.path
            for entry in entries
            if entry.is_directory and entry.path.parent == project_root
        ):
            branch_router_name = router_filename(branch.name)
            if f"{branch.name}/{branch_router_name}" not in project_targets:
                errors.append(f"{project_router}: missing branch route {branch.name}/{branch_router_name}")
            branch_router = branch / branch_router_name
            targets, branch_errors = _router(store, branch_router)
            errors.extend(branch_errors)
            if not branch_errors:
                for leaf in (
                    entry.path
                    for entry in entries
                    if not entry.is_directory
                    and entry.path.parent == branch
                    and entry.path.suffix.lower() == ".md"
                ):
                    if leaf.name != branch_router_name and leaf.name not in targets:
                        errors.append(f"{branch_router}: orphan project doc {leaf.name}")
                for target in targets:
                    if target.lower().endswith(".md") and not (branch / target).is_file():
                        errors.append(f"{branch_router}: route target does not exist: {target}")
    return errors
