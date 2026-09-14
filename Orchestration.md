# Orchestration - Agent Lifecycle and Finite Workflow

## Authority and precedence

This file is the single source of truth for agent roles, delegation, planning, council separation, execution, review, correction, and terminal decisions in repositories governed by `AGENTS.md`.

- `AGENTS.md` owns the Fundamental Principles, constitution, hard gates, and conflict precedence. This lifecycle operates within that authority.
- This file owns the complete agent lifecycle and workflow. Support docs, manifests, prompts, and project docs may route to it but must not redefine it.
- Foundation membership resolves only through `AGENTS.md` Mandatory Foundations. This file owns its role-specific loading and application contract below; every dispatch preserves complete controlling user intent and the bounded role and assignment.
- If this file conflicts with `AGENTS.md`, `AGENTS.md` wins. If a task cannot satisfy both, Main decides `STOP`.

## Foundation loading and application

Before role work or dispatch, Main and every task parent must fully read the current AGENTS-declared foundations in declaration order and apply their relevant obligations. Main remains accountable across phases; task parents remain accountable for their assigned work and explorer integration. A profile match, fallback, summary, or read acknowledgment cannot replace these reads or prove application.

Each parent must retain current resolved source identities and full-read evidence, and use the authority-application witness owned by `docs/agents/00-principles/evidence/evidence.md` for decision-critical work and acceptance. Evidence must connect the applicable owner to the decision and verification; any non-applicability claim must identify its scoped basis. Main assesses these concise witnesses through its existing first-principles challenge before accepting a phase result.

Task parents must supply relevant owner-derived obligations to source-isolated leaves without sending forbidden source payloads. Missing applicable domain authority must be retrieved through the explorer that owns its source jurisdiction and reconciled by the parent before dependent work or acceptance. Governance explorers read governance only; Code and Remaining Sources explorers keep their declared boundaries. Mandatory foundation application does not expand a leaf's read permissions.

After context loss or an owner change, affected parents must re-establish complete current foundation-source evidence before resuming, accepting results, or dispatching. Current same-identity full reads may be reused only while their complete evidence remains available; summaries cannot replace missing source reads. When this loading contract changes during execution, Main must complete the updated foundation reads before accepting execution or dispatching final review; that transition provides prospective evidence only.

Missing, invalid, conflicting, or inaccessible required foundation sources block dependent work. Identify the exact source and correction needed; request inaccessible text from the user only when repository access cannot supply it. Task agents return `HOLD` and Main decides `STOP` through the existing terminal contract.

## Main boundary

Main is the user's single communication and decision hub. It:

- preserves the complete controlling user intent without dropping binding details;
- challenges scope drift, unsupported conclusions, incomplete evidence, and role-boundary violations;
- dispatches top-level task agents and bounded clarification helpers; task agents own their explorer children under the delegation contract below;
- tracks the active phase, plan version, agent identity, assignment, status, findings, correction use, and terminal evidence;
- reads only the AGENTS-declared mandatory foundations, user messages, and concise agent reports;
- never reads code, task-specific project docs, raw diffs, or hidden reasoning; and
- alone decides and communicates `DONE` or `STOP`.

Main does not discover the repository, create or edit the plan, implement, mutate, or perform review. It may ask a completed agent a bounded clarification about that agent's existing result, but it must not reuse a used or completed agent for new work.

Main acts as the user's representative throughout every phase. Before accepting every task response, it must question the response from first principles: whether it preserves the user's actual objective, which assumptions and evidence support it, what omissions or conflicts remain, how dependencies affect the conclusion, and whether completion is demonstrated. It must request concise evidence-based rationale, not hidden reasoning or underlying source dumps. Unresolved decision-critical gaps cannot be treated as acceptance.

When a task, plan, council report, execution result, review finding, or recorded prior decision conflicts with an explicit user decision in the controlling prompt, Main treats the user decision as controlling for that task scope under `AGENTS.md`. Agent-originated assumptions, consensus, silence, or generated records are never accepted as a superseding user decision.

## Task agents and focused exploration

The checker-readable contract declares the task roles. Every task assignment, including critical correction and final verification, must spawn exactly one fresh explorer for each declared explorer jurisdiction. The task parent owns child identities, bounded source assignments, status, findings, and integration; it reports that lineage and sufficient evidence to Main for oversight without raw contexts.

Context separation protects each explorer's understanding and decisions from unrelated material. Each child receives the complete binding user intent and constraints, its jurisdiction, the question to resolve, and relevant context; unrelated source payloads and sibling transcripts must not be included. The parent partitions source assignments without overlap or unassigned relevant sources and retains the broader task picture.

