---
doc_type: policy
ssot_owner: docs/agents/skills/00-skill-standards/skill-standards.md
update_trigger: skill bundle identity, contents, or platform-format requirements change
---

# Skill Standards (SSOT)

`AGENTS.md` owns the Fundamental Principles and instruction derivation; `Orchestration.md` owns the agent lifecycle. This file owns reusable skill bundle identity, naming, and packaging. Platform normalization routes through `docs/agents/skills/10-platform-adapters/platform-adapters.md`.

## Bundle identity
- Canonical installable bundles live at `docs/agents/skills/<skill-name>/`, exactly one directory below the skill authority; nested bundle roots are unsupported by this source-asset contract.
- `SKILL.md` identifies a bundle. Tooling MUST treat a directory without it as non-skill content.
- `<skill-name>` MUST be a stable lowercase kebab-case identifier. The filesystem name identifies the runtime path; the title in `SKILL.md` supplies human-readable naming.
- A rename MUST migrate affected links and identified downstream installation consumers under `AGENTS.md` FP-16 and FP-31.

## Minimum bundle contract
`SKILL.md` MUST expose:
- purpose and activation conditions;
- task-specific routing and operational instructions, with agent lifecycle routed to `Orchestration.md`;
- required support files and their bundle-relative locations;
- verified platform constraints and explicit unsupported outcomes when relevant;
- one deterministic verification path or a pointer to its platform owner.

The target runtime owns frontmatter and metadata format. Bundle verification MUST apply that format and the relevant `README.md` checks; structural checks do not establish semantic compliance under `AGENTS.md` FP-32 and FP-33.

## Support content
- Bundle support files MUST be reachable from `SKILL.md` through relevant reference routes. Create them only for a declared bundle need under `AGENTS.md` FP-09 and FP-34.
- Reusable source assets belong in the bundle; generated outputs, machine-local state, credentials, and runtime-only artifacts do not.
- Runtime-specific sidecars require a verified consuming contract and an adapter record naming the consumer, purpose, and verification route.

## Source and runtime boundary
- Edit the canonical bundle. Installation and installed state belong to the consuming project or user; this repository tracks no parallel runtime copies or projection mappings.
- Instruction content MUST route constitutional obligations to `AGENTS.md` and lifecycle mechanics to `Orchestration.md`, without copying either authority.
- A change to bundle identity or platform behavior MUST update affected routes in this owner, the platform adapter reference, `docs/agents/agents_index.md`, and `README.md` together.
- Docs-header carveouts are owned by `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.

## Runtime discovery and context
Runtime limits and skill discovery behavior MUST resolve from the target runtime's current authoritative contract under `AGENTS.md` FP-18 and FP-27. This source-bundle policy defines no fallback context budget or fixed capability ceiling. Descriptions MUST lead with the activation condition; conditional operational detail belongs in referenced support files. References do not replace full reads of governing and touched sources under FP-05.

## Owner routes
- Fundamental obligations: `AGENTS.md`.
- Agent lifecycle: `Orchestration.md`.
- Copy/paste scaffolds: `docs/agents/playbooks/playbooks_index.md`.
- Skill documentation and bundles: `docs/agents/skills/skills_index.md`.
