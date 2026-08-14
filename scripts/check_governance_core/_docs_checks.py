from __future__ import annotations

from pathlib import Path

from scripts.check_governance_core._documents import (
    DocumentStore,
    code_paths,
    declared_doc_types,
    frontmatter,
    primary_leaf_filename,
    router_filename,
    router_targets,
)
from scripts.check_governance_core._inventory import RepositoryInventory


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
    _markdown_files, markdown_error = inventory.markdown_files(docs_root)
    if markdown_error:
        return [markdown_error], []
    policy = governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
    policy_text, policy_error = store.read_text(policy)
    if policy_error:
        errors.append(policy_error)
        policy_text = ""
    allowed_doc_types = declared_doc_types(policy_text or "")
    if not allowed_doc_types:
        errors.append(f"Docs policy does not declare one consistent doc_type domain: {policy}")

    tree, inventory_error = inventory.tree_entries(docs_root)
    if inventory_error:
        return [inventory_error, *errors], []
    entries = tuple(entry for entry in tree if entry.path == docs_root or docs_root in entry.path.parents)
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
            for entry in entries
            if entry.path.parent == directory
            and entry.path.name != router_name
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


def _required_project_paths(agents_document) -> tuple[str, ...]:
    section = agents_document.section("Documentation SSOT Policy (Hard Gate)", level=2)
    if section is None:
        return ()
    values = code_paths((line for _line_no, line in section.operative_lines), prefix="docs/project/")
    return tuple(dict.fromkeys(value for value in values if value.endswith(".md")))


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
    agents_path, agents_validation_error = inventory.validate_file(governance_root / "AGENTS.md")
    if agents_validation_error:
        return [agents_validation_error]
    assert agents_path is not None
    agents, read_error = store.markdown(agents_path)
    if read_error:
        return [read_error]
    assert agents is not None
    required = _required_project_paths(agents)
    if not required:
        errors.append("AGENTS.md Documentation SSOT Policy does not expose required project-doc paths")
    for relative in required:
        if not (repo_root / relative).is_file():
            errors.append(f"Missing required project doc: {relative}")

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
