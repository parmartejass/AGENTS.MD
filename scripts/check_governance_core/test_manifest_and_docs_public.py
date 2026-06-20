from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]


def _load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from _test_helpers import write_text

MANIFEST_AND_DOCS = _load_module(
    "check_governance_core_manifest_and_docs", SCRIPT_ROOT / "_manifest_and_docs.py"
)


class ManifestAndDocsPublicCheckTests(unittest.TestCase):
    def _write_minimal_manifest_tree(
        self,
        governance_root: Path,
        *,
        project_docs_keyword: str = "project docs",
        project_docs_file_globs: tuple[str, ...] = ("README.md", "docs/project/**/*.md"),
        include_project_template_in_inject: bool = True,
    ) -> None:
        manifest_paths = [
            "AGENTS.md",
            "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md",
            "docs/agents/35-coding-principles/coding-principles.md",
            "docs/project/project_index.md",
            "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
            "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
        ]
        if include_project_template_in_inject:
            manifest_paths.append("docs/agents/playbooks/project-docs-template/project-docs-template.md")
        for rel_path in manifest_paths:
            write_text(governance_root / rel_path, "# Test\n")
        write_text(
            governance_root / "scripts/entrypoint_contracts.json",
            (REPO_ROOT / "scripts/entrypoint_contracts.json").read_text(encoding="utf-8"),
        )

        file_globs = "\n".join(f'        - "{file_glob}"' for file_glob in project_docs_file_globs)
        project_docs_inject = [
            "docs/project/project_index.md",
            "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
            "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
        ]
        if include_project_template_in_inject:
            project_docs_inject.append("docs/agents/playbooks/project-docs-template/project-docs-template.md")
        project_docs_inject_text = "\n".join(f'      - "{rel_path}"' for rel_path in project_docs_inject)

        write_text(
            governance_root / "agents-manifest.yaml",
            f"""
version: 1
default_inject:
  - "AGENTS.md"
profiles:
  governance_improvement:
    detect:
      keywords:
        - "governance"
      code_patterns: []
      file_globs: []
    inject:
      - "docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md"
  coding_principles:
    detect:
      keywords:
        - "coding principles"
      code_patterns: []
      file_globs: []
    inject:
      - "docs/agents/35-coding-principles/coding-principles.md"
      - "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"
  project_docs:
    detect:
      keywords:
        - "{project_docs_keyword}"
      code_patterns: []
      file_globs:
{file_globs}
    inject:
{project_docs_inject_text}
""".lstrip(),
        )

    def test_check_agents_manifest_rejects_broad_project_docs_keyword(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_minimal_manifest_tree(governance_root, project_docs_keyword="docs")

            errors = MANIFEST_AND_DOCS.check_agents_manifest(governance_root)

            self.assertTrue(
                any("profiles.project_docs.detect keyword is too broad: docs" in error for error in errors),
                errors,
            )

    def test_check_agents_manifest_requires_project_docs_inject_owner_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_minimal_manifest_tree(governance_root, include_project_template_in_inject=False)
            write_text(
                governance_root / "docs/agents/playbooks/project-docs-template/project-docs-template.md",
                "# Test\n",
            )

            errors = MANIFEST_AND_DOCS.check_agents_manifest(governance_root)

            self.assertTrue(
                any("profiles.project_docs.inject must include docs/agents/playbooks/project-docs-template/project-docs-template.md" in error for error in errors),
                errors,
            )

    def test_check_agents_manifest_requires_project_docs_file_globs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            governance_root = Path(tmp_dir)
            self._write_minimal_manifest_tree(governance_root, project_docs_file_globs=("README.md",))

            errors = MANIFEST_AND_DOCS.check_agents_manifest(governance_root)

            self.assertTrue(
                any("profiles.project_docs.detect.file_globs must include docs/project/**/*.md" in error for error in errors),
                errors,
            )

    def test_check_agents_manifest_requires_coding_principles_owner_injects(self) -> None:
        cases = (
            (
                '      - "docs/agents/35-coding-principles/coding-principles.md"\n'
                '      - "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"',
                '      - "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"',
                "profiles.coding_principles.inject must include docs/agents/35-coding-principles/coding-principles.md",
            ),
            (
                '      - "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md"\n  project_docs:',
                "  project_docs:",
                "profiles.coding_principles.inject must include docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
            ),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    governance_root = Path(tmp_dir)
                    self._write_minimal_manifest_tree(governance_root)
                    manifest_path = governance_root / "agents-manifest.yaml"
                    write_text(
                        manifest_path,
                        manifest_path.read_text(encoding="utf-8").replace(old, new, 1),
                    )

                    errors = MANIFEST_AND_DOCS.check_agents_manifest(governance_root)

                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_check_docs_ssot_rejects_missing_leaf_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            write_text(
                repo_root / "docs/docs_index.md",
                """
# Docs Index

- [example](example/example_index.md) - Example docs. Required when: checking docs.
""".lstrip(),
            )
            write_text(
                repo_root / "docs/example/example_index.md",
                """
# Example Index

- [example.md](example.md) - Example leaf. Required when: checking docs.
""".lstrip(),
            )
            write_text(repo_root / "docs/example/example.md", "# Example\n")

            errors, _warnings = MANIFEST_AND_DOCS.check_docs_ssot(repo_root, REPO_ROOT)

            self.assertTrue(any("Missing doc header (doc_type)" in error for error in errors), errors)
            self.assertTrue(any("Missing doc header (ssot_owner)" in error for error in errors), errors)
            self.assertTrue(any("Missing doc header (update_trigger)" in error for error in errors), errors)
