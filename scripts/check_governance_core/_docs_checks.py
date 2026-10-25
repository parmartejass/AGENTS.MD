from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from scripts.check_governance_core._declared_paths import canonical_relative
from scripts.check_governance_core._documents import (
    AGENTS_DOCS_ROOT,
    CHANGELOG_DOCS_ROOT,
    CONSTITUTION_PATH,
    DOCS_ROOT,
    PROJECT_DOCS_ROOT,
    SKILL_FILENAME,
    DocumentStore,
    MarkdownDocument,
    declared_doc_types,
    frontmatter,
    primary_leaf_filename,
    router_filename,
    router_targets,
)
from scripts.check_governance_core._inventory import RepositoryInventory


# README guidance must name this package's runnable module launcher; deriving the name
# from the import identity keeps a second hardcoded package name out of the rule.
_LAUNCHER_REFERENCE = re.compile(rf"(?<![\w-])-m[ \t]+{re.escape(__package__)}(?!\w|\.\w)")
# Narrow docs modes resolve the docs-policy owner without the foundation declaration (architecture record).
DOCS_POLICY_PATH = AGENTS_DOCS_ROOT / "governance/documentation/documentation.md"


def _policy_document(
    governance_root: Path, store: DocumentStore, inventory: RepositoryInventory,
) -> tuple[MarkdownDocument | None, list[str]]:
    path, error = inventory.validate_file(governance_root / DOCS_POLICY_PATH)
    if error:
        return None, [error]
    assert path is not None
    document, error = store.markdown(path)
    return document, [error] if error else []


def _documentation_line_limit(document: MarkdownDocument) -> tuple[int | None, list[str]]:
    return document.positive_integer_declaration("documentation_line_limit", "Docs policy")


# Repeat report (documentation owner, Validation boundary): the predicates stay equal to the
# Phase-6 witness scan, so the warning-only report and its witness give the same result.
_REPEAT_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_REPEAT_DECLARATION = re.compile(r"^([a-z][a-z0-9_]*): \S.*$")
_REPEAT_SENTENCE_BREAK = re.compile(r"(?<=[.;!?])\s+")
_REPEAT_WORD = re.compile(r"[a-z0-9][a-z0-9_'-]*")
_REPEAT_OWNER = "(documentation owner, Validation boundary)"


def _repeat_parameters(policy: MarkdownDocument) -> tuple[tuple[re.Pattern[str], int, int] | None, list[str]]:
    """Read the three repeat-report declarations from the docs-policy owner, with no defaults."""

    terms = (policy.declaration_value("normative_repeat_terms") or "").split("|")
    errors = [] if all(terms) and len({term.casefold() for term in terms}) == len(terms) else [
        "Docs policy must declare exactly one normative_repeat_terms list of unique, non-empty, pipe-separated terms"
    ]
    words, word_errors = policy.positive_integer_declaration("normative_repeat_shingle_words", "Docs policy")
    percent, percent_errors = policy.positive_integer_declaration("normative_repeat_min_percent", "Docs policy")
    errors.extend(word_errors + percent_errors)
    if errors or words is None or percent is None:
        return None, errors
    return (re.compile(r"\b(" + "|".join(map(re.escape, terms)) + r")\b", re.IGNORECASE), words, percent), []


def _repeat_lines(text: str):
    """Yield numbered lines outside frontmatter, fences and blockquotes."""

    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        start = next((index + 1 for index in range(1, len(lines)) if lines[index].strip() == "---"), 0)
    in_fence = False
    for number, line in enumerate(lines[start:], start + 1):
        if _REPEAT_FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and not line.lstrip().startswith(">"):
            yield number, line


