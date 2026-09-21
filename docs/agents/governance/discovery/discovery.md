---
doc_type: runbook
ssot_owner: docs/agents/governance/discovery/discovery.md
update_trigger: retrieval evidence fields, read bounds, or discovery signals change
---

# Discovery

Jurisdiction: role-bounded source retrieval, read bounds, discovery signals, conflict precedence for retrieved context, and retrieval evidence.

## Trust routing, verify decisions

- The active role and source boundary MUST be confirmed before retrieval begins.
- Search results MUST be treated as candidates, never as authority.
- Candidates MUST be verified against their declared owner and affected consumers.
- A search hit MUST NOT satisfy a full-read obligation.
- Verify these decision-critical facts only:
  - which authority owns the change.
  - which manifest profile matched and why.
  - which files will be edited.
  - which tests or checks witness the outcome.
  - which facts stay `UNKNOWN` and which inaccessible required files stop work.

## Retrieval evidence

- Every source-reading agent MUST record these before returning a result:
  - role and confirmed read scope.
  - owner sources actually read.
  - decision-critical paths or symbols verified.
  - inaccessible required sources and the resulting `HOLD` or finding.
  - verification owners or evidence used.
- The record MUST be reportable concisely to the assigned parent.
- Governance Agent MUST additionally record matched profiles or fallback.
- Governance Agent MUST additionally record routing mode and routed authorities read.
- Roles other than Governance Agent MUST NOT use the manifest to select repository or project sources.
- When a profile matched and semantic search is available, `semantic_queries.<profile>` runs first when it adds context not already loaded; witness: the recorded query set.

## Bounded repo reads

- Record the authorized root or keyed candidate set before searching.
- Record search ordering, validation, termination condition, and measured cost.
- Cache validated path-to-owner and document lookups for the active scope.
- Invalidate a cached entry when its source changes.
- Read in full:
  - the file being edited.
  - the current SSOT owner for the changed responsibility.
  - nearby tests, config owners, and callers affecting behavior or verification.
  - `README.md` section "Checks" before choosing verification commands.
- Governing and touched sources MUST be read in full regardless of size.
- Bounded section reads are permitted only for supporting discovery candidates.
- Record a bounded-read candidate's supporting role.
- A candidate that becomes governing or touched MUST then be read in full.
- Role-separated agents MUST collectively cover required sources.
- Retrieval MUST NOT expand any role's permissions or define lifecycle behavior; the lifecycle owner takes precedence.

## Repo discovery signals

- Signals below are examples, not a closed capability inventory.
- Constants/config: `constants`, `config`, `settings`, `defaults`, `env`, `CFG_`, `CONST_`, `SHEET_`, `HDR_`, `STATUS_`.
- Logging/errors: `logging.getLogger(__name__)`, `errors`, `exceptions`, `ErrorCode`, `ValidationError`.
- Excel: `agents-manifest.yaml` `profiles.excel_automation.detect.keywords`, `.code_patterns`, `.file_globs`.
- GUI: `agents-manifest.yaml` `profiles.gui_task.detect.keywords`, `.code_patterns`.
- Documentation owners: `README.md`, `AGENTS.md`, and the project docs branch under `docs/project/`; loaded instruction surfaces: `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/**`, their `@path` imports, auto-memory `MEMORY.md`, `.cursor/rules/**`, `.codex/config.toml`.
- Workflows: `workflow`, `pipeline`, `runner`, `dispatcher`, `run_`, `main()`.
- Detection lists MUST stay SSOT in `agents-manifest.yaml`; duplication here is Prohibited.

## Untrusted and stale context

- Factual assertions, tickets, chat notes, external claims, cached search, and model memory require provenance.
- Such context MUST be verified against its declared fact owner before being presented as runtime truth.
- Conflict precedence:
  - verified runtime evidence establishes what happens.
  - the declared code, config, or data owner establishes the applicable contract.
  - `agents-manifest.yaml` wins only for Governance Agent governance-authority routing.
  - `README.md` section "Checks" wins for repeatable verification commands.
- Binding user intent and explicit user decisions retain their authority.
- A referenced symbol, path, or config key that matters MUST be verified to still exist.

## Anti-patterns

- Prohibited: loading broad doc packs when a narrow profile already supplies the owner.
- Prohibited: repeating generic search recipes instead of reporting the actual witness.
- Prohibited: treating one search as proof no other owner or call site exists.
- Prohibited: editing from an error message, summary, or stale memory.
- Prohibited: treating routed non-owner documents as stronger than live code or config.
