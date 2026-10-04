from __future__ import annotations

import logging
import re
import unittest
from time import perf_counter
from unittest.mock import patch

from scripts.check_governance_core._docs_checks import (
    DOCS_POLICY_PATH, _documentation_line_limit, _physical_lines, _required_project_paths, check_docs,
)
from scripts.check_governance_core._documents import DocumentStore
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import REPOSITORY_ROOT, live_principles_section


logger = logging.getLogger(__name__)


def _performance_target_ms() -> int:
    return int(re.search(r"### FP-03\n\n.*?within ([0-9]+) milliseconds", live_principles_section(), re.S).group(1))


class DocsPolicyTimingTests(unittest.TestCase):
    def test_actual_corpus_policy_lookup_and_validation_timing(self) -> None:
        scenario_started = perf_counter()
        root = REPOSITORY_ROOT
        target_ms = _performance_target_ms()
        preparation_started = perf_counter()
        inventory = RepositoryInventory(root)
        store = DocumentStore()
        started = perf_counter()
        files, error = inventory.markdown_files(root)
        self.assertIsNone(error)
        policy_path = root / DOCS_POLICY_PATH
        document, error = store.markdown(policy_path)
        self.assertIsNone(error)
        corpus_load_ms = (perf_counter() - started) * 1000
        populations = []
        for _sample in range(5):
            started = perf_counter()
            fresh = RepositoryInventory(root)
            fresh_files, error = fresh.markdown_files(root)
            populations.append((perf_counter() - started) * 1000)
            self.assertIsNone(error)
            self.assertEqual(files, fresh_files)
        texts = [store.read_text(path)[0] for path in files]
        self.assertTrue(all(text is not None for text in texts))
        preparation_ms = (perf_counter() - preparation_started) * 1000
        samples = {"policy_resolution_ms": [], "cached_lookup_ms": [], "line_validation_ms": []}
        for _sample in range(5):
            started = perf_counter()
            limit, errors = _documentation_line_limit(document)
            required, branch_errors = _required_project_paths(document)
            samples["policy_resolution_ms"].append((perf_counter() - started) * 1000)
            self.assertIsNotNone(limit)
            self.assertTrue(required)
            self.assertEqual([], errors + branch_errors)
            started = perf_counter()
            self.assertIsNotNone(store.read_text(policy_path)[0])
            samples["cached_lookup_ms"].append((perf_counter() - started) * 1000)
            started = perf_counter()
            over_limit = [index for index, text in enumerate(texts) if _physical_lines(text) > limit]
            samples["line_validation_ms"].append((perf_counter() - started) * 1000)
            self.assertEqual([], over_limit)
        handlers = {"cold_document_cache": [], "warm_document_cache": []}
        for cache, timings in handlers.items():
            for _sample in range(5):
                sample_store = DocumentStore() if cache == "cold_document_cache" else store
                started = perf_counter()
                errors, warnings = check_docs(root, root, sample_store, inventory)
                timings.append((perf_counter() - started) * 1000)
                self.assertEqual([], errors + warnings)
        measured = {"corpus_load_ms": [corpus_load_ms], "corpus_preparation_ms": [preparation_ms],
                    "fresh_inventory_ms": populations, **samples, **handlers,
                    "timing_scenario_ms": [(perf_counter() - scenario_started) * 1000]}
        for name, values in measured.items():
            logger.warning("FP-03 operation=%s target_ms=%s samples_ms=%s outcome=%s", name, target_ms,
                           [round(value, 3) for value in values],
                           "UNMET" if max(values) > target_ms else "MET")
        logger.warning("FP-03 boundaries: corpus preparation includes fresh inventory probes and text loading; "
                       "handlers include validation with warm inventory as in engine dispatch; scenario includes "
                       "target lookup, setup, samples, and correctness assertions through measurement. "
                       "Reporting, test-runner setup/teardown and model/platform/network/status timing are "
                       "uninstrumented here; no workbook persistence occurs. Reporting success is not target attainment.")
        for name, values in samples.items():
            self.assertLess(max(values), target_ms, (name, values))

    def test_timing_reports_slow_filesystem_operations_as_unmet(self) -> None:
        elapsed = 0.0
        delay = _performance_target_ms() * 2 / 1000
        original = RepositoryInventory.markdown_files

        def delayed_inventory(inventory, root):
            nonlocal elapsed
            result = original(inventory, root)
            # Advance elapsed time at the real operation boundary, independent of clock-call counts.
            elapsed += delay
            return result

        with patch(f"{__name__}.perf_counter", side_effect=lambda: elapsed), patch.object(
            RepositoryInventory, "markdown_files", new=delayed_inventory
        ), self.assertLogs(logger, level="WARNING") as captured:
            self.test_actual_corpus_policy_lookup_and_validation_timing()
        for operation in ("corpus_load_ms", "corpus_preparation_ms", "fresh_inventory_ms",
                          "cold_document_cache", "warm_document_cache", "timing_scenario_ms"):
            self.assertTrue(any(f"operation={operation} " in line and "outcome=UNMET" in line
                                for line in captured.output), (operation, captured.output))

    def test_timing_rejects_slow_policy_decisions(self) -> None:
        elapsed = 0.0
        delay = _performance_target_ms() * 2 / 1000
        original = _documentation_line_limit

        def delayed_policy(document):
            nonlocal elapsed
            result = original(document)
            elapsed += delay
            return result

        with patch(f"{__name__}.perf_counter", side_effect=lambda: elapsed), patch(
            f"{__name__}._documentation_line_limit", new=delayed_policy
        ), self.assertRaisesRegex(AssertionError, "policy_resolution_ms"):
            self.test_actual_corpus_policy_lookup_and_validation_timing()


if __name__ == "__main__":
    unittest.main()
