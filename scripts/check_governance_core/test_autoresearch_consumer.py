from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py"
)


def load_consumer():
    spec = importlib.util.spec_from_file_location("governance_research_contract_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AutoresearchConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.consumer = load_consumer()

    def setUp(self) -> None:
        self.consumer.governance_file_set.cache_clear()

    def test_single_file_input_must_be_canonical_corpus_member(self) -> None:
        consumer = self.consumer
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            owned = root / "docs/agents/owned.md"
            owned.parent.mkdir(parents=True)
            with owned.open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Owned Topic\n")
            outside = root.parent / "outside-governance.md"
            values = (str(outside), "../owned.md", "docs/agents/orphan.md")
            with (
                patch.object(consumer, "REPO_ROOT", root),
                patch.object(consumer, "governance_files", return_value=("docs/agents/owned.md",)),
            ):
                for value in values:
                    with self.subTest(value=value):
                        with self.assertRaises(consumer.UsageError):
                            consumer.extract_topics(value)

    def test_valid_corpus_member_is_read_and_reported_canonically(self) -> None:
        consumer = self.consumer
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            owned = root / "docs/agents/owned.md"
            owned.parent.mkdir(parents=True)
            with owned.open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Owned Governance Topic\n")
            with (
                patch.object(consumer, "REPO_ROOT", root),
                patch.object(consumer, "governance_files", return_value=("docs/agents/owned.md",)),
                patch.object(consumer, "search_x", return_value=[]),
            ):
                result = consumer.research_file("docs/agents/owned.md")
            self.assertEqual("docs/agents/owned.md", result["file"])
            self.assertEqual(["Owned Governance Topic"], result["topics_searched"])

    def test_membership_index_is_built_once(self) -> None:
        consumer = self.consumer
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            owned = root / "docs/agents/owned.md"
            owned.parent.mkdir(parents=True)
            with owned.open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Owned Topic\n")
            with (
                patch.object(consumer, "REPO_ROOT", root),
                patch.object(
                    consumer,
                    "governance_files",
                    return_value=("docs/agents/owned.md",),
                ) as corpus,
            ):
                consumer.resolve_governance_path("docs/agents/owned.md")
                consumer.resolve_governance_path("docs/agents/owned.md")

            self.assertEqual(1, corpus.call_count)

    def test_research_item_is_resolved_once(self) -> None:
        consumer = self.consumer
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            owned = root / "docs/agents/owned.md"
            owned.parent.mkdir(parents=True)
            with owned.open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Owned Topic\n")
            with (
                patch.object(consumer, "REPO_ROOT", root),
                patch.object(consumer, "governance_files", return_value=("docs/agents/owned.md",)),
                patch.object(consumer, "search_x", return_value=[]),
                patch.object(
                    consumer,
                    "resolve_governance_path",
                    wraps=consumer.resolve_governance_path,
                ) as resolver,
            ):
                consumer.research_file("docs/agents/owned.md")

            self.assertEqual(1, resolver.call_count)

    def test_list_reports_full_loop_search_bound_from_corpus_and_topic_owner(self) -> None:
        consumer = self.consumer
        corpus = ("AGENTS.md", "docs/agents/owned.md")
        with (
            patch.object(consumer, "governance_files", return_value=corpus),
            patch.object(consumer, "extract_topics", return_value=[]),
            patch.object(consumer.sys, "argv", [str(SCRIPT), "--list"]),
            patch.object(consumer, "write_stdout_line") as writer,
        ):
            consumer.main()

        self.assertEqual(
            f"Summary: documents=2, max_topics_per_file={consumer.MAX_TOPICS_PER_FILE}, "
            f"maximum_full_loop_searches={2 * consumer.MAX_TOPICS_PER_FILE}",
            writer.call_args_list[-1].args[0],
        )

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_cached_corpus_member_is_revalidated_before_read(self) -> None:
        consumer = self.consumer
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            root = workspace / "repo"
            branch = root / "docs/agents/branch"
            outside = workspace / "outside"
            branch.mkdir(parents=True)
            outside.mkdir()
            leaf = branch / "leaf.md"
            with leaf.open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Original Topic\n")
            leaf.unlink()
            branch.rmdir()
            with (outside / "leaf.md").open("w", encoding="utf-8", newline="") as handle:
                handle.write("# Outside Secret Topic\n")
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(branch), str(outside)],
                check=True,
                capture_output=True,
                timeout=10,
            )
            with (
                patch.object(consumer, "REPO_ROOT", root),
                patch.object(
                    consumer,
                    "governance_files",
                    return_value=("docs/agents/branch/leaf.md",),
                ),
            ):
                with self.assertRaises(consumer.UsageError):
                    consumer.extract_topics("docs/agents/branch/leaf.md")


if __name__ == "__main__":
    unittest.main()