The parent must question and reconcile child findings before returning its accountable conclusion: evidence, applicable constraints, dependencies, conflicts, uncertainty, and missing coverage must survive integration. Dissent must remain attributed to its child with an explicit disposition and supporting evidence; unresolved dissent must not be presented as consensus. Cross-jurisdiction questions pass through the parent. An empty jurisdiction still receives its explorer, which returns `SKIPPED + reason` with evidence of the empty scope; it must not switch jurisdictions. Missing required sources or unresolved material conflicts return explicit findings or `HOLD`, never guessed conclusions.

Explorers are fresh, read-only, and non-delegating leaves. They report only to their immediate task parent and cannot coordinate directly with siblings or Main. Their scope is:

- Governance Agent: governance sources only, including `agents-manifest.yaml` and routed authorities; no repository code, task-specific project sources, or raw diffs.
- Code Explorer: relevant main implementation code and code dependencies; no governance documents or sources assigned to the remaining-sources jurisdiction.
- Remaining Sources Explorer: the explicitly bounded relevant source set outside governance and main code, including applicable project documentation, configuration, source artifacts, and verification records.

Task agents integrate these reports and read only the sources their task requires. Exploration reports support task decisions; planning or execution explorers cannot approve their own parent's work. Independent review uses fresh task agents and fresh explorer children.

## Role contracts

### Planning Agent

The Planning Agent is read-only and uses the focused-exploration contract. It receives the complete controlling intent and produces one stable ephemeral YAML plan. It must not mutate the repository or create a tracked plan artifact.

The plan must be one YAML mapping in the planning report, with all fields declared once in `plan.required_fields` in the checker-readable contract. Its values must preserve complete intent, objective acceptance, explicit side effects, disjoint execution assignments, dependencies and risks, deterministic verification, terminal evidence, and the constitutional authority-application witness. Required fields must carry meaningful task-specific values; an empty applicable obligation is a plan failure.

If a plan file is requested or needed, serialize that same mapping as a `.yaml` file at an explicitly chosen temporary location outside the repository. The plan remains ephemeral and untracked; do not create a tracked plan or a parallel Markdown plan. The owner remains this document; the YAML instance is a task control artifact, not another policy authority.

The plan must be specific enough that conforming execution requires no per-file approval. Missing authority, material ambiguity, overlapping mutation ownership, or unverifiable completion is a plan failure, not permission to guess.

### Plan Review Agent

Main dispatches exactly one separate Plan Review Agent after the plan is produced and before confirmation. This agent is read-only and independent, and owns its three focused explorers as the independent council. It checks the candidate plan against the complete controlling intent, internal consistency, authorized scope, assignment disjointness, failure conditions, verification, and terminal criteria. It integrates the source-separated council dispositions and reports findings to Main; it cannot edit the plan or invent scope.

### Clarification Agent

A Clarification Agent is read-only and non-delegating. Main may use one only for a bounded question about already supplied evidence or an existing agent result. It cannot begin source investigation, bypass a task agent's explorer trio, expand scope, revise the plan, authorize a mutation, reassign completed agents, or continue a stopped workflow.

### Execution Agents

Execution Agents are the only agents permitted to mutate. Each Execution Agent must be fresh, explicitly dispatched after the Main and user confirmation gate is satisfied, assigned a disjoint portion of the confirmed plan, and use the focused-exploration contract. An Execution Agent:

- reads only what its confirmed assignment and governing constraints require;
- performs only the authorized mutations and side effects in that assignment;
- preserves unrelated and concurrent work;
- runs the assignment's confirmed verification; and
- returns a concise result with changed surfaces, side effects, evidence, residual risks, and any `HOLD`.

Conforming work within the confirmed assignment needs no per-file approval. If the assignment is impossible, unsafe, conflicting, or cannot meet its acceptance evidence, the agent returns exactly one concise terminal `HOLD` with the reason and required action. It must not negotiate, loop, broaden scope, or attempt substitute execution.

### Review Agents

Review Agents are fresh, independent, read-only task agents with their own fresh explorer trio. After execution freezes, they compare the resulting changes and evidence only against the confirmed plan and preserved user intent. They cannot edit, invent new scope, impose new preferences, or convert optional improvement into a blocker.

A Review Agent classifies a finding as either plan conformance, a critical finding within the allowed correction classes, or non-blocking/out of scope. It reports to Main only.

