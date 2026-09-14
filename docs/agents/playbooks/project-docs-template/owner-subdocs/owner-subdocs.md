---
doc_type: playbook
ssot_owner: docs/agents/playbooks/project-docs-template/owner-subdocs/owner-subdocs.md
update_trigger: owner-subdoc creation mechanics or initial scaffold shape changes
---

# Branch-local Owner Subdocs

This child of the project-doc scaffold owner defines shared owner-subdoc creation mechanics. Apply `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md` for materiality, placement, headers, and safe supersession.

Create one branch-local subdoc when a stable truth cluster would blur the root jurisdiction. It owns one responsibility, stays under its existing branch, and gains a direct router route in the same change. Do not create one per prompt, task, commit, or fixed truth category.

| Branch | Stable cluster and exclusion |
|---|---|
| Goal | Durable intent cluster; no per-prompt/task/commit records. |
| Rules | Project-specific rule cluster; reusable governance remains in its governance owner. |
| Architecture | Stable behavior, boundary, workflow, integration, or module-authority cluster; no task logs/history. |
| Data truth | Data/config/constant/default/source-artifact cluster; no fixed truth taxonomy or copied source-owned values. |
| Learning | Recurring operational lesson; no chronology or work-status records. |

### Branch-local owner subdoc example
```md
---
doc_type: reference
ssot_owner: docs/project/<branch>/<owner-subdoc>.md
update_trigger: intent, boundary, invariant, change rule, verification, or references change
---

# <Stable Truth Cluster Name>

## Intent
- <what the user wanted and why this truth exists>

## Boundary
- <what this truth covers>
- <what this truth does not cover, when needed>

## Invariant
- <what future work must preserve>

## Change Rule
- <exact condition under which this truth may change>

## Verification
- <deterministic command or manual witness>

## References
- <related owner docs, when jurisdiction crosses branches>
```
