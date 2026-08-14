from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_governance_core.check_governance_core_main import resolve_documents


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def corpus_fixture(root: Path) -> None:
    write(root / "AGENTS.md", "# Agent\n")
    write(
        root / "docs/agents/agents_index.md",
        "# Agents\n\n"
        "- [MCP](mcp/mcp_index.md) - MCP. Required when: using MCP.\n"
        "- [Workflow](workflow-registry/workflow-registry_index.md) - workflows. "
        "Required when: selecting workflows.\n",
    )
    write(
        root / "docs/agents/mcp/mcp_index.md",
        "# MCP\n\n"
        "- [Standards](00-mcp-standards/mcp-standards.md) - standards. "
        "Required when: using MCP.\n",
    )
    write(root / "docs/agents/mcp/00-mcp-standards/mcp-standards.md", "# MCP Standards\n")
    write(
        root / "docs/agents/workflow-registry/workflow-registry_index.md",
        "# Workflows\n\n"
        "- [Registry](workflow-registry.md) - registry. Required when: selecting workflows.\n",
    )
    write(root / "docs/agents/workflow-registry/workflow-registry.md", "# Workflow Registry\n")


class DocumentResolutionTests(unittest.TestCase):
    def test_live_corpus_contains_mcp_and_workflow_registry_leaves(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
        self.assertEqual("PASSED", result["status"], result)
        self.assertIn(
            "docs/agents/mcp/00-mcp-standards/mcp-standards.md",
            result["documents"],
        )
        self.assertIn(
            "docs/agents/workflow-registry/workflow-registry.md",
            result["documents"],
        )

    def test_corpus_is_router_ordered_and_manifest_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            write(root / "agents-manifest.yaml", "not: [valid: yaml\n")
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(
                [
                    "AGENTS.md",
                    "docs/agents/mcp/00-mcp-standards/mcp-standards.md",
                    "docs/agents/workflow-registry/workflow-registry.md",
                ],
                result["documents"],
            )

    def test_router_addition_is_discovered_without_manifest_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            router = root / "docs/agents/agents_index.md"
            write(
                router,
                router.read_text(encoding="utf-8")
                + "- [Extra](extra/extra.md) - extra. Required when: researching extra.\n",
            )
            write(root / "docs/agents/extra/extra.md", "# Extra\n")
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual("docs/agents/extra/extra.md", result["documents"][-1])

    def test_direct_directory_route_follows_its_canonical_child_router(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            write(
                root / "docs/agents/agents_index.md",
                "# Agents\n\n- [MCP](mcp/) - MCP. Required when: using MCP.\n",
            )
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(
                ["AGENTS.md", "docs/agents/mcp/00-mcp-standards/mcp-standards.md"],
                result["documents"],
            )

    def test_directory_route_without_canonical_child_router_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "AGENTS.md", "# Agent\n")
            write(
                root / "docs/agents/agents_index.md",
                "# Agents\n\n- [MCP](mcp/) - MCP. Required when: using MCP.\n",
            )
            (root / "docs/agents/mcp").mkdir(parents=True)
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])
            self.assertTrue(any("canonical child router" in error for error in result["errors"]), result)

    def test_dead_router_target_fails_with_empty_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            router = root / "docs/agents/agents_index.md"
            write(
                router,
                router.read_text(encoding="utf-8")
                + "- [Missing](missing/missing.md) - missing. Required when: missing.\n",
            )
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])
            self.assertTrue(any("missing" in error for error in result["errors"]), result)

    def test_wrong_case_directory_and_leaf_routes_fail_canonically(self) -> None:
        mutations = (
            ("mcp/mcp_index.md", "MCP/"),
            ("00-mcp-standards/mcp-standards.md", "00-mcp-standards/MCP-STANDARDS.md"),
        )
        for old, new in mutations:
            with self.subTest(new=new), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                corpus_fixture(root)
                for router in (
                    root / "docs/agents/agents_index.md",
                    root / "docs/agents/mcp/mcp_index.md",
                ):
                    text = router.read_text(encoding="utf-8")
                    if old in text:
                        write(router, text.replace(old, new))
                result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
                self.assertEqual("FAILED", result["status"], result)
                self.assertEqual([], result["documents"])
                self.assertTrue(any("noncanonical" in error for error in result["errors"]), result)

    def test_invalid_utf8_leaf_fails_during_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            leaf = root / "docs/agents/mcp/00-mcp-standards/mcp-standards.md"
            with leaf.open("wb") as handle:
                handle.write(b"\xff\xfe")
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])
            self.assertTrue(any("Invalid UTF-8" in error for error in result["errors"]), result)

    def test_hardlinked_agents_and_leaf_are_rejected_as_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            leaf = root / "docs/agents/mcp/00-mcp-standards/mcp-standards.md"
            leaf.unlink()
            try:
                leaf.hardlink_to(root / "AGENTS.md")
            except OSError as exc:
                self.skipTest(f"hard links unavailable: {exc}")
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])
            self.assertTrue(any("alias" in error for error in result["errors"]), result)

    def test_duplicate_route_fails_instead_of_silently_deduplicating(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus_fixture(root)
            router = root / "docs/agents/agents_index.md"
            write(
                router,
                router.read_text(encoding="utf-8")
                + "- [MCP again](mcp/mcp_index.md) - duplicate. Required when: duplicated.\n",
            )
            result = resolve_documents({"repo_root": str(root), "governance_root": str(root)})
            self.assertEqual("FAILED", result["status"], result)
            self.assertEqual([], result["documents"])
            self.assertTrue(any("duplicate route target" in error for error in result["errors"]), result)

    def test_vendored_governance_root_is_accepted_when_contained(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            governance_root = repo_root / ".governance"
            write(governance_root / "AGENTS.md", "# Agent\n")
            write(governance_root / "docs/agents/agents_index.md", "# Agents\n")
            result = resolve_documents(
                {"repo_root": str(repo_root), "governance_root": str(governance_root)}
            )
            self.assertEqual("PASSED", result["status"], result)
            self.assertEqual(["AGENTS.md"], result["documents"])


if __name__ == "__main__":
    unittest.main()