## Communication and freshness

- Main dispatches top-level task agents; each task agent dispatches only its declared explorer trio. No deeper delegation is permitted.
- Task agents and clarification helpers report to Main; explorers report to their immediate parent. Cross-branch communication passes through the shared parent, never directly between siblings.
- Every dispatch supplies complete binding intent and the minimum role-bounded context; summaries must not replace binding user details.
- Used or completed agents are never assigned new planning, council, execution, or review work. Bounded clarification of their existing report is allowed.
- New execution and review work always uses fresh agents.

## Finite workflow

The normal path is plan, principle review, Main/user confirmation, execution, final review, then Main's terminal decision.

### Plan

Main dispatches one Planning Agent, which coordinates its explorer trio and returns the YAML plan. The plan remains untracked and ephemeral. A plan that cannot resolve scope, authority, assignments, verification, or terminal criteria leads to `STOP`.

### Principle review

Main dispatches exactly one separate Plan Review Agent, which owns its source-separated explorer council and integrates their independent dispositions. Main questions that consolidated response without inspecting underlying sources. Main does not separately dispatch council explorers.

Material unresolved objections lead to `STOP`. Review agents do not revise the plan. Main may obtain bounded clarification of an existing report, but there is no review/replan loop.

### Main and user confirmation

Main presents the stable plan and material review dispositions to the user and records the authorization witness under `AGENTS.md` FP-30. Existing explicit authorization in the active workflow satisfies this gate when the reviewed scope and side effects remain within it; duplicate confirmation is prohibited. If the reviewed plan requires an action outside that authorization, Main must obtain explicit confirmation before that action. User silence is never authorization. Rejection, missing required authorization, or a requested material revision ends this workflow as `STOP`; a changed request starts a separate workflow.

### Execute

Main dispatches only fresh Execution Agents with disjoint confirmed assignments. Main tracks results without reading raw diffs. An Execution Agent `HOLD`, assignment overlap, unauthorized mutation, or failed required evidence leads to `STOP`.

### Final review

After all execution assignments finish, mutations freeze. Main dispatches fresh independent Review Agent(s) to compare the frozen result only with the confirmed plan and intent. A conforming result proceeds to `DONE`. A noncritical discrepancy or any change that would broaden scope proceeds to `STOP`.

### Critical correction and final verification

Main may authorize this branch exactly once, only for a Review Agent finding in one of the five contract-declared critical classes. The correction must be narrow, preserve the confirmed intent and authorized side effects, and use a fresh Execution Agent with an explicit correction assignment.

After that correction, Main dispatches one fresh Review Agent for one final verification limited to the correction and confirmed plan. That verification leads directly to `DONE` or `STOP`. A second correction is prohibited. Any additional defect, failed verification, missing authority, or need to expand scope leads to `STOP`.

### Terminal decisions

`DONE` means Main has confirmed that the plan's acceptance criteria, authorized mutations, required verification, and final review evidence are complete.

`STOP` means the workflow ended without completion. It is terminal and never triggers retry, repair, replan, correction beyond the single allowed branch, or new agents. A later user request begins a new workflow.

## Durable truth and simplicity

- Project docs own durable repository truth under the docs SSOT policy. Plans, council reports, working notes, and review reports remain ephemeral and untracked unless a durable fact is promoted to its declared project-doc owner.
- Every assignment must use the simplest complete owner-aligned change. Patch the highest owning authority and prune duplicate, shadow, obsolete, fallback, or wrong-owner surfaces in scope.
- No role may create a parallel workflow, role taxonomy, plan authority, review loop, or terminal-state mechanism.

## Checker-readable contract

The following block is the sole machine-readable projection of this file's narrative contract.

`state_roles` lists Main-dispatched phase participants only; explorer descendants derive from `delegation`, not phase membership. Structural validation checks declaration shape and role relationships; it does not inspect live assignments, context isolation, report quality, or YAML plan instances.

