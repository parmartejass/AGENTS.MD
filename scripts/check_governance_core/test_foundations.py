from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.check_governance_core._test_support import install_foundations, live_foundations, write
from scripts.check_governance_core.check_governance_core_main import resolve_documents, run_checks


def _manifest(authority: str = "docs/agents/other.md") -> str:
    source = Path(__file__).parent / "fixtures/manifest_valid.yaml"
    return source.read_text(encoding="utf-8").replace("__AUTHORITY__", authority)


def _fixture(root: Path) -> dict[str, str]:
    declared = install_foundations(root)
    write(root / "docs/agents/agents_index.md", "# Agents\n")
    write(root / "docs/agents/other.md", "# Other owner\n")
    write(root / "agents-manifest.yaml", _manifest())
    return declared


def _records(root: Path, *, repo: Path | None = None) -> dict[str, dict]:
    result = run_checks({"repo_root": str(repo or root), "governance_root": str(root)})
    return {record["id"]: record for record in result["checks"]}


class FoundationContractTests(unittest.TestCase):
    def assert_foundation_failure(self, root: Path) -> None:
        records = _records(root)
        for name in ("governance", "manifest"):
            self.assertEqual("FAILED", records[name]["status"], records[name])
            self.assertFalse(any("unexpectedly" in error for error in records[name]["errors"]), records[name])

    def test_fixture_membership_is_gated_by_public_governance_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = _fixture(root)
            with patch("scripts.check_governance_core._test_support.REPOSITORY_ROOT", root), \
                 patch("scripts.check_governance_core._test_support.run_checks", wraps=run_checks) as boundary:
                self.assertEqual(declared, live_foundations()[1])
                boundary.assert_called_once_with({"repo_root": str(root), "governance_root": str(root)})
                owner = root / declared["constitution"]
                write(owner, owner.read_text(encoding="utf-8").replace(
                    "foundation_contract_version: 1", "foundation_contract_version: 9"))
                with self.assertRaisesRegex(ValueError, "foundation_contract_version"):
                    live_foundations()
                self.assertEqual(2, boundary.call_count)

    def test_fixture_propagates_public_validation_failure_without_extracting(self) -> None:
        result = {"status": "FAILED_VALIDATION", "checks": [], "errors": ["owner root unavailable"]}
        with patch("scripts.check_governance_core._test_support.run_checks", return_value=result), \
             patch.object(Path, "read_text", side_effect=AssertionError("unvalidated owner read")):
            with self.assertRaisesRegex(ValueError, "owner root unavailable"):
                live_foundations()

    def test_live_standalone_and_contained_vendored_foundations(self) -> None:
        live = Path(__file__).resolve().parents[2]
        for name in ("governance", "manifest"):
            self.assertEqual("PASSED", _records(live)[name]["status"])
        for relative in ("", ".governance"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                repo = Path(temp)
                root = repo / relative
                _fixture(root)
                records = _records(root, repo=repo)
                for name in ("governance", "manifest"):
                    self.assertEqual("PASSED", records[name]["status"], records[name])

    def test_missing_malformed_duplicate_and_unsupported_declarations(self) -> None:
        section, declared = live_foundations()
        version = "foundation_contract_version: 1"
        markers = {role: f"<!-- foundation-authority: {role}={path} -->" for role, path in declared.items()}
        first = next(iter(markers.values()))
        cases = {
            "missing_section": "",
            "duplicate_section": section + "\n" + section,
            "missing_version": section.replace(version, ""),
            "duplicate_version": section.replace(version, version + "\n" + version),
            "unsupported_version": section.replace(version, "foundation_contract_version: 2"),
            "malformed_version": section.replace(version, "foundation_contract_version = 1"),
            "malformed_marker": section.replace(first, first.replace("=", ": ", 1)),
            "duplicate_role": section.replace(first, first + "\n" + first),
            "unknown_role": section.replace(first, first.replace("constitution=", "unknown=")),
            "duplicate_path": section.replace("docs_policy=" + declared["docs_policy"], "docs_policy=" + declared["coding_principles"]),
            "outside_section": section + "\n## Other\n" + first,
            "wrong_constitution": section.replace("constitution=" + declared["constitution"], "constitution=docs/agents/other.md"),
            "wrong_lifecycle": section.replace("orchestration=" + declared["orchestration"], "orchestration=docs/agents/other.md"),
        }
        cases.update({"missing_" + role: section.replace(marker, "") for role, marker in markers.items()})
        for name, mutated in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _fixture(root)
                owner = root / declared["constitution"]
                write(owner, owner.read_text(encoding="utf-8").replace(section, mutated))
                self.assert_foundation_failure(root)

    def test_fenced_quoted_and_indented_examples_do_not_supply_membership(self) -> None:
        section, declared = live_foundations()
        examples = (
            "```md\n" + section + "```\n",
            "\n".join("> " + line for line in section.splitlines()) + "\n",
            "\n".join("    " + line for line in section.splitlines()) + "\n",
        )
        for example in examples:
            for retain in (False, True):
                with self.subTest(example=example[:20], retain=retain), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    _fixture(root)
                    owner = root / declared["constitution"]
                    value = owner.read_text(encoding="utf-8")
                    write(owner, (value if retain else value.replace(section, "")) + "\n" + example)
                    if retain:
                        self.assertEqual("PASSED", _records(root)["governance"]["status"])
                    else:
                        self.assert_foundation_failure(root)

    def test_unsafe_noncanonical_missing_nonregular_and_invalid_utf8_targets(self) -> None:
        for case in ("absolute", "traversal", "wrong_case", "stream", "backslash", "trailing_space",
                     "non_markdown", "missing", "nonregular", "invalid_utf8", "hardlink"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = _fixture(root)
                value = declared["coding_principles"]
                target = root / value
                alternatives = {
                    "absolute": target.as_posix(), "traversal": "../outside.md",
                    "wrong_case": value.upper(), "stream": value + ":stream.md",
                    "backslash": value.replace("/", "\\"), "trailing_space": value + " ",
                    "non_markdown": "source.txt",
                }
                if case in alternatives:
                    owner = root / declared["constitution"]
                    write(owner, owner.read_text(encoding="utf-8").replace("coding_principles=" + value, "coding_principles=" + alternatives[case]))
                elif case == "invalid_utf8":
                    write(target, b"\xff")
                else:
                    original = target.read_bytes()
                    target.unlink()
                    if case == "nonregular":
                        target.mkdir()
                    elif case == "hardlink":
                        source = root / "source.md"
                        write(source, original)
                        os.link(source, target)
                self.assert_foundation_failure(root)

    def test_file_symlink_and_ancestor_reparse_metadata_reject_before_read(self) -> None:
        for alias in ("file_symlink", "file_reparse", "ancestor_reparse"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = _fixture(root)
                target = root / declared["coding_principles"]
                aliased = target.parent if alias == "ancestor_reparse" else target
                real_stat = Path.stat
                real_open = Path.open
                opened = []

                def metadata(path, *args, **kwargs):
                    result = real_stat(path, *args, **kwargs)
                    if path != aliased or kwargs.get("follow_symlinks", True):
                        return result
                    values = {name: getattr(result, name) for name in dir(result) if name.startswith("st_")}
                    if alias == "file_symlink":
                        values["st_mode"] = stat.S_IFLNK | 0o777
                    else:
                        values["st_file_attributes"] = values.get("st_file_attributes", 0) | 0x400
                    return SimpleNamespace(**values)

                def capture(path, *args, **kwargs):
                    opened.append(path)
                    return real_open(path, *args, **kwargs)

                with patch.object(Path, "stat", metadata), patch.object(Path, "open", capture):
                    self.assert_foundation_failure(root)
                self.assertNotIn(target, opened)

    def test_read_failure_has_explicit_foundation_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = _fixture(root)
            target = root / declared["coding_principles"]
            original = Path.open

            def denied(path, *args, **kwargs):
                if path == target:
                    raise PermissionError("foundation source denied")
                return original(path, *args, **kwargs)

            with patch.object(Path, "open", denied):
                records = _records(root)
            self.assertTrue(any("foundation source denied" in error for error in records["governance"]["errors"]), records)
            self.assertEqual("FAILED", records["manifest"]["status"])

    def test_every_foundation_is_nonselectable_in_fallback_and_profiles(self) -> None:
        _, live = live_foundations()
        for role in live:
            for location in ("fallback", "profile"):
                with self.subTest(role=role, location=location), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    declared = _fixture(root)
                    original = _manifest()
                    old = "'docs/agents/other.md'"
                    if location == "fallback":
                        value = original.replace(old, repr(declared[role]), 1)
                    else:
                        index = original.rindex(old)
                        value = original[:index] + original[index:].replace(old, repr(declared[role]), 1)
                    write(root / "agents-manifest.yaml", value)
                    record = _records(root)["manifest"]
                    self.assertEqual("FAILED", record["status"], record)
                    self.assertTrue(any("mandatory foundation" in error for error in record["errors"]), record)

    def test_manifest_case_and_physical_aliases_cannot_select_foundations(self) -> None:
        for alias in ("case", "hardlink", "symlink"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                declared = _fixture(root)
                relative = declared["coding_principles"]
                if alias == "case":
                    candidate = relative.upper()
                else:
                    candidate = "docs/agents/alias.md"
                    if alias == "hardlink":
                        os.link(root / relative, root / candidate)
                    else:
                        try:
                            (root / candidate).symlink_to(root / relative)
                        except OSError as exc:
                            self.skipTest(f"native file symlink unavailable; metadata rejection tested separately: {exc}")
                write(root / "agents-manifest.yaml", _manifest(candidate))
                self.assertEqual("FAILED", _records(root)["manifest"]["status"])

    def test_declared_path_change_controls_selection_without_corpus_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = _fixture(root)
            request = {"repo_root": str(root), "governance_root": str(root)}
            before = resolve_documents(request)
            old = declared["coding_principles"]
            new = "docs/agents/extra/extra.md"
            write(root / new, (root / old).read_bytes())
            owner = root / declared["constitution"]
            write(owner, owner.read_text(encoding="utf-8").replace("coding_principles=" + old, "coding_principles=" + new))
            write(root / "agents-manifest.yaml", _manifest(old))
            records = _records(root)
            self.assertEqual("PASSED", records["governance"]["status"], records)
            self.assertEqual("PASSED", records["manifest"]["status"], records)
            self.assertEqual(before, resolve_documents(request))
            write(root / "agents-manifest.yaml", _manifest(new))
            first = _records(root)
            self.assertEqual("FAILED", first["manifest"]["status"])
            self.assertEqual(first, _records(root))

    def test_narrow_modes_and_research_do_not_depend_on_startup_declarations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = _fixture(root)
            request = {"repo_root": str(root), "governance_root": str(root)}
            before = {mode: run_checks({**request, "mode": mode}) for mode in ("docs", "project_docs")}
            corpus = resolve_documents(request)
            owner = root / declared["constitution"]
            write(owner, owner.read_text(encoding="utf-8").replace("foundation_contract_version: 1", "foundation_contract_version: 9"))
            write(root / "agents-manifest.yaml", "malformed: [manifest\n")
            for mode, expected in before.items():
                self.assertEqual(expected, run_checks({**request, "mode": mode}))
            self.assertEqual(corpus, resolve_documents(request))
            self.assert_foundation_failure(root)

    def test_shared_run_cache_reads_each_foundation_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            declared = _fixture(root)
            targets = {root / value: 0 for value in declared.values()}
            original = Path.open

            def capture(path, *args, **kwargs):
                if path in targets:
                    targets[path] += 1
                return original(path, *args, **kwargs)

            with patch.object(Path, "open", capture):
                records = _records(root)
            self.assertEqual("PASSED", records["governance"]["status"], records)
            self.assertEqual({path: 1 for path in targets}, targets)


if __name__ == "__main__":
    unittest.main()
