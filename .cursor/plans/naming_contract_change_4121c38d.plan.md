---
name: Naming contract change
overview: Complete the folder-owned public contract naming shift so runtime entrypoints, docs routers, validator behavior, and active guidance all align to one clean SSOT model with no legacy residue in the active contract surface.
todos:
  - id: decision-doc
    content: Record the contract-family decision and docs-router migration in the authority-decision doc while keeping family-level policy ownership in the correct SSOT docs.
    status: completed
  - id: registry-contract
    content: Maintain one machine-readable contract registry that resolves canonical contract filenames by contract family, artifact kind, and language.
    status: completed
  - id: consumers
    content: Keep policy docs, validators, README references, architecture docs, and template docs aligned to the derived contract rules instead of hardcoded legacy filenames.
    status: completed
isProject: false
---

# Naming Contract Implementation Record

## Final Authority State
- Top policy authority: [AGENTS.md](AGENTS.md)
- Runtime contract-family owner: [docs/agents/35-authority-bounded-modules/authority-bounded-modules.md](docs/agents/35-authority-bounded-modules/authority-bounded-modules.md)
- Docs contract-family owner: [docs/agents/25-docs-ssot-policy/docs-ssot-policy.md](docs/agents/25-docs-ssot-policy/docs-ssot-policy.md)
- Migration decision owner: [docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md](docs/agents/22-ssot-authority-decisions/ssot-authority-decisions.md)
- Machine-readable filename owner: [scripts/entrypoint_contracts.json](scripts/entrypoint_contracts.json)

## Active Contract
- Runtime code folders expose exactly one canonical public owner file.
- Runtime owner filenames are derived from `scripts/entrypoint_contracts.json` as `<authority>_<entrypoint_token>.<extension>`.
- Docs folders with narrative content expose:
  - exactly one canonical router file: `<authority>_index.md`
  - one-or-more router-linked public leaf docs in the same folder authority
- Docs primary public leaf filenames are derived from `scripts/entrypoint_contracts.json` through:
  - `plain_folder_default`
  - `numbered_governance_folder`
  - `dated_evidence_folder`
- Router-only docs folders remain valid only when they are artifact-first and expose no public narrative leaf docs.
- Deeper runtime identity files such as `SKILL.md` and `mcp.json` remain outside this naming contract and stay governed by their existing SSOT owners.

## Implemented Registry Surface
```json
{
  "version": 1,
  "ssot_owner": {
    "runtime_code": "docs/agents/35-authority-bounded-modules/authority-bounded-modules.md",
    "docs": "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
  },
  "runtime_code": {
    "filename_pattern": "<authority>_<entrypoint_token>.<extension>"
  },
  "docs": {
    "router_pattern": "<authority>_index.md",
    "authority_resolution": {
      "numbered_governance_folder_regex": "^[0-9]{2}-(?P<authority>.+)$",
      "dated_evidence_folder_regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+$",
      "dated_evidence_authority": "evidence"
    },
    "public_leaf_model": {
      "default": "one_or_more",
      "minimum_public_leaf_count": 1,
      "router_only_exception_kind": "artifact_first"
    },
    "public_leaf_patterns": {
      "plain_folder_default": "<authority>.md",
      "numbered_governance_folder": "<authority>.md",
      "dated_evidence_folder": "evidence.md"
    },
    "public_leaf_exposure": {
      "source_of_truth": "router_links",
      "require_distilled_route_line": true
    },
    "explicit_family_exceptions": {
      "identity_files": ["SKILL.md", "mcp.json"]
    }
  }
}
```

## Consumer Alignment
- [scripts/check_docs_ssot.ps1](scripts/check_docs_ssot.ps1) enforces router presence, direct-child routing, canonical primary leaf presence, exact-case link matching, and docs header policy.
- [scripts/check_project_docs.ps1](scripts/check_project_docs.ps1) enforces project-doc router and primary-leaf linkage with explicit malformed-route diagnostics.
- [scripts/check_governance_core/_manifest_and_docs.py](scripts/check_governance_core/_manifest_and_docs.py) mirrors the same contract logic for cross-platform validation.
- [scripts/_entrypoint_contracts.ps1](scripts/_entrypoint_contracts.ps1) and [scripts/check_governance_core/_entrypoint_contracts.py](scripts/check_governance_core/_entrypoint_contracts.py) both require the same docs leaf-pattern keys from the registry.
- [scripts/check_folder_architecture/check_folder_architecture_main.py](scripts/check_folder_architecture/check_folder_architecture_main.py) fails closed on malformed runtime registry data instead of synthesizing default entrypoint names.
- [scripts/check_governance_core/check_governance_core_main.py](scripts/check_governance_core/check_governance_core_main.py) now treats `check_docs_ssot` as the live docs gate and no longer treats docs-router regression tests as runtime validation.
- [scripts/check_docs_router_contract/check_docs_router_contract_main.py](scripts/check_docs_router_contract/check_docs_router_contract_main.py) remains a regression-test harness for fixture-backed router edge cases, not a second live SSOT gate.
- [.cursor/agents/docs-reviewer.md](.cursor/agents/docs-reviewer.md) now references the live `*_index.md` project-doc structure and the enforced `doc_type` token model.

## Verification Record
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1`
- `python scripts/check_docs_router_contract/check_docs_router_contract_main.py`
- `python scripts/check_folder_architecture/check_folder_architecture_main.py`
- `python -m unittest -v scripts.check_folder_architecture.test_main`
- `python scripts/check_governance_core/check_governance_core_main.py`

## Failure-Path Witnesses
- Missing docs tree: `scripts/check_docs_ssot.ps1` fails non-zero with `Missing required docs/ folder: ...`
- Malformed runtime registry: folder-architecture checks now report registry-key errors and do not fall back to synthetic `<authority>_main.py` names
- Case-mismatched router links: docs checks now fail on `Goal.md` vs `goal.md`
- Rooted scope paths: folder-architecture tests now reject entries such as `/scripts`

## Clean-Shift Result
- No active live validator or policy doc relies on legacy `index.md` routers.
- No active live validator synthesizes runtime entrypoint defaults when registry data is malformed.
- No active machine-readable registry field remains as unused naming guidance in the docs leaf model.
- No active governance-core message describes regression tests as live contract validation.