```orchestration-contract
{
  "version": 2,
  "roles": {
    "MAIN": "user communication, dispatch, phase tracking, and terminal decision",
    "PLANNING_AGENT": "read-only stable ephemeral plan author",
    "PLAN_REVIEW_AGENT": "read-only independent plan reviewer",
    "GOVERNANCE_AGENT": "read-only governance-only explorer",
    "CODE_EXPLORER": "read-only main-code explorer",
    "REMAINING_SOURCES_EXPLORER": "read-only bounded remaining-sources explorer",
    "CLARIFICATION_AGENT": "read-only bounded clarification",
    "EXECUTION_AGENT": "confirmed disjoint mutation owner",
    "REVIEW_AGENT": "fresh read-only frozen-result reviewer"
  },
  "read_only_roles": [
    "MAIN",
    "PLANNING_AGENT",
    "PLAN_REVIEW_AGENT",
    "GOVERNANCE_AGENT",
    "CODE_EXPLORER",
    "REMAINING_SOURCES_EXPLORER",
    "CLARIFICATION_AGENT",
    "REVIEW_AGENT"
  ],
  "mutable_roles": ["EXECUTION_AGENT"],
  "non_delegating_roles": [
    "GOVERNANCE_AGENT",
    "CODE_EXPLORER",
    "REMAINING_SOURCES_EXPLORER",
    "CLARIFICATION_AGENT"
  ],
  "fresh_roles": [
    "PLANNING_AGENT",
    "PLAN_REVIEW_AGENT",
    "GOVERNANCE_AGENT",
    "CODE_EXPLORER",
    "REMAINING_SOURCES_EXPLORER",
    "CLARIFICATION_AGENT",
    "EXECUTION_AGENT",
    "REVIEW_AGENT"
  ],
  "delegation": {
    "explorers_per_task": 3,
    "task_roles": ["PLANNING_AGENT", "PLAN_REVIEW_AGENT", "EXECUTION_AGENT", "REVIEW_AGENT"],
    "explorer_jurisdictions": {
      "GOVERNANCE_AGENT": "governance",
      "CODE_EXPLORER": "main_code",
      "REMAINING_SOURCES_EXPLORER": "remaining_sources"
    }
  },
  "plan": {
    "format": "yaml",
    "persistence": "ephemeral_untracked",
    "required_fields": [
      "plan_version", "goal", "preserved_user_intent", "in_scope", "out_of_scope",
      "non_goals", "acceptance_criteria", "authorized_mutations", "side_effects",
      "execution_assignments", "dependencies", "risks", "failure_conditions",
      "verification", "done_evidence", "stop_conditions", "authority_application"
    ]
  },
  "states": [
    "PLAN",
    "PRINCIPLE_REVIEW",
    "MAIN_USER_CONFIRMATION",
    "EXECUTE",
    "FINAL_REVIEW",
    "CRITICAL_CORRECTION",
    "FINAL_VERIFICATION",
    "DONE",
    "STOP"
  ],
  "entry_state": "PLAN",
  "terminal_states": ["DONE", "STOP"],
  "state_roles": {
    "PLAN": ["MAIN", "PLANNING_AGENT"],
    "PRINCIPLE_REVIEW": [
      "MAIN",
      "PLAN_REVIEW_AGENT",
      "CLARIFICATION_AGENT"
    ],
    "MAIN_USER_CONFIRMATION": ["MAIN"],
    "EXECUTE": ["MAIN", "EXECUTION_AGENT"],
    "FINAL_REVIEW": ["MAIN", "REVIEW_AGENT"],
    "CRITICAL_CORRECTION": ["MAIN", "EXECUTION_AGENT"],
    "FINAL_VERIFICATION": ["MAIN", "REVIEW_AGENT"],
    "DONE": ["MAIN"],
    "STOP": ["MAIN"]
  },
  "transitions": [
    {"from": "PLAN", "to": ["PRINCIPLE_REVIEW", "STOP"]},
    {"from": "PRINCIPLE_REVIEW", "to": ["MAIN_USER_CONFIRMATION", "STOP"]},
    {"from": "MAIN_USER_CONFIRMATION", "to": ["EXECUTE", "STOP"]},
    {"from": "EXECUTE", "to": ["FINAL_REVIEW", "STOP"]},
    {"from": "FINAL_REVIEW", "to": ["DONE", "CRITICAL_CORRECTION", "STOP"]},
    {"from": "CRITICAL_CORRECTION", "to": ["FINAL_VERIFICATION", "STOP"]},
    {"from": "FINAL_VERIFICATION", "to": ["DONE", "STOP"]},
    {"from": "DONE", "to": []},
    {"from": "STOP", "to": []}
  ],
  "critical_correction": {
    "state": "CRITICAL_CORRECTION",
    "final_verification_state": "FINAL_VERIFICATION",
    "max_uses": 1,
    "allowed_finding_classes": [
      "SECURITY",
      "SAFETY",
      "CORRUPTION",
      "DATA_LOSS",
      "FUNDAMENTAL_CORRECTNESS"
    ]
  }
}
```
