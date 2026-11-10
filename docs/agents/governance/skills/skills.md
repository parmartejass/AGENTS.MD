---
doc_type: policy
ssot_owner: docs/agents/governance/skills/skills.md
update_trigger: skill bundle standard or platform adapter contracts change
---

# Skills

Jurisdiction: reusable skill bundle identity, format, and platform adapter records.

## Baseline
```yaml
baseline:
  interface: the Agent Skills open-specification SKILL.md bundle (agentskills.io)
  pattern: "<skill-name>/SKILL.md with specification-conformant frontmatter plus optional scripts/, references/, assets/; one canonical source bundle under this jurisdiction, installed into runtime discovery roots by the consumer"
  reason: "one cross-vendor format read by every major agent runtime; progressive disclosure is a property of the format, not of a wrapper"
  exception: "a runtime-specific sidecar only where a verified runtime contract requires a key the specification does not define, recorded as an adapter record"
```

## Bundles
- Canonical bundles MUST live at `docs/agents/governance/skills/<skill-name>/`.
- `SKILL.md` identifies a bundle; a directory without it is not a skill.
- `SKILL.md` frontmatter MUST conform to the Agent Skills open specification.
- `allowed-tools` is experimental and MUST NOT be the only control on a destructive or externally visible action.

## Platform adapters
- An adapter record records format normalization only.
- An adapter record MUST name the platform, its verified contract, and the normalization it requires.
