from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Iterable

from scripts.check_governance_core._documents import AGENTS_DOCS_ROOT, DocumentStore, router_filename, router_targets


MAX_ROUTED_DOCUMENTS = 10_000


def routed_markdown_corpus(
    governance_root: Path,
    store: DocumentStore,
    available_markdown: Iterable[Path],
    *,
    reserved_paths: Iterable[Path] = (),
) -> tuple[tuple[str, ...], list[str]]:
    """Resolve terminal Markdown leaves from the canonical agents router topology."""

    docs_root = governance_root / AGENTS_DOCS_ROOT
    start = docs_root / router_filename(docs_root.name)
    available_by_key: dict[str, Path] = {}
    directory_keys: set[str] = set()
    for path in available_markdown:
        try:
            key = path.relative_to(governance_root).as_posix()
        except ValueError:
            continue
        available_by_key[key] = path
        current = path.parent
        while current == docs_root or docs_root in current.parents:
            directory_keys.add(current.relative_to(governance_root).as_posix())
            if current == docs_root:
                break
            current = current.parent
    folded_directory_keys = {key.casefold() for key in directory_keys}
    errors: list[str] = []
    leaves: list[str] = []
    visited_routers: set[Path] = set()
    active_routers: set[Path] = set()
    visited_leaves: set[Path] = set()
    identities: dict[tuple[int, int], Path] = {}

    def register_identity(path: Path) -> bool:
        try:
            metadata = path.stat(follow_symlinks=False)
        except OSError as exc:
            errors.append(f"Unable to inspect routed governance document {path}: {exc}")
            return False
        identity = (metadata.st_dev, metadata.st_ino)
        prior = identities.get(identity)
        if prior is not None and prior != path:
            errors.append(f"Governance document aliases another routed path: {path} -> {prior}")
            return False
        identities[identity] = path
        return True

    for reserved in reserved_paths:
        register_identity(reserved)

    def visit(router: Path) -> None:
        if router in active_routers:
            errors.append(f"Governance docs router cycle detected at {router}")
            return
        if router in visited_routers:
            errors.append(f"Governance docs router is referenced more than once: {router}")
            return
        router_key = router.relative_to(governance_root).as_posix()
        canonical_router = available_by_key.get(router_key)
        if canonical_router is None:
            errors.append(f"Governance docs router is missing or aliased: {router}")
            return
        router = canonical_router
        if not register_identity(router):
            return
        if len(visited_routers) + len(visited_leaves) >= MAX_ROUTED_DOCUMENTS:
            errors.append(f"Governance docs topology exceeded {MAX_ROUTED_DOCUMENTS} Markdown documents")
            return
        visited_routers.add(router)
        active_routers.add(router)
        document, read_error = store.markdown(router)
        if read_error:
            errors.append(read_error)
            active_routers.remove(router)
            return
        assert document is not None
        targets, route_errors = router_targets(document)
        errors.extend(f"{router}: {error}" for error in route_errors)
        seen_targets: set[str] = set()
        for value in targets:
            key = value.casefold()
            if key in seen_targets:
                errors.append(f"{router}: duplicate route target {value}")
                continue
            seen_targets.add(key)
            relative = PurePosixPath(value)
            candidate = router.parent.joinpath(*relative.parts)
            try:
                candidate.relative_to(docs_root)
            except ValueError:
                errors.append(f"{router}: route target escapes governance docs root: {value}")
                continue
            candidate_key = candidate.relative_to(governance_root).as_posix()
            if candidate_key in directory_keys:
                visit(candidate / router_filename(candidate.name))
                continue
            if candidate_key.casefold() in folded_directory_keys:
                errors.append(f"{router}: route target has noncanonical spelling: {value}")
                continue
            if candidate.suffix.lower() != ".md":
                if candidate.is_dir():
                    errors.append(
                        f"{router}: directory route is missing its canonical child router: {value}"
                    )
                elif not candidate.exists():
                    errors.append(f"{router}: route target does not exist: {value}")
                continue
            canonical_candidate = available_by_key.get(candidate_key)
            if canonical_candidate is None:
                errors.append(
                    f"{router}: Markdown route target is missing, aliased, unreadable, or noncanonical: {value}"
                )
                continue
            candidate = canonical_candidate
            if candidate.name == router_filename(candidate.parent.name):
                visit(candidate)
                continue
            if candidate in visited_leaves:
                errors.append(f"Governance document is routed more than once: {candidate}")
                continue
            if not register_identity(candidate):
                continue
            _leaf, read_error = store.markdown(candidate)
            if read_error:
                errors.append(read_error)
                continue
            visited_leaves.add(candidate)
            leaves.append(candidate.relative_to(governance_root).as_posix())
        active_routers.remove(router)

    visit(start)
    return tuple(leaves), errors
