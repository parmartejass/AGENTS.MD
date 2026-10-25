---
doc_type: policy
ssot_owner: docs/agents/governance/skills/skills.md
update_trigger: skill bundle identity, contents, or platform adapter contracts change
---

# Skills

Jurisdiction: reusable skill bundle identity, packaging, support content, source boundary, and platform adapter records.

## Baseline
```yaml
baseline:
  interface: the Agent Skills open-specification SKILL.md bundle (agentskills.io)
  pattern: "<skill-name>/SKILL.md with specification-conformant frontmatter plus optional scripts/, references/, assets/; one canonical source bundle under this jurisdiction, installed into runtime discovery roots by the consumer"
  reason: "one cross-vendor format read by every major agent runtime; progressive disclosure is a property of the format, not of a wrapper"
  exception: "a runtime-specific sidecar only where a verified runtime contract requires a key the specification does not define, recorded as an adapter record"
```

## Bundle identity
- Canonical bundles MUST live at `docs/agents/governance/skills/<skill-name>/`, exactly one directory below this authority.
- Under this source-asset contract, bundle roots MUST stay flat: nested bundle roots are Prohibited.
- `SKILL.md` identifies a bundle.
- A directory without that file MUST be treated as non-skill content.
- `<skill-name>` MUST equal the frontmatter `name`: 1-64 lowercase alphanumeric characters and single hyphens, no leading or trailing hyphen.
- The filesystem name identifies the runtime path.
- `SKILL.md` supplies human-readable naming.
- A rename MUST migrate affected links and identified downstream installation consumers.

## Minimum bundle contract
- `SKILL.md` MUST expose purpose and activation conditions.
- `SKILL.md` MUST expose task routing and operational instructions, with lifecycle routed to the agent lifecycle owner.
- `SKILL.md` MUST expose required support files and their bundle-relative locations.
- `SKILL.md` MUST expose verified platform constraints and explicit unsupported outcomes when relevant.
- `allowed-tools` is experimental. A destructive or externally visible action MUST have a control beyond `allowed-tools` (FP-30).
- `SKILL.md` MUST expose one deterministic verification path or a pointer to its platform owner.
- `SKILL.md` frontmatter MUST conform to the Agent Skills open specification.
- A runtime-specific key requires an adapter record.
- Bundle verification MUST apply that format and the repository README Checks, the command source the evidence owner names.

## Support content
- Support files MUST be reachable from `SKILL.md` through reference routes.
- Create support files only for a declared bundle need.
- Reusable source assets belong in the bundle.
- Generated outputs, machine-local state, credentials and runtime-only artifacts MUST stay out of the bundle.
- A runtime-specific sidecar MUST have a verified consuming contract and an adapter record.

## Source and runtime boundary
- Edit the canonical bundle only.

## Runtime discovery and context
- Runtime limits and discovery behavior MUST resolve from the target runtime's current authoritative contract.
- This policy declares no fallback context budget and no fixed capability ceiling.
- `description` MUST be 1-1024 characters and MUST state what the skill does and when to use it, leading with the activation condition.
- Conditional operational detail MUST live in referenced support files.
- References add to full reads of governing and touched sources and never replace them (FP-04, FP-05).

## Platform adapters
- An adapter record records format normalization only.
- An adapter record MUST name the consuming platform and its verified runtime contract.
- An adapter record MUST state the required format or location normalization and why it is necessary.
- An adapter record MUST state discovered tool, sandbox, permission, and context constraints for that consumer.
- An adapter record MUST name the installation/update owner and a deterministic verification route.
- An adapter record MUST list affected bundle and documentation routes.
- Current runtime contracts supply changing capability and context limits.
- Platform behavior MUST come from current runtime contracts, not from archived examples or estimates.
- Durable installation evidence goes to its declared project-doc owner.