def _repeat_report(
    repo_root: Path, store: DocumentStore, inventory: RepositoryInventory, policy: MarkdownDocument,
) -> tuple[list[str], list[str]]:
    """Warn on normative sentences and declarations that repeat across tracked Markdown files."""

    parameters, errors = _repeat_parameters(policy)
    if parameters is None or not inventory.has_git_worktree(repo_root):
        return errors, []
    terms, size, percent = parameters
    tracked, error = inventory.tracked_paths(repo_root)
    if error:
        return [], [f"repeat: report not run: {error} {_REPEAT_OWNER}"]
    warnings: list[str] = []
    sentences: list[tuple[str, int, set[str]]] = []
    declarations: dict[str, list[tuple[str, int]]] = defaultdict(list)
    excluded = CHANGELOG_DOCS_ROOT.as_posix() + "/"
    for relative in sorted(tracked):
        path = PurePosixPath(relative)
        if (not relative.lower().endswith(".md") or relative.startswith(excluded)
                or path.name in {f"{path.parent.name}_index.md", router_filename(DOCS_ROOT.name)}):
            continue
        text, read_error = store.read_text(repo_root / relative)
        if read_error:
            warnings.append(f"repeat: report skipped {relative}: {read_error} {_REPEAT_OWNER}")
            continue
        assert text is not None
        for number, line in _repeat_lines(text):
            declaration = _REPEAT_DECLARATION.match(line.strip())
            if declaration and line == line.lstrip():
                declarations[declaration.group(1)].append((relative, number))
            for sentence in _REPEAT_SENTENCE_BREAK.split(line.strip()):
                words = _REPEAT_WORD.findall(sentence.lower().replace("`", "")) if terms.search(sentence) else []
                if len(words) >= size:
                    sentences.append((relative, number, {" ".join(words[i:i + size]) for i in range(len(words) - size + 1)}))
    index: dict[str, list[int]] = defaultdict(list)
    for number, (_relative, _line, shingles) in enumerate(sentences):
        for shingle in shingles:
            index[shingle].append(number)
    shared: Counter[tuple[int, int]] = Counter()
    for members in (members for members in index.values() if len(members) > 1):
        for position, first in enumerate(members):
            for second in members[position + 1:]:
                if sentences[first][0] != sentences[second][0]:
                    shared[(first, second)] += 1
    for (first, second), count in sorted(shared.items()):
        (file_a, line_a, set_a), (file_b, line_b, set_b) = sentences[first], sentences[second]
        share = count * 100 // min(len(set_a), len(set_b))
        if share >= percent:
            warnings.append(f"repeat: {file_a}:{line_a} and {file_b}:{line_b} share {share}% of their "
                            f"{size}-word phrases {_REPEAT_OWNER}")
    warnings.extend(
        f"repeat: declaration {key} in " + " and ".join(f"{file}:{line}" for file, line in sites) + f" {_REPEAT_OWNER}"
        for key, sites in sorted(declarations.items()) if len({file for file, _line in sites}) > 1
    )
    return [], warnings

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
    docs_root = repo_root / DOCS_ROOT
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
            and entry.path.name != SKILL_FILENAME
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
        if path.name in {router_filename(path.parent.name), SKILL_FILENAME}:
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
    if policy is None:
        return errors, []
    repeat_errors, warnings = _repeat_report(repo_root, store, inventory, policy)
    return errors + repeat_errors, warnings


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
        declared = canonical_relative(value)
        if declared is None or len(declared.parts) != 1:
            errors.append(f"Docs policy has invalid required project branch: {line!r}")
        elif value.casefold() in seen:
            errors.append(f"Docs policy has duplicate required project branch: {value}")
        else:
            branches.append(value)
            seen.add(value.casefold())
    if not branches:
        errors.append("Docs policy must declare at least one required project branch")
    project = PROJECT_DOCS_ROOT
    paths = [(project / router_filename(project.name)).as_posix()]
    for branch in branches:
        paths.extend((project / branch / name).as_posix() for name in (router_filename(branch), primary_leaf_filename(branch)))
    return (() if errors else tuple(paths)), errors


def check_project_docs(
    repo_root: Path,
    governance_root: Path,
    store: DocumentStore,
    inventory: RepositoryInventory,
) -> list[str]:
    errors: list[str] = []
    docs_root = repo_root / DOCS_ROOT
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
        for reference in (CONSTITUTION_PATH, (PROJECT_DOCS_ROOT / router_filename(PROJECT_DOCS_ROOT.name)).as_posix()):
            if reference.casefold() not in readme.casefold():
                errors.append(f"README.md must reference {reference}")
        if _LAUNCHER_REFERENCE.search(readme) is None:
            errors.append(f"README.md must reference the governance-core launcher: -m {__package__}")
        if "## Checks" not in readme:
            errors.append("README.md must contain a Checks section")

    project_root = repo_root / PROJECT_DOCS_ROOT
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
