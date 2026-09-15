from __future__ import annotations

import os
import logging
import re
import stat
import subprocess
import tempfile
import unittest
from time import perf_counter
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from scripts.check_governance_core._docs_checks import (
    _documentation_line_limit, _physical_lines, _required_project_paths, check_docs,
)
from scripts.check_governance_core._documents import (
    DocumentStore, declared_doc_types, parse_markdown, router_filename, router_targets,
)
from scripts.check_governance_core._inventory import RepositoryInventory
from scripts.check_governance_core._test_support import (
    REPOSITORY_ROOT, install_docs_policy, install_root_authorities, live_principles_section, write,
)
from scripts.check_governance_core.check_governance_core_main import run_checks


logger = logging.getLogger(__name__)


def _performance_target_ms() -> int:
    return int(re.search(r"### FP-03\n\n.*?within ([0-9]+) milliseconds", live_principles_section(), re.S).group(1))


def docs_fixture(root: Path, governance_root: Path | None = None) -> tuple[Path, int]:
    governance = governance_root or root
    install_root_authorities(governance)
    policy_path = install_docs_policy(governance)
    document = parse_markdown(policy_path.read_text(encoding="utf-8"))
    limit, errors = _documentation_line_limit(document)
    required, branch_errors = _required_project_paths(document)
    assert limit is not None and not errors and not branch_errors
    for relative in required:
        path = root / relative
        write(path, "# Router\n" if path.name.endswith("_index.md") else
              "---\ndoc_type: reference\nssot_owner: fixture\nupdate_trigger: fixture changes\n---\n\n# Fixture\n")
    for docs in {root / "docs", governance / "docs"}:
        directories = [docs, *(path for path in docs.rglob("*") if path.is_dir())]
        for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
            router = directory / router_filename(directory.name)
            children = sorted((path for path in directory.iterdir() if path != router), key=lambda path: path.name)
            links = [f"{path.name}/{router_filename(path.name)}" if path.is_dir() else path.name for path in children]
            write(router, "# Router\n\n" + "".join(f"- [{link}]({link}) - fixture. Required when: testing.\n" for link in links))
    prefix = ".governance/" if governance != root else ""
    write(root / "README.md", "# Fixture\n\nAGENTS.md docs/project/project_index.md\n\n## Checks\n"
          + prefix + "scripts/check_governance_core/check_governance_core_main.py\n")
    return policy_path, limit


def docs_result(root: Path, governance: Path | None = None, mode: str = "docs"):
    return run_checks({"repo_root": root, "governance_root": governance or root, "mode": mode})


