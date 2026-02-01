---
name: Authority-bounded modules policy
overview: Codify the “Authority-Bounded Modules with Explicit Contracts” concept into this governance pack by adding a new supporting policy doc, linking it from the docs index, extending the SSOT map, and adding a minimal hard-gate reference in `AGENTS.md`—without adding any new `agents-manifest.yaml` profile.
todos:
  - id: add-policy-doc
    content: Create `docs/agents/35-authority-bounded-modules.md` with required header and repo-agnostic rules + witnesses.
    status: pending
  - id: update-agents-md
    content: Add minimal Authority Graph hard-gate bullets in `AGENTS.md` referencing authority-bounded modules + explicit contracts (pointing to the new doc).
    status: pending
  - id: update-ssot-map-index
    content: Update `docs/agents/20-sources-of-truth-map.md` (schema/types + module boundaries/contracts) and link new doc from `docs/agents/index.md`.
    status: pending
  - id: verify-checks
    content: Run README “Checks” scripts for docs SSOT + manifest integrity; fix any failures.
    status: pending
  - id: post-change-review
    content: Run a brief post-change council scan for duplicates/edge-cases/perf-risk wording.
    status: pending
isProject: false
---

# Authority-Bounded Modules with Explicit Contracts

## Goal / acceptance criteria

- Add a new governance policy doc that explains how to structure code into **authority-bounded modules** with an **explicit public contract** (preconditions/postconditions/failure modes + witnesses), while staying consistent with `AGENTS.md` SSOT/no-duplicates rules.
- Update `AGENTS.md` to encode a **minimal hard-gate** reference tying module boundaries/contracts to the existing “Authority Graph” hard gate.
- Extend the conceptual SSOT map to include **schema/types** ownership and **module boundaries/contracts** ownership.
- Ensure the new doc is **not orphaned** (linked from `docs/agents/index.md`).
- **Do not** add a new `agents-manifest.yaml` profile (per your choice).

## SSOT owners + fix placement

- Canonical policy stays in `[AGENTS.md](AGENTS.md)`.
- Detailed operational guidance lives in a single new supporting doc under `[docs/agents/](docs/agents/)`.
- Concept→owner mapping remains centralized in `[docs/agents/20-sources-of-truth-map.md](docs/agents/20-sources-of-truth-map.md)`.

## Implementation outline (minimal diffs)

- **Create** `[docs/agents/35-authority-bounded-modules.md](docs/agents/35-authority-bounded-modules.md)` (doc header required per `docs/agents/25-docs-ssot-policy.md`).
  - Define the unified concept (BMEPA + domain-bounded authority) in repo-agnostic terms.
  - Specify core rules:
    - Module == authority boundary (one owner per decision-critical responsibility).
    - Single explicit public contract per module; no cross-boundary “deep imports”.
    - Dependency direction guidance (keep config/constants dependency-light; avoid cycles).
    - UI/presentation is a consumer, not an authority for business rules/constants/config.
    - Contracts must have witnesses (tests/type checks/runtime validation/logged outcomes) and must not hide I/O.
  - Include “reject patterns” to prevent over-abstraction and duplicate authorities.
  - Reference existing SSOT docs instead of duplicating their content (e.g., `docs/agents/20-sources-of-truth-map.md`, `docs/agents/10-repo-discovery.md`, `docs/agents/40-config-constants.md`).
- **Update** `[AGENTS.md](AGENTS.md)` in the hard-gated section `### Authority Graph (Required for non-trivial systems)` to add 1–3 bullets:
  - Require that when code is split into modules/packages, **module boundaries align with authority boundaries** and access occurs via an **explicit public contract** (and point to the new doc for details).
- **Update** `[docs/agents/20-sources-of-truth-map.md](docs/agents/20-sources-of-truth-map.md)`:
  - Add a **Schema / types / data model** category (single owner; used across modules).
  - Add a **Module boundaries + contracts** category, pointing to the new policy doc and (in target repos) to `docs/project/architecture.md` as the place to record the authority graph/boundaries.
- **Update** `[docs/agents/index.md](docs/agents/index.md)`:
  - Add the new doc to the “Core docs” list so it’s discoverable and not orphaned.

## Verification (repo SSOT: README “Checks”)

Run these deterministic checks from `[README.md](README.md)`:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_docs_ssot.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1`

## Post-change council review (hard gate)

After edits, run a brief independent scan to confirm:

- No duplicated SSOT owners were introduced.
- The new rules don’t accidentally re-encode existing policies or encourage over-abstraction.
- Docs header + index linkage requirements are satisfied.

