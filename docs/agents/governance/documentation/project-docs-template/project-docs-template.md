---
doc_type: policy
ssot_owner: docs/agents/governance/documentation/project-docs-template/project-docs-template.md
update_trigger: project-doc scaffold shape or subdoc scaffold fields change
---

# Project Docs Scaffold

Jurisdiction: initial shape of project-doc root docs, branch routers, and branch-local owner subdocs.

## Root-doc shape
- Each root doc MUST carry the documentation header and a `## Boundary` stating what the branch owns and excludes; the table below declares each branch's stable cluster, exclusion, and subdoc trigger, so root docs do not restate them.
- Generated text MUST be adapted to verified owners; placeholders MUST NOT ship as truth.
- Verification sections MUST cite the README Checks command or deterministic manual steps.

| Branch | Root sections after Boundary | Stable cluster and exclusion |
|---|---|---|
| Goal | Objective, Acceptance criteria, Durable intent, Non-goals, Verification | Durable intent cluster; no per-prompt/task/commit records. |
| Rules | Do, Don't | Project-specific rule cluster; reusable governance stays with its governance owner. |
| Architecture | Entrypoints, SSOT pointers (concept -> owner), Authority graph (owner -> dependents), Current Summary | Stable behavior, boundary, workflow, integration, or module-authority cluster; no task logs or history. |
| Data truth | Purpose, Current Summary, Change Rule, Verification | Data/config/constant/default/source-artifact cluster; no truth taxonomy, no copied source-owned values. |
| Changelog | Invariant, Field Contract (routes to the release owner), Entries | Closure records in the release field order; no owner truth. |
| Learning | Common pitfalls, Verification tips | Recurring operational lesson; no chronology or work-status records. |

## Branch-local subdoc rule
- Create one subdoc per stable truth cluster that would blur the root jurisdiction; Prohibited: one subdoc per prompt, task, commit, or fixed truth category.
- Each subdoc MUST own one responsibility, stay under its existing branch, and land with its branch router route in the same change; orphan subdocs are Prohibited.

## Template - branch router
```md
# <Branch> Branch Index

- [<leaf>.md](<leaf>.md) - <what it owns>. Required when: <retrieval trigger>.
```

The project router `docs/project/project_index.md` uses the same shape with one route per branch router (`<branch>/<branch>_index.md`).

## Template - branch-local owner subdoc
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
- <what this truth covers and excludes>

## Invariant
- <what future work must preserve>

## Change Rule
- <exact condition under which this truth may change>

## Verification
- <deterministic command or manual witness>

## References
- <related owner docs when jurisdiction crosses branches>
```

## Final linkage verification
- Verify placement, linkage, headers, routers, and owner maintenance through the [Documentation owner](../documentation.md).
