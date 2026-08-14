from __future__ import annotations

import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core.check_governance_core_main import resolve_documents, run_checks
from scripts.check_governance_core._documents import declared_doc_types, parse_markdown, router_targets
from scripts.check_governance_core._docs_checks import check_docs
from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._governance_checks import (
    governance_contract_digest,
    resolve_governance_contract,
)
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
ROOT_AUTHORITIES = (
    "docs/agents/owner.md",
    "docs/agents/context.md",
    "docs/agents/map.md",
)
CANONICAL_DELEGATION = "Delegate through the owning contract."
def write(path: Path, text: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        with path.open("wb") as handle:
            handle.write(text)
    else:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)

def governance_fixture(root: Path, manifest: str) -> None:
    witness = governance_contract_digest(ROOT_AUTHORITIES, CANONICAL_DELEGATION)
    write(
        root / "AGENTS.md",
        f"""# Agent

## Assigned-Lead Authority Routing Procedure (Hard Gate)

Read and follow these authorities:
- `docs/agents/owner.md`
- `docs/agents/context.md`
- `docs/agents/map.md`

> {CANONICAL_DELEGATION}

<!-- governance-root-contract: authorities=3 sha256={witness} -->

## Documentation SSOT Policy (Hard Gate)

Baseline required project docs include:
- `docs/project/project_index.md`
""",
    )
    for authority in ROOT_AUTHORITIES:
        write(root / authority, "---\ndoc_type: policy\nssot_owner: AGENTS.md\nupdate_trigger: owner changes\n---\n")
    write(root / "docs/agents/agents_index.md", "# Agents Index\n")
    write(root / "agents-manifest.yaml", manifest)


def valid_manifest(authority: str = "docs/agents/other.md") -> str:
    return (FIXTURE_ROOT / "manifest_valid.yaml").read_text(encoding="utf-8").replace(
        "__AUTHORITY__", authority
    )


