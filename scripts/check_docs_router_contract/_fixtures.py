from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import textwrap
from contextlib import contextmanager
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = SCRIPT_ROOT / "check_governance_core"
MODULE_PATH = MODULE_DIR / "_manifest_and_docs.py"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

SPEC = importlib.util.spec_from_file_location("_manifest_and_docs", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load docs-check module from {MODULE_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_docs_ssot = MODULE.check_docs_ssot
from _docs_routes import resolve_docs_router_filename  # noqa: E402


POLICY_DOC = """
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md
update_trigger: docs governance rules change
---

# Docs SSOT Policy

```md
---
doc_type: policy|reference|runbook|playbook|decision|generated
ssot_owner: AGENTS.md | <module path> | <workflow registry location>
update_trigger: <what change requires updating this doc>
---
```
"""


def resolve_router_filename(folder_name: str) -> str:
    return resolve_docs_router_filename(folder_name)


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = textwrap.dedent(content).lstrip("\n")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(rendered)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _write(path: Path, content: str) -> None:
    _atomic_write_text(path, content)


@contextmanager
def temporary_workspace():
    tmp_dir = tempfile.TemporaryDirectory(prefix="check-docs-router-contract-")
    body_error: BaseException | None = None
    try:
        yield Path(tmp_dir.name)
    except BaseException as exc:
        body_error = exc
        raise
    finally:
        try:
            tmp_dir.cleanup()
        except Exception as exc:
            cleanup_error = RuntimeError(f"FAILED_CLEANUP: Unable to remove temporary workspace {tmp_dir.name}: {exc}")
            if body_error is not None:
                raise BaseExceptionGroup(
                    "FAILED_CLEANUP: Temporary workspace cleanup failed after test body error.",
                    [body_error, cleanup_error],
                ) from exc
            raise cleanup_error from exc


def route_line(target: str, description: str, *, when: str | None = None) -> str:
    trigger = when or f"you need {target}"
    return f"- [{target}]({target}) - {description}. Required when: {trigger}."


def write_router(path: Path, title: str, route_lines: list[str]) -> None:
    _write(path, "\n".join([f"# {title}", "", *route_lines, ""]))


def write_parent_chain(repo_root: Path, rel_dir: str) -> None:
    parts = rel_dir.split("/")
    chain: list[str] = []
    docs_root = repo_root / "docs"
    for part in parts:
        parent_dir = docs_root / "/".join(chain) if chain else docs_root
        parent_router = parent_dir / resolve_router_filename(parent_dir.name)
        title = "Docs Branch Index" if not chain else f"{chain[-1].title()} Branch Index"
        target = f"{part}/{resolve_router_filename(part)}"
        write_router(
            parent_router,
            title,
            [route_line(target, f"route into {part}", when=f"navigating into the {part} branch")],
        )
        chain.append(part)


def write_router_fixture(
    repo_root: Path,
    governance_root: Path,
    rel_dir: str,
    primary_leaf_name: str,
    *,
    router_target: str | None = None,
    extra_leaf_names: list[str] | None = None,
    content_bearing_router: bool = False,
) -> None:
    _write(governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md", POLICY_DOC)
    write_parent_chain(repo_root, rel_dir)

    final_dir = repo_root / "docs" / rel_dir
    router_name = resolve_router_filename(final_dir.name)
    router_lines: list[str] = []
    if content_bearing_router:
        router_lines.extend(["This should not be narrative prose.", ""])
    router_lines.append(
        route_line(
            router_target or primary_leaf_name,
            "canonical narrative leaf",
            when="reviewing the canonical narrative content",
        )
    )
    for extra_leaf_name in extra_leaf_names or []:
        router_lines.append(
            route_line(
                extra_leaf_name,
                "additional public leaf",
                when=f"reviewing the {extra_leaf_name} public leaf",
            )
        )
    write_router(final_dir / router_name, f"{rel_dir.split('/')[-1].title()} Branch Index", router_lines)
    _write(
        final_dir / primary_leaf_name,
        """
        ---
        doc_type: reference
        ssot_owner: AGENTS.md
        update_trigger: example fixture changes
        ---

        # Canonical Leaf

        - Example canonical content.
        """,
    )
    for extra_leaf_name in extra_leaf_names or []:
        _write(
            final_dir / extra_leaf_name,
            f"""
            ---
            doc_type: reference
            ssot_owner: AGENTS.md
            update_trigger: example fixture changes
            ---

            # {extra_leaf_name}

            - Additional public leaf.
            """,
        )
