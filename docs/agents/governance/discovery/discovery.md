---
doc_type: runbook
ssot_owner: docs/agents/governance/discovery/discovery.md
update_trigger: retrieval evidence fields, read bounds, or discovery signals change
---

# Discovery

Jurisdiction: role-bounded source retrieval, read bounds, discovery signals, conflict precedence for retrieved context, and retrieval evidence.

## Trust routing, verify decisions

- The active role and source boundary MUST be confirmed before retrieval begins.
- MUST treat search results as candidates only.
- Candidates MUST be verified against their declared owner and affected consumers.
- A full-read obligation MUST be met by a full read, not by a search hit.
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
- When a profile matched and semantic search is available, `semantic_queries.<profile>` runs first if it adds context not already loaded. Witness: the recorded query set.

## Bounded repo reads

- Record the authorized root or keyed candidate set before searching.
- Record the FP-26 bounds for each search.
- Cache validated path-to-owner and document lookups for the active scope.
- Invalidate a cached entry when its source changes.
- Read in full:
  - the file being edited.
  - the current SSOT owner for the changed responsibility.
  - nearby tests, config owners, and callers affecting behavior or verification.
  - `README.md` section "Checks" before choosing verification commands.
- Bounded section reads are permitted only for supporting discovery candidates.
- Record a bounded-read candidate's supporting role.
- Role-separated agents MUST collectively cover required sources.
- Retrieval MUST keep each role's permissions unchanged.
- Retrieval MUST leave lifecycle behavior to the lifecycle owner, which takes precedence.

## Repo discovery signals

- Signals below are examples, not a closed capability inventory.
- Constants/config: `constants`, `config`, `settings`, `defaults`, `env`, `CFG_`, `CONST_`, `SHEET_`, `HDR_`, `STATUS_`.
- Logging/errors: `logging.getLogger(__name__)`, `errors`, `exceptions`, `ErrorCode`, `ValidationError`.
- Excel: `agents-manifest.yaml` `profiles.excel_automation.detect.keywords`, `.code_patterns`, `.file_globs`.
- GUI: `agents-manifest.yaml` `profiles.gui_task.detect.keywords`, `.code_patterns`.
- Documentation owners: `README.md`, `AGENTS.md`, and the project docs branch under `docs/project/`.
- Loaded instruction surfaces: `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/**`, their `@path` imports, auto-memory `MEMORY.md`, `.cursor/rules/**`, `.codex/config.toml`.
- Workflows: `workflow`, `pipeline`, `runner`, `dispatcher`, `run_`, `main()`.
- Detection lists MUST stay in `agents-manifest.yaml` alone; the signals here are examples only.

## Untrusted and stale context

- Factual assertions, tickets, chat notes, external claims, cached search, and model memory require provenance.
- Such context MUST be verified against its declared fact owner before being presented as runtime truth.
- Conflict precedence:
  - verified runtime evidence establishes what happens.
  - the declared code, config, or data owner establishes the applicable contract.
  - `agents-manifest.yaml` wins only for Governance Agent governance-authority routing.
  - repeatable verification commands follow the evidence owner's verification floors.
- Binding user intent and explicit user decisions keep the authority the constitutional User Prompt Intake and Durable Project Truth contract gives them.
- A referenced symbol, path, or config key that matters MUST be verified to still exist.

## Anti-patterns

- When a narrow profile already supplies the owner, load that owner, not a broad doc pack.
- Report the actual witness, not a generic search recipe.
- Treat one search as one candidate set, never as proof that no other owner or call site exists.
- Edit from the verified source, never from an error message, summary, or stale memory.
- Rank live code and config above routed non-owner documents.
