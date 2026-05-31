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


class ProjectAuthorityMemoryDocTests(unittest.TestCase):
    def test_record_shape_rejects_malformed_status_and_blank_values(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/architecture/protected-behavior.md",
            """
### PB-20260531-001 - Bad record
- Status: `active` trailing-garbage
- Behavior:
- Scope: TODO
- Protected because: <placeholder>
- Current mechanism: `owner`
- Required equivalence: `N/A`
- Verification: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Weakening rule: `N/A`
- Related data truths: `N/A`
- Superseded by: `N/A`
""".lstrip(),
            prefix="PB",
            required_fields=[
                "Status",
                "Behavior",
                "Scope",
                "Protected because",
                "Current mechanism",
                "Required equivalence",
                "Verification",
                "Evidence/version",
                "Re-verification trigger",
                "Weakening rule",
                "Related data truths",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            duplicate_key_fields=["Behavior", "Scope"],
        )

        self.assertTrue(any("invalid status" in error for error in errors), errors)
        self.assertTrue(any("blank or placeholder value for field: Behavior" in error for error in errors), errors)
        self.assertTrue(any("blank or placeholder value for field: Scope" in error for error in errors), errors)
        self.assertTrue(
            any("blank or placeholder value for field: Protected because" in error for error in errors),
            errors,
        )

    def test_record_shape_rejects_malformed_heading(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/learning/changelog.md",
            """
### CH-not-a-date - Bad
- Date: `2026-05-31`
- Status: `proposed`
- Change type: `governance-policy`
- Changed owners/files: `AGENTS.md`
- Current work: `CW-20260531-999`
- Context: `N/A`
- Decision/change: `N/A`
- Validation: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Commit/push state: `not-required + reason:test`
- Superseded by: `N/A`
- Follow-up required: `N/A`
""".lstrip(),
            prefix="CH",
            required_fields=[
                "Date",
                "Status",
                "Change type",
                "Changed owners/files",
                "Current work",
                "Context",
                "Decision/change",
                "Validation",
                "Evidence/version",
                "Commit/push state",
                "Superseded by",
                "Follow-up required",
            ],
            allowed_statuses={"proposed", "accepted", "corrected", "deprecated", "superseded", "rolled-back"},
            duplicate_key_fields=["Change type", "Changed owners/files", "Decision/change"],
        )

        self.assertTrue(any("malformed CH record heading" in error for error in errors), errors)

    def test_allow_empty_record_shape_rejects_malformed_record_like_heading(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            """
## Records

This is an explicit reviewed-empty registry state.
- Reviewed-empty date: `2026-05-31`

### DT bad malformed heading
- Status: `active`
""".lstrip(),
            prefix="DT",
            required_fields=["Status", "Truth type", "Owner SSOT"],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            allow_empty=True,
            empty_marker="Reviewed-empty date:",
        )

        self.assertTrue(any("malformed DT record heading" in error for error in errors), errors)

    def test_allow_empty_record_shape_rejects_lowercase_and_underscore_record_like_headings(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            """
## Records

This is an explicit reviewed-empty registry state.
- Reviewed-empty date: `2026-05-31`

### dt-20260531-001 - lower

### DT_20260531_002 - underscore
""".lstrip(),
            prefix="DT",
            required_fields=["Status", "Truth type", "Owner SSOT"],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            allow_empty=True,
            empty_marker="Reviewed-empty date:",
        )

        self.assertGreaterEqual(sum("malformed DT record heading" in error for error in errors), 2, errors)

    def test_record_shape_rejects_duplicate_field_lines(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            """
### DT-20260531-001 - Duplicate field
- Status: `active`
- Status: `invalid`
- Truth type: `config`
- Owner SSOT: `config/settings.json`
- Doc role: `router`
- Scope: `export`
- Statement: `N/A`
- Provenance: `N/A`
- Consumers: `N/A`
- Validation: `N/A`
- Change rule: `N/A`
- Related protected behavior: `N/A`
- Related rules: `N/A`
- Supersedes: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Superseded by: `N/A`
""".lstrip(),
            prefix="DT",
            required_fields=[
                "Status",
                "Truth type",
                "Owner SSOT",
                "Doc role",
                "Scope",
                "Statement",
                "Provenance",
                "Consumers",
                "Validation",
                "Change rule",
                "Related protected behavior",
                "Related rules",
                "Supersedes",
                "Evidence/version",
                "Re-verification trigger",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            allowed_field_values={
                "Truth type": {"config"},
                "Doc role": {"router"},
            },
        )

        self.assertTrue(any("contains duplicate field: Status" in error for error in errors), errors)
        self.assertTrue(any("invalid status: invalid" in error for error in errors), errors)
        self.assertEqual(1, sum("contains duplicate field: Status" in error for error in errors), errors)

    def test_data_truth_record_shape_rejects_invalid_taxonomy_values(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            """
### DT-20260531-001 - Invalid taxonomy
- Status: `active`
- Truth type: `business-rule`
- Owner SSOT: `config/settings.json`
- Doc role: `ownerish`
- Scope: `export`
- Statement: `N/A`
- Provenance: `N/A`
- Consumers: `N/A`
- Validation: `N/A`
- Change rule: `N/A`
- Related protected behavior: `N/A`
- Related rules: `N/A`
- Supersedes: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Superseded by: `N/A`
""".lstrip(),
            prefix="DT",
            required_fields=[
                "Status",
                "Truth type",
                "Owner SSOT",
                "Doc role",
                "Scope",
                "Statement",
                "Provenance",
                "Consumers",
                "Validation",
                "Change rule",
                "Related protected behavior",
                "Related rules",
                "Supersedes",
                "Evidence/version",
                "Re-verification trigger",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            allowed_field_values={
                "Truth type": {"config"},
                "Doc role": {"owner", "router", "provenance", "interpretation", "validation"},
            },
        )

        self.assertTrue(any("invalid Truth type: business-rule" in error for error in errors), errors)
        self.assertTrue(any("invalid Doc role: ownerish" in error for error in errors), errors)

    def test_data_truth_record_shape_requires_provenance_and_consumers(self) -> None:
        errors: list[str] = []
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            """
### DT-20260531-001 - Missing routing fields
- Status: `active`
- Truth type: `config`
- Owner SSOT: `config/settings.json`
- Doc role: `router`
- Scope: `export`
- Statement: `N/A`
- Validation: `N/A`
- Change rule: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Superseded by: `N/A`
""".lstrip(),
            prefix="DT",
            required_fields=[
                "Status",
                "Truth type",
                "Owner SSOT",
                "Doc role",
                "Scope",
                "Statement",
                "Provenance",
                "Consumers",
                "Validation",
                "Change rule",
                "Related protected behavior",
                "Related rules",
                "Supersedes",
                "Evidence/version",
                "Re-verification trigger",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
        )

        self.assertTrue(any("missing required field: Provenance" in error for error in errors), errors)
        self.assertTrue(any("missing required field: Consumers" in error for error in errors), errors)

    def test_record_shape_rejects_duplicate_structural_authority_key(self) -> None:
        errors: list[str] = []
        text = """
### DT-20260531-001 - First
- Status: `active`
- Truth type: `config`
- Owner SSOT: `config/settings.json`
- Doc role: `router`
- Scope: `export`
- Statement: `N/A`
- Provenance: `N/A`
- Consumers: `N/A`
- Validation: `N/A`
- Change rule: `N/A`
- Related protected behavior: `N/A`
- Related rules: `N/A`
- Supersedes: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Superseded by: `N/A`

### DT-20260531-002 - Duplicate
- Status: `active`
- Truth type: `config`
- Owner SSOT: `config/settings.json`
- Doc role: `router`
- Scope: `export`
- Statement: `N/A`
- Provenance: `N/A`
- Consumers: `N/A`
- Validation: `N/A`
- Change rule: `N/A`
- Related protected behavior: `N/A`
- Related rules: `N/A`
- Supersedes: `N/A`
- Evidence/version: `2026-05-31 fixture`
- Re-verification trigger: `owner changes`
- Superseded by: `N/A`
""".lstrip()
        MANIFEST_AND_DOCS._validate_record_shape(
            errors,
            "docs/project/data-truth/data-truth.md",
            text,
            prefix="DT",
            required_fields=[
                "Status",
                "Truth type",
                "Owner SSOT",
                "Doc role",
                "Scope",
                "Statement",
                "Provenance",
                "Consumers",
                "Validation",
                "Change rule",
                "Related protected behavior",
                "Related rules",
                "Supersedes",
                "Evidence/version",
                "Re-verification trigger",
                "Superseded by",
            ],
            allowed_statuses={"active", "proposed", "deprecated", "superseded"},
            duplicate_key_fields=["Truth type", "Owner SSOT", "Scope"],
        )

        self.assertTrue(any("duplicate structural authority key" in error for error in errors), errors)

