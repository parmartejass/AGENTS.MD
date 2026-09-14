---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: constitutional application mechanics or their delegated owner routes change
---

# 00 - Principles (First Principles)

`AGENTS.md` owns the Fundamental Principles and their binding force. This delegated application owner defines modeling, scope, authority-first correction, control-artifact selection, and design mechanics under those principles. Apply it before non-trivial work; it creates no second principles set or agent lifecycle.

## First-Principles Protocol (Hard Gate)

Before implementing, explicitly define:
- **Model and scope**: record the FP-04 and FP-07 inputs, boundaries, owners, consumers, and completion evidence.
- **SSOT map**: record each decision-critical fact, state, side effect, and witness against its FP-12 owner and public contract.
- **Root-cause uplift** (authority-first): for any defect or error, trace from symptom to the earliest defective authority/contract/boundary; fix there by adding or strengthening invariants/validation so the class of errors becomes structurally impossible; one authority fix prevents N errors. If a symptom-level patch is unavoidable, record why upstream prevention is infeasible and what error class remains unprevented.
- **Structural consolidation** (authority-first): when multiple findings map to the same invariant/authority, treat them as one defect; consolidate the fix in that authority owner.
- **Derived task authority** (authority-first): for any non-trivial output, first identify or create the minimum task-specific control artifact required to make the output trustworthy (for example an authority map, source map, extraction ledger, validation matrix, patch plan, or test fixture). The final output must be generated from and verified against that control artifact; do not treat the final output itself as the authority.
- **Patch, do not fork authority**: when improving governance, docs structure, frameworks, prompts, or reusable procedures, update the current highest owning authority through an explicit patch/supersession path. Do not create disconnected framework versions, parallel docs, or replacement structures unless the user explicitly authorizes a new authority and the old authority is deprecated or superseded.
- **Proof obligations**: preconditions/postconditions + failure modes to cover.
- **Verification**: exact commands or deterministic manual checks (include at least one failure-path check when feasible).
- **Resource bounds**: timeouts, cancellation, and guaranteed cleanup in `finally` for external resources.
- **Performance constraints**: expected data sizes and speed targets; choose algorithm/I/O strategy accordingly, without weakening correctness or safety.
- **Design principles (generation + maintenance)**: apply DRY, KISS, YAGNI, Separation of Concerns, and Law of Demeter alongside SOLID/DI; select the simplest complete design preserving explicit contracts and authority boundaries under FP-34.
- **Defect vocabulary**: use the exact terms owned by `docs/agents/00-principles/diagnosis/diagnosis.md`.
- **Shift-left quality** (mandatory for behavior changes/new features): convert reactive RCA learnings into proactive prevention via tests, design failure analysis, boundary contracts, static checks, and observability.

Supporting references:
- First principles patterns: `docs/agents/00-principles/principles.md`
- Concept -> owner map: `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`

## Application routes
- Outcome, scope, model, and control-artifact evidence: `AGENTS.md` Fundamental Principles and First-Principles Protocol.
- Defect localization and disconfirming experiments: `docs/agents/00-principles/diagnosis/diagnosis.md`; examples in `docs/agents/playbooks/rca-methods-template/rca-methods-template.md`.
- Owner selection: `docs/agents/20-sources-of-truth-map/sources-of-truth-map.md`.
- Full reads and bounded discovery: `docs/agents/05-context-retrieval/context-retrieval.md`.
- Coding contracts and deletion/reroute witnesses: `docs/agents/35-coding-principles/coding-principles.md`.
- Verification floors and invariant evidence: `docs/agents/00-principles/evidence/evidence.md`; repeatable commands: repo-root `README.md` Checks.
- Council, execution, independent review, and terminal decisions: `Orchestration.md`.
- Document placement: `docs/agents/25-docs-ssot-policy/docs-ssot-policy.md`.
- I/O commit and recovery: `docs/agents/70-io-data-integrity/io-data-integrity.md` File handling rules.
- External Excel ownership and cleanup: `docs/agents/50-excel-com-lifecycle/excel-com-lifecycle.md`.

## Non-normative examples
The following worked examples illustrate the named owner contracts; they add no lifecycle or mandatory artifact beyond the task-specific acceptance criteria.

| Application | Concrete evidence example | Governing section |
|---|---|---|
| Model and proof | For an invoice export, identify source records and authorized destination; precondition: validated required fields; postcondition: exported keys reconcile with eligible keys; failure case: missing required field produces the declared failure without publishing output. | `AGENTS.md` First-Principles Protocol and Invariants + Witnesses |
| Authority uplift | Two callers disagree on an eligibility rule. Locate its declared validator, correct that owner, reroute callers, and compare a frozen qualifying/nonqualifying fixture. | `AGENTS.md` First-Principles Protocol: Root-cause uplift and Structural consolidation; coding-principles SSOT Jurisdiction Mechanics |
| Resource and write safety | A locked destination leaves the original intact; record validation, attempted promotion, failure, and cleanup. An external-resource case also records the owned handle/PID and cleanup result. | `AGENTS.md` Implementation Write State Machine + Two-Phase Commit and Resource Safety; I/O and COM owners in Application routes |
| Performance | A bounded export records row count, I/O round trips, peak batch size, elapsed time, and output equivalence before claiming an improvement. | `AGENTS.md` Performance & Speed |
| Auditability | Distinguish observed output (R), intended invariant (S), and recorded test/report (D); mark an unmeasured outcome Unknown and name its missing witness. | `AGENTS.md` First-Principles + SSOT + Evidence Model and Authority-Constrained Reasoning |

Practical placement resolves through docs-policy Bounded Project Authority Memory and Operational asset carveouts: a playbook can carry the task scaffold, a reusable skill can carry its operator example, and a project owner records only the durable fact. Review objections and terminal decisions remain owned by `Orchestration.md` Principle review and Terminal decisions.
