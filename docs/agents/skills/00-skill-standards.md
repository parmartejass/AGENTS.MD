---
doc_type: policy
ssot_owner: docs/agents/skills/00-skill-standards.md
update_trigger: skill standards change OR new platform support requirements emerge
---

# Skill Standards (SSOT)

## Purpose
- A skill is a reusable operational bundle that adapts governance guidance to a tool environment.
- `docs/agents/skills/` is the authority for repo-owned skills, including both governance docs and installable skill bundles.
- This file owns the cross-platform skill contract: bundle identity, naming, minimum contents, safety expectations, runtime-projection model, and coordination rules.
- Keep platform-specific installation paths, runtime quirks, and capability differences in `docs/agents/skills/10-platform-adapters.md`.

## Bundle identity
- Governance skill docs live directly under `docs/agents/skills/*.md`.
- Installable skill bundles live exactly one directory below that authority at `docs/agents/skills/<skill-name>/`; nested bundle roots are not supported.
- `SKILL.md` is the identity file for a skill bundle.
- A directory without `SKILL.md` is not a skill bundle and must be treated as non-skill content by tooling.

## Bundle naming
- `<skill-name>` should be a stable, lowercase, kebab-case identifier.
- Use the filesystem name as the runtime path identifier; use the title inside `SKILL.md` for human-readable naming.
- Renames are breaking for docs links, grepability, and runtime projection paths, so coordinate them across the docs index, adapter docs, and linker when they are necessary.

## Minimum Bundle Contract
- Every bundle must contain `SKILL.md`.
- `SKILL.md` must make these discoverable:
  - what the skill is for and when to use it
  - the workflow, routing logic, or decision path the agent should follow
  - any required support files and where they live inside the bundle
  - compatibility or platform constraints when relevant
  - one deterministic verification path, or an explicit pointer to the platform-owned verification path
  - explicit unsupported/failure notes when omission would mislead the user
- Exact frontmatter or metadata keys are owned by the target runtime format, not by this doc.

## Support Files
- Allowed support content includes `references/`, `assets/`, `scripts/`, and `templates/` when the bundle needs them.
- Support files must be referenced from `SKILL.md`; unreferenced bundle clutter is not allowed.
- Support files must remain reusable, non-secret repo assets. Do not store generated outputs, machine-local state, or runtime-only artifacts in a skill bundle.
- Runtime-specific sidecars are exceptions. Add them only when a verified runtime contract requires them, and document the consumer and coordination points in `docs/agents/skills/10-platform-adapters.md`.

## Invariants
- One canonical repo copy: `docs/agents/skills/<skill-name>/` is the source of truth for that skill.
- No policy duplication: skills reference `AGENTS.md` and core docs instead of restating hard gates or copying platform policy into each bundle.
- Non-secret only: do not store credentials, bearer tokens, cookies, machine identities, or other sensitive local values in any skill file.
- Deterministic guidance: workflow instructions and verification notes should be reproducible from repo state and declared external authorities.
- Explicit exceptions only: any runtime-specific sidecar or non-standard bundle file must name the consuming platform and why it exists.

## Runtime Projections
- Repo-owned skill bundles may be projected into supported runtime locations by `docs/agents/link_repo_assets.ps1`.
- Exact runtime mappings, support levels, and scope rules live in `docs/agents/platforms/runtime-projections.json`.
- Official project-local skill surfaces are platform-specific and do not all use the same runtime folder layout.
- Compatibility mappings may exist, but they must stay explicitly labeled and disabled by default unless the setup flow is told to include them.
- Runtime locations are derived views of the canonical repo bundle, not independent authorities.

## Operating Rules
- Edit the canonical repo bundle first. Regenerate runtime projections through `docs/agents/link_repo_assets.ps1` or `docs/agents/skills/link_skills.ps1` instead of editing projected runtime paths directly.
- If a skill change affects runtime projection behavior, bundle identity, or supported platform behavior, update this file, `docs/agents/skills/10-platform-adapters.md`, `docs/agents/platforms/runtime-projections.json`, `docs/agents/index.md`, and `docs/agents/link_repo_assets.ps1` together.
- Keep docs-header carveout details in `docs/agents/25-docs-ssot-policy.md`.
- Keep linker implementation details in `docs/agents/link_repo_assets.ps1`.

## Verification Expectations
- Every skill should include one deterministic smoke check or an explicit pointer to the platform-owned verification path.
- When a platform or API limitation materially changes behavior, the skill should call that out explicitly rather than implying unsupported behavior works.
- Bundle changes should be verified with the repo checks listed in `README.md` and any targeted skill-linking smoke check required by the change.

## Codification Targets
- Cross-platform principles -> `docs/agents/*.md`
- Copy/paste templates -> `docs/agents/playbooks/*.md`
- Skill governance docs -> `docs/agents/skills/*.md`
- Installable skill bundles -> `docs/agents/skills/<skill-name>/`