class DocsPolicyTests(unittest.TestCase):
    def test_cached_ancestor_metadata_is_checked_before_any_document_read(self) -> None:
        cases = ((kind, cached) for kind in ("valid", "reparse", "symlink", "io_error") for cached in (False, True))
        for kind, cached in cases:
            with self.subTest(kind=kind, cached=cached), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                scan_root = root / "nested"
                ancestor = scan_root / "middle"
                source = ancestor / "child/cached.md"
                write(source, "unchanged leaf\n")
                inventory, store = RepositoryInventory(root), DocumentStore()
                if cached:
                    self.assertIsNone(inventory.tree_entries(root)[1])
                    self.assertEqual(((source,), None), inventory.markdown_files(scan_root))
                    self.assertEqual(([], []), check_docs(root, root, store, inventory))
                real_stat = Path.stat
                leaf_metadata, leaf_resolution = source.stat(), source.resolve(strict=True)

                def metadata(path, *args, **kwargs):
                    value = real_stat(path, *args, **kwargs)
                    if path != ancestor or kwargs.get("follow_symlinks", True):
                        return value
                    if kind == "io_error":
                        raise PermissionError("ancestor metadata denied")
                    fields = {name: getattr(value, name) for name in dir(value) if name.startswith("st_")}
                    if kind == "reparse":
                        fields["st_file_attributes"] = getattr(value, "st_file_attributes", 0) | stat.FILE_ATTRIBUTE_REPARSE_POINT
                    elif kind == "symlink":
                        fields["st_mode"] = stat.S_IFLNK
                    return SimpleNamespace(**fields)

                with patch.object(Path, "stat", new=metadata), patch.object(store, "read_text", wraps=store.read_text) as read:
                    self.assertEqual(leaf_metadata, source.stat())
                    self.assertEqual(leaf_resolution, source.resolve(strict=True))
                    errors, warnings = check_docs(root, root, store, inventory)
                    self.assertEqual([], warnings)
                    if kind == "valid":
                        self.assertEqual([], errors)
                        self.assertTrue(read.called)
                    else:
                        read.assert_not_called()
                        diagnostic = "ancestor metadata denied" if kind == "io_error" else "alias"
                        self.assertTrue(any(diagnostic in error for error in errors), errors)
                        for files, error in (inventory.markdown_files(scan_root), inventory.markdown_files(root)):
                            self.assertEqual((), files)
                            self.assertIn(diagnostic, error or "")
                        resolved, error = inventory.validate_file(source)
                        self.assertIsNone(resolved)
                        self.assertIn(diagnostic, error or "")
                if kind != "valid":
                    self.assertEqual((), inventory.markdown_files(scan_root)[0])

    def test_cached_family_revalidates_alias_type_identity_and_resolution(self) -> None:
        for kind in ("hardlink", "directory", "special", "identity", "ancestor_alias", "case"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                source = root / "cached.md"
                write(source, "cached original\n")
                inventory, store = RepositoryInventory(root), DocumentStore()
                self.assertEqual(([], []), check_docs(root, root, store, inventory))
                real_stat, real_resolve = Path.stat, Path.resolve
                if kind in {"hardlink", "directory", "identity"}:
                    previous = root / "previous.txt"
                    source.replace(previous)
                    if kind == "hardlink":
                        os.link(previous, source)
                    elif kind == "directory":
                        source.mkdir()
                    else:
                        write(source, "replacement\n")

                def metadata(path, *args, **kwargs):
                    value = real_stat(path, *args, **kwargs)
                    if path == source and kind == "special":
                        return SimpleNamespace(st_mode=stat.S_IFIFO, st_nlink=1, st_file_attributes=0)
                    return value

                def resolved(path, *args, **kwargs):
                    if path == source and kind in {"ancestor_alias", "case"}:
                        return root.parent / source.name if kind == "ancestor_alias" else root / "CACHED.md"
                    return real_resolve(path, *args, **kwargs)

                with patch.object(Path, "stat", new=metadata), patch.object(Path, "resolve", new=resolved), patch.object(
                    store, "read_text", side_effect=AssertionError("invalid cached member must fail before any read")
                ):
                    errors, warnings = check_docs(root, root, store, inventory)
                self.assertEqual([], warnings)
                self.assertTrue(errors, kind)
                self.assertFalse(any("unexpectedly" in error for error in errors), errors)

    def test_family_uses_current_metadata_for_byte_limits_and_io_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "growing.md"
            write(source, "x")
            inventory = RepositoryInventory(root)
            inventory.tree_entries(root)
            write(source, "longer content")
            with patch("scripts.check_governance_core._inventory.MAX_MARKDOWN_BYTES", 1):
                files, error = inventory.markdown_files(root)
            self.assertEqual((), files)
            self.assertIn("exceeded", error or "")
            inventory = RepositoryInventory(root)
            inventory.tree_entries(root)
            real_stat = Path.stat

            def denied(path, *args, **kwargs):
                if path == source:
                    raise PermissionError("fixture denied")
                return real_stat(path, *args, **kwargs)

            with patch.object(Path, "stat", new=denied):
                files, error = inventory.markdown_files(root)
            self.assertEqual((), files)
            self.assertIn("fixture denied", error or "")

    def test_inventory_hardlink_metadata_witness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "source.txt"
            alias = root / "alias.md"
            write(target, "sanitized metadata witness\n")
            os.link(target, alias)
            with os.scandir(root) as entries:
                entry = next(item for item in entries if item.name == alias.name)
                directory_links = entry.stat(follow_symlinks=False).st_nlink
            direct_links = alias.stat(follow_symlinks=False).st_nlink
            files, error = RepositoryInventory(root).markdown_files(root)
            logger.warning("Hardlink metadata witness: DirEntry.st_nlink=%s Path.st_nlink=%s inventory_files=%s inventory_error=%s", directory_links, direct_links, len(files), error)
            self.assertGreater(direct_links, 1)
            self.assertEqual((), files)
            self.assertIn("alias", error or "")

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
        policy_path = root / "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
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

    def test_physical_lf_records_preserve_original_delimiters(self) -> None:
        cases = {"": 0, "\n": 1, "x": 1, "x\n": 1, "x\n\n": 2,
                 "x\r\ny\r\n": 2, "x\ry": 1, "x\u2028y": 1, "\ufeffx\n": 1}
        with tempfile.TemporaryDirectory() as temp:
            for index, (value, expected) in enumerate(cases.items()):
                with self.subTest(value=value):
                    path = Path(temp) / f"{index}.md"
                    write(path, value)
                    text, error = DocumentStore().read_text(path)
                    self.assertIsNone(error)
                    self.assertEqual(value, text)
                    self.assertEqual(expected, _physical_lines(text))

    def test_every_markdown_location_obeys_the_owner_boundary(self) -> None:
        locations = ("AGENTS.md", "deep-research-report.md", "guide.MD", ".hidden/untracked.md",
                     "ignored/report.md", ".governance/report.md", "docs/agents/25-docs-ssot-policy/template.md")
        for relative in locations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _policy, limit = docs_fixture(root)
                path = root / relative
                for ending in ("\n", ""):
                    for count in (limit, limit + 1):
                        write(path, "x\n" * (count - 1) + "x" + ending)
                        result = docs_result(root)
                        size_errors = [error for error in result["errors"] if "documentation exceeds" in error]
                        self.assertEqual(count > limit, bool(size_errors), result)
                        if count > limit:
                            self.assertTrue(any(str(path) in error for error in size_errors), result)

    def test_docs_inventory_reads_invalid_utf8_and_aliases_fail_explicitly(self) -> None:
        for kind in ("utf8", "alias"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                docs_fixture(root)
                path = root / "outside-docs.MD"
                if kind == "utf8":
                    write(path, b"\xff")
                else:
                    write(root / "source.txt", "source\n")
                    os.link(root / "source.txt", path)
                result = docs_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("Invalid UTF-8" in error if kind == "utf8" else "alias" in error for error in result["errors"]), result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_missing_malformed_duplicate_and_nonpositive_limits_fail(self) -> None:
        for replacement in ("", "documentation_line_limit: nope", "documentation_line_limit: 0",
                            "documentation_line_limit: -1", "documentation_line_limit: 1\ndocumentation_line_limit: 2"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                write(policy, re.sub(r"(?m)^documentation_line_limit: .+$", replacement, policy.read_text(encoding="utf-8")))
                result = docs_result(root)
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("exactly one positive documentation_line_limit" in error for error in result["errors"]), result)

    def test_owner_changes_control_acceptance_without_a_checker_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            policy, limit = docs_fixture(root)
            write(root / "report.md", "x\n" * (limit + 1))
            self.assertEqual("FAILED", docs_result(root)["status"])
            write(policy, policy.read_text(encoding="utf-8").replace(f"documentation_line_limit: {limit}", f"documentation_line_limit: {limit + 1}"))
            self.assertEqual("PASSED", docs_result(root)["status"])

    def test_required_branches_and_optional_agency_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            policy, _limit = docs_fixture(root)
            agents = root / "AGENTS.md"
            write(agents, agents.read_text(encoding="utf-8") + "\n## Documentation SSOT Policy (Hard Gate)\n- `docs/project/unrequested/unrequested.md`\n")
            self.assertEqual("PASSED", docs_result(root, mode="project_docs")["status"])
            required, errors = _required_project_paths(parse_markdown(policy.read_text(encoding="utf-8")))
            self.assertEqual([], errors)
            for relative in required[:3]:
                target = root / relative
                saved = target.read_bytes()
                target.unlink()
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any(relative in error for error in result["errors"]), result)
                write(target, saved)

    def test_invalid_required_branch_declarations_fail_without_tracebacks(self) -> None:
        cases = ("- `../escape/`: unsafe", "- `nested/child/`: unsafe", "- `bad\\name/`: unsafe",
                 "- `repeat/`: first\n- `repeat/`: duplicate", "- missing/: malformed", "")
        for body in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                value = policy.read_text(encoding="utf-8")
                value = re.sub(r"(?ms)^## Required project-doc branches\n.*?(?=^## )", "## Required project-doc branches\n" + body + "\n\n", value)
                write(policy, value)
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertTrue(any("Docs policy" in error for error in result["errors"]), result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_vendored_docs_mode_and_ignored_untracked_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance = root / ".governance"
            _policy, limit = docs_fixture(root, governance)
            self.assertEqual("PASSED", docs_result(root, governance)["status"])
            self.assertEqual("PASSED", docs_result(root, governance, "project_docs")["status"])
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, timeout=10)
            write(root / ".gitignore", "ignored/\n")
            write(root / "ignored/report.MD", "x\n" * (limit + 1))
            result = docs_result(root, governance)
            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(any("ignored" in error and "documentation exceeds" in error for error in result["errors"]), result)

    def test_policy_alias_missing_section_and_duplicate_sections_fail(self) -> None:
        for kind in ("alias", "missing", "duplicate"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy, _limit = docs_fixture(root)
                if kind == "alias":
                    source = policy.with_suffix(".source")
                    policy.replace(source)
                    os.link(source, policy)
                else:
                    text = policy.read_text(encoding="utf-8")
                    text = text.replace("## Required project-doc branches", "## Other") if kind == "missing" else text + "\n## Required project-doc branches\n- `another/`: duplicate section\n"
                    write(policy, text)
                result = docs_result(root, mode="project_docs")
                self.assertEqual("FAILED", result["status"], result)
                self.assertFalse(any("unexpectedly" in error for error in result["errors"]), result)

    def test_project_docs_rejects_readme_alias_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs_fixture(root)
            readme = root / "README.md"
            source = root / "README.md.source"
            readme.replace(source)
            os.link(source, readme)
            result = docs_result(root, mode="project_docs")
            self.assertEqual("FAILED", result["status"], result)
            self.assertTrue(any("README.md" in error and "must not be an alias" in error for error in result["errors"]), result)

    def test_docs_mode_preloads_repository_markdown_without_reading_python(self) -> None:
        root = REPOSITORY_ROOT
        seen: list[Path] = []
        original = RepositoryInventory.tree_entries

        def record(inventory: RepositoryInventory, scan_root: Path):
            seen.append(scan_root.resolve())
            return original(inventory, scan_root)

        with patch.object(RepositoryInventory, "tree_entries", new=record), patch.object(
            RepositoryInventory, "python_files", side_effect=AssertionError("docs must not read Python")
        ):
            result = docs_result(root)
        self.assertEqual("PASSED", result["status"], result)
        self.assertIn(root.resolve(), seen)
        self.assertIn((root / "docs").resolve(), seen)

    def test_report_reconciles_the_selected_work_universe(self) -> None:
        result = docs_result(REPOSITORY_ROOT)
        self.assertEqual(["docs"], result["planned"])
        self.assertEqual(result["planned"], result["eligible"])
        self.assertEqual(result["planned"], result["executed"])
        self.assertEqual([], result["skipped"])
        self.assertEqual([], result["failed"])

    def test_router_target_and_doc_type_contract_helpers_reject_invalid_values(self) -> None:
        router = parse_markdown("# Router\n\n- [ghost](ghost.md) - route. Required when: needed.\n")
        targets, errors = router_targets(router)
        self.assertEqual(["ghost.md"], targets)
        self.assertEqual([], errors)
        policy = "doc_type: policy|reference|runbook|playbook|decision|generated\n"
        self.assertNotIn("nonsense", declared_doc_types(policy))

    def test_docs_check_rejects_dead_router_target_and_invalid_doc_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs_fixture(root)
            write(root / "docs/docs_index.md", "# Docs\n\n- [docs](docs.md) - docs. Required when: reading docs.\n- [ghost](ghost.md) - ghost. Required when: reading ghost.\n")
            write(root / "docs/docs.md", "---\ndoc_type: nonsense\nssot_owner: owner\nupdate_trigger: changes\n---\n\n# Docs\n")
            errors, _warnings = check_docs(root, root, DocumentStore(), RepositoryInventory(root))
            self.assertTrue(any("ghost.md" in error for error in errors), errors)
            self.assertTrue(any("unsupported doc_type" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