class PublicApiContractTests(unittest.TestCase):
    def test_governance_owner_witness_rejects_membership_order_and_delegation_drift(self) -> None:
        mutations = (
            ("- `docs/agents/context.md`\n", ""),
            (
                "- `docs/agents/owner.md`\n- `docs/agents/context.md`\n",
                "- `docs/agents/context.md`\n- `docs/agents/owner.md`\n",
            ),
            (CANONICAL_DELEGATION, "Delegate through a different contract."),
        )
        for old, new in mutations:
            with self.subTest(old=old), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest())
                path = root / "AGENTS.md"
                write(path, path.read_text(encoding="utf-8").replace(old, new))
                contract = resolve_governance_contract(root, DocumentStore(), RepositoryInventory(root))
                self.assertTrue(contract.errors, contract)

    def test_unrelated_blockquote_does_not_change_governance_owner_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            path = root / "AGENTS.md"
            write(path, path.read_text(encoding="utf-8") + "\n## Unrelated\n\n> Example only.\n")
            contract = resolve_governance_contract(root, DocumentStore(), RepositoryInventory(root))
            self.assertEqual((), contract.errors, contract)

    def test_decision_critical_governance_file_aliases_are_rejected(self) -> None:
        for filename in ("AGENTS.md", "agents-manifest.yaml"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest())
                write(root / "docs/agents/other.md", "owner\n")
                target = root / filename
                source = root / f"{filename}.source"
                target.replace(source)
                os.link(source, target)

                result = run_checks({"repo_root": str(root), "governance_root": str(root)})

                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(
                    any("must not be an alias" in error for error in result["errors"]),
                    result,
                )

    def test_project_docs_rejects_readme_alias_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/project/project_index.md", "# Project\n")
            source = root / "README.md.source"
            write(source, "# Test\n")
            os.link(source, root / "README.md")

            result = run_checks(
                {
                    "repo_root": str(root),
                    "governance_root": str(root),
                    "mode": "project_docs",
                }
            )

            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(
                any("README.md" in error and "must not be an alias" in error for error in result["errors"]),
                result,
            )

    def test_docs_mode_does_not_preload_the_repository_tree(self) -> None:
        root = Path(__file__).resolve().parents[2]
        seen: list[Path] = []
        original = RepositoryInventory.tree_entries

        def record(inventory: RepositoryInventory, scan_root: Path):
            seen.append(scan_root.resolve())
            return original(inventory, scan_root)

        with patch.object(RepositoryInventory, "tree_entries", new=record):
            result = run_checks(
                {"repo_root": str(root), "governance_root": str(root), "mode": "docs"}
            )

        self.assertEqual("PASSED", result["status"], result)
        self.assertNotIn(root.resolve(), seen)
        self.assertIn((root / "docs").resolve(), seen)

    def test_report_reconciles_the_selected_work_universe(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = run_checks(
            {"repo_root": str(root), "governance_root": str(root), "mode": "docs"}
        )
        self.assertEqual(["docs"], result["planned"])
        self.assertEqual(result["planned"], result["eligible"])
        self.assertEqual(result["planned"], result["executed"])
        self.assertEqual([], result["skipped"])
        self.assertEqual([], result["failed"])

    def test_rejects_unknown_public_request_key(self) -> None:
        result = run_checks({"unexpected": True})
        self.assertEqual("FAILED_VALIDATION", result["status"])
        self.assertIn("unsupported request key", result["errors"][0])

    def test_rejects_invalid_public_request_value_types(self) -> None:
        for request in ({"mode": []}, {"fail_on_safety_warnings": "false"}, {"repo_root": 42}):
            with self.subTest(request=request):
                result = run_checks(request)
                self.assertEqual("FAILED_VALIDATION", result["status"], result)

    def test_handler_exception_preserves_work_universe(self) -> None:
        root = Path(__file__).resolve().parents[2]
        with patch("scripts.check_governance_core._engine.validate_manifest", side_effect=RuntimeError("boom")):
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
        self.assertEqual("FAILED", result["status"])
        self.assertEqual(
            sorted(result["planned"]),
            sorted([*result["executed"], *result["skipped"], *result["failed"]]),
        )
        self.assertIn("manifest", result["failed"])

    def test_invalid_yaml_is_explicit_failure_not_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(
                root,
                (FIXTURE_ROOT / "manifest_invalid_trailing.yaml").read_text(encoding="utf-8"),
            )
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"])
            self.assertTrue(any("invalid double-quoted scalar" in error for error in result["errors"]), result)

    def test_invalid_yaml_colon_space_scalar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest().replace(
                "update_trigger: routes change",
                "update_trigger: routes: change",
            ))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_invalid_yaml_colon_tab_scalar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest().replace("- 'sample'", "- sample:\tevil"))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_invalid_yaml_mapping_marker_and_single_quote_are_rejected(self) -> None:
        for value in ("sample:", "'a' b 'c'"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest().replace("'sample'", value))
                write(root / "docs/agents/other.md", "owner\n")
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)

    def test_single_quoted_scalars_are_parsed_once_and_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("PASSED", manifest["status"], manifest)

    def test_root_authority_aliases_are_rejected_before_filesystem_lookup(self) -> None:
        aliases = (
            "DOCS/AGENTS/OWNER.MD",
            "docs/agents/owner.md ",
            "docs/agents/owner.md:stream",
        )
        for alias in aliases:
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest(alias))
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)

    def test_non_root_authority_case_alias_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest("DOCS/AGENTS/OTHER.MD"))
            write(root / "docs/agents/other.md", "owner\n")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_hard_link_alias_of_root_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest("docs/agents/alias.md"))
            os.link(root / "docs/agents/owner.md", root / "docs/agents/alias.md")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            manifest = next(record for record in result["checks"] if record["id"] == "manifest")
            self.assertEqual("FAILED", manifest["status"], manifest)

    def test_root_authority_list_is_scoped_to_owner_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/agents/other.md", "owner\n")
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            agents = agents.replace(
                "Read and follow these authorities:\n"
                "- `docs/agents/owner.md`\n"
                "- `docs/agents/context.md`\n"
                "- `docs/agents/map.md`\n\n",
                "",
            ) + (
                "\n## Unrelated\n\nRead and follow these authorities:\n"
                "- `docs/agents/owner.md`\n"
                "- `docs/agents/context.md`\n"
                "- `docs/agents/map.md`\n"
            )
            write(root / "AGENTS.md", agents)
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            governance = next(record for record in result["checks"] if record["id"] == "governance")
            self.assertEqual("FAILED", governance["status"], governance)

    def test_fenced_and_indented_headings_are_not_owner_sections(self) -> None:
        for fake in (
            "```md\n## Assigned-Lead Authority Routing Procedure (Hard Gate)\n```",
            "    ## Assigned-Lead Authority Routing Procedure (Hard Gate)",
        ):
            with self.subTest(fake=fake), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest())
                write(root / "AGENTS.md", f"# Agent\n\n{fake}\n")
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                governance = next(record for record in result["checks"] if record["id"] == "governance")
                self.assertEqual("FAILED", governance["status"], governance)

    def test_one_to_three_space_heading_is_operative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/agents/other.md", "owner\n")
            path = root / "AGENTS.md"
            write(path, path.read_text(encoding="utf-8").replace("## Assigned-Lead", "   ## Assigned-Lead"))
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            governance = next(record for record in result["checks"] if record["id"] == "governance")
            self.assertEqual("PASSED", governance["status"], governance)

    def test_invalid_utf8_returns_explicit_issue(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "agents-manifest.yaml", b"\xff\xfe")
            result = run_checks({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"])
            self.assertTrue(any("Invalid UTF-8" in error for error in result["errors"]), result)

    def test_document_resolution_is_independent_of_agents_routing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance_fixture(root, valid_manifest())
            write(root / "docs/agents/other.md", "owner\n")
            write(root / "AGENTS.md", "# Missing owner section\n")
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(["AGENTS.md"], result["documents"])

    def test_document_resolution_rejects_invalid_root_types(self) -> None:
        for request in ({"repo_root": []}, {"governance_root": False}, {"repo_root": ""}):
            with self.subTest(request=request):
                result = resolve_documents(request)
                self.assertEqual("FAILED_VALIDATION", result["status"], result)

    def test_manifest_requires_string_metadata(self) -> None:
        for mutation in (
            ("description: >-\n  frozen success fixture", "description: {}"),
            ("update_trigger: routes change", "update_trigger: []"),
            ("- 'find the owner'", "- ''"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                governance_fixture(root, valid_manifest().replace(*mutation))
                write(root / "docs/agents/other.md", "owner\n")
                result = run_checks({"repo_root": str(root), "governance_root": str(root)})
                manifest = next(record for record in result["checks"] if record["id"] == "manifest")
                self.assertEqual("FAILED", manifest["status"], manifest)

    def test_router_target_and_doc_type_contract_helpers_reject_invalid_values(self) -> None:
        router = parse_markdown(
            "# Router\n\n- [ghost](ghost.md) - route. Required when: needed.\n"
        )
        targets, errors = router_targets(router)
        self.assertEqual(["ghost.md"], targets)
        self.assertEqual([], errors)
        policy = "doc_type: policy|reference|runbook|playbook|decision|generated\n"
        self.assertNotIn("nonsense", declared_doc_types(policy))

    def test_docs_check_rejects_dead_router_target_and_invalid_doc_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            repo_root = workspace / "repo"
            governance_root = workspace / "governance"
            write(
                governance_root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
                "doc_type: policy|reference|runbook|playbook|decision|generated\n",
            )
            write(
                repo_root / "docs/docs_index.md",
                "# Docs\n\n- [docs](docs.md) - docs. Required when: reading docs.\n"
                "- [ghost](ghost.md) - ghost. Required when: reading ghost.\n",
            )
            write(
                repo_root / "docs/docs.md",
                "---\ndoc_type: nonsense\nssot_owner: owner\nupdate_trigger: changes\n---\n\n# Docs\n",
            )
            errors, _warnings = check_docs(
                repo_root,
                governance_root,
                DocumentStore(),
                RepositoryInventory(repo_root),
            )
            self.assertTrue(any("ghost.md" in error for error in errors), errors)
            self.assertTrue(any("unsupported doc_type" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
