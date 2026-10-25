# Orchestration - Agent Lifecycle and Finite Workflow

## Authority and precedence

This file owns the agent lifecycle that `AGENTS.md` assigns to it: agent roles, delegation, planning, council separation, execution, review, correction and terminal decisions in repositories governed by `AGENTS.md`. It also owns the role-specific foundation loading and application contract below. Every dispatch MUST preserve the complete controlling user intent and the bounded role and assignment. If a task cannot satisfy both, Main decides `STOP`.

## Foundation loading and application

Before role work or dispatch, Main and every task parent must fully read the current AGENTS-declared foundations in declaration order and apply their relevant obligations. Main MUST remain accountable across phases, and each task parent MUST remain accountable for its assigned work and explorer integration. A profile match, fallback, summary, or read acknowledgment cannot replace these reads or prove application.

Each parent must retain current resolved source identities and full-read evidence, and use the authority-application witness owned by `docs/agents/governance/evidence/evidence.md` for decision-critical work and acceptance. Evidence MUST connect the applicable owner to the decision and its verification. Each non-applicability claim MUST name its scoped basis. Main assesses these concise witnesses through its existing first-principles challenge before accepting a phase result.

Task parents MUST give source-isolated leaves the relevant owner-derived obligations and keep forbidden source payloads out of them. Missing applicable domain authority must be retrieved through the explorer that owns its source jurisdiction and reconciled by the parent before dependent work or acceptance. Governance explorers MUST read only governance, and Code and Remaining Sources explorers MUST keep their declared boundaries. Mandatory foundation application does not expand a leaf's read permissions.

After context loss or an owner change, affected parents must re-establish complete current foundation-source evidence before resuming, accepting results, or dispatching. A current same-identity full read may be reused only while its complete evidence stays available. Summaries cannot replace missing source reads. When this loading contract changes during execution, Main MUST complete the updated foundation reads before it accepts execution or dispatches final review. That transition provides prospective evidence only.

Missing, invalid, conflicting, or inaccessible required foundation sources block dependent work. Identify the exact source and the correction it needs. Ask the user for inaccessible text only when repository access cannot supply it. Task agents return `HOLD` and Main decides `STOP` through the existing terminal contract.

## Main boundary

Main MUST:

- keep every binding detail of the complete controlling user intent;
- challenge scope drift, unsupported conclusions, incomplete evidence and role-boundary violations;
- dispatch top-level task agents and bounded clarification helpers, while task agents own their explorer children under the delegation contract below;
- track the active phase, plan version, agent identity, assignment, status, findings, correction use and terminal evidence;
- read only the AGENTS-declared mandatory foundations, user messages and concise agent reports, never code, task-specific project docs, raw diffs or hidden reasoning; and
- alone decide and communicate `DONE` or `STOP`.

Main does not discover the repository, create or edit the plan, implement, mutate, or perform review. Main may ask a completed agent a bounded clarification about that agent's existing result. New work MUST go to a fresh agent, never to a used or completed one.

Main acts as the user's representative throughout every phase. Before accepting each task response, Main MUST question it from first principles: whether it preserves the user's actual objective, which assumptions and evidence support it, what omissions or conflicts remain, how dependencies affect the conclusion, and whether completion is demonstrated. It must request concise evidence-based rationale, not hidden reasoning or underlying source dumps. Unresolved decision-critical gaps cannot be treated as acceptance.

Main MUST apply `AGENTS.md` User Prompt Intake and Durable Project Truth through the serial intake contract below. Its role boundary and constitutional precedence stay controlling.

## Task agents and focused exploration

The checker-readable contract declares the task roles. Every task assignment, including critical correction and final verification, must spawn exactly one fresh explorer for each declared explorer jurisdiction. The task parent owns child identities, bounded source assignments, status, findings and integration. It reports that lineage and enough evidence to Main for oversight, without raw contexts. Each parent alone dispatches and relays its explorer assignments; Main never does.

Self-performed exploration (`AGENTS.md` FP-21): only when no authorized interface can spawn child agents that report back to it, the accountable task agent performs each explorer jurisdiction itself as a separate read-only pass. Each pass MUST stay within that jurisdiction's source boundary and disjoint source assignment, and keep its sources, findings and dissent attributed to that jurisdiction. The task agent MUST report the unavailability evidence and the reduced context isolation. Explorer duties then apply to those passes.

Context separation protects each explorer's understanding and decisions from unrelated material. Each child MUST receive the complete binding user intent and constraints, its jurisdiction, the question to resolve and the relevant context. Binding user details MUST reach it in full, never only as a summary. Leave out unrelated source payloads and sibling transcripts. The parent partitions source assignments without overlap or unassigned relevant sources and retains the broader task picture.

The parent must question and reconcile child findings before returning its accountable conclusion: evidence, applicable constraints, dependencies, conflicts, uncertainty, and missing coverage must survive integration. Dissent MUST stay attributed to its child, with an explicit disposition and supporting evidence. Present unresolved dissent as dissent, never as consensus. Cross-jurisdiction questions pass through the parent. An empty jurisdiction still receives its explorer. That explorer returns `SKIPPED + reason` with evidence of the empty scope and MUST stay in its own jurisdiction. Missing required sources or unresolved material conflicts MUST return explicit findings or `HOLD`, never guessed conclusions (FP-27).

Explorers are fresh, read-only, and non-delegating leaves. They report only to their immediate task parent and cannot coordinate directly with siblings or Main. Their scope is:

- Governance Agent: governance sources only, including `agents-manifest.yaml` and routed authorities; no repository code, task-specific project sources or raw diffs. `agents-manifest.yaml` routes Governance Agent authorities only, and only the Governance Agent uses it to select repository or project sources.
- Code Explorer: relevant main implementation code and code dependencies only; no governance documents and no sources assigned to the remaining-sources jurisdiction.
- Remaining Sources Explorer: the explicitly bounded relevant source set outside governance and main code, including applicable project documentation, configuration, source artifacts, and verification records.

Task agents integrate these reports and read only the sources their task requires. Exploration reports support task decisions. Planning and execution explorers MUST NOT approve their own parent's work. Independent review uses fresh task agents and fresh explorer children.

## Role contracts

### Planning Agent

The Planning Agent is read-only and uses the focused-exploration contract. It receives the complete controlling intent and produces one stable ephemeral YAML plan per lifecycle instance. It MUST leave the repository unchanged and create no tracked plan artifact.

The plan must be one YAML mapping in the planning report, with all fields declared once in `plan.required_fields` in the checker-readable contract. Its values MUST preserve the complete intent, objective acceptance, explicit side effects, disjoint execution assignments, dependencies and risks, deterministic verification, terminal evidence and the constitutional authority-application witness. Every required field MUST carry a meaningful task-specific value. An empty applicable obligation is a plan failure.

If a plan file is requested or needed, serialize that same mapping as a `.yaml` file at an explicitly chosen temporary location outside the repository. Keep the plan ephemeral and untracked, with no tracked plan and no parallel Markdown plan. This document stays the owner. The YAML instance is a task control artifact, not another policy authority.

For a substantive plan, `prompt_intake` MUST reference the completed intake dispositions, owner locations and review witnesses. It MUST NOT treat the generated plan as a new user message.

The plan must be specific enough that conforming execution requires no per-file approval. Missing authority, material ambiguity, overlapping mutation ownership, or unverifiable completion is a plan failure, not permission to guess.

### Plan Review Agent

Main dispatches exactly one separate Plan Review Agent after the plan is produced and before confirmation. This agent is read-only and independent, and owns its three focused explorers as the independent council. It MUST check the candidate plan against the complete controlling intent, internal consistency, authorized scope, assignment disjointness, failure conditions, verification and terminal criteria. It MUST also check for silent-failure paths, unhandled edge cases, and resource, security and performance risks. These checks are the review intents. It integrates the source-separated council dispositions and reports its findings to Main. It MUST leave the plan as written and add no scope.

### Clarification Agent

A Clarification Agent is read-only and non-delegating. Main may use one only for a bounded question about already supplied evidence or an existing agent result. It MUST NOT begin source investigation, bypass a task agent's explorer trio, expand scope, revise the plan, authorize a mutation, reassign completed agents or continue a stopped workflow.

### Execution Agents

Execution Agents are the only agents permitted to mutate. Each Execution Agent MUST be fresh, explicitly dispatched after the Main and user confirmation gate is met, assigned a disjoint portion of the confirmed plan, and run under the focused-exploration contract. An Execution Agent MUST:

- read only what its confirmed assignment and governing constraints require;
- perform only the authorized mutations and side effects in that assignment;
- keep unrelated and concurrent work intact;
- run the assignment's confirmed verification; and
- return a concise result with changed surfaces, side effects, evidence, residual risks, and any `HOLD`.

Conforming work within the confirmed assignment needs no per-file approval. The agent MUST return exactly one concise terminal `HOLD` with the reason and required action when the assignment is impossible, unsafe or conflicting, when it cannot meet its acceptance evidence, when the same failure recurs with the same root cause after one correction, or when verification contradicts a claimed result. It MUST NOT negotiate, loop, broaden scope or attempt substitute execution; this extends the no-fallback rule of `docs/agents/governance/coding/coding.md` to agents.

### Review Agents

Review Agents are fresh, independent, read-only task agents with their own fresh explorer trio. After execution freezes, they compare the resulting changes and evidence only against the confirmed plan and preserved user intent, under the same review intents. They cannot edit, invent new scope, impose new preferences, or convert optional improvement into a blocker.

A Review Agent classifies a finding as either plan conformance, a critical finding within the allowed correction classes, or non-blocking/out of scope. It reports to Main only.

## Finite workflow

The normal path is: plan, principle review, Main and user confirmation, execution, final review, then Main's terminal decision. Each bounded intake instance uses these existing phases serially before the affected parent continuation.

### User-message intake

When an actual user message affects authorized repository work, Main MUST suspend the affected work and open one fresh intake instance under `AGENTS.md` User Prompt Intake and Durable Project Truth. Only actual user messages trigger intake; generated agent plans, reports, summaries and artifacts never do. Main MUST process each further user message serially before affected work resumes. Run one intake at a time, and keep parent mutation paused during it.

Before dispatch, Main must retain the message identity, intake-instance identity, and parent continuation: phase, plan identity/version, authorization witness, completed evidence, and exact resume target. For an initial request, absent parent values must be explicitly marked initial and the resume target is substantive PLAN. This record is ephemeral task control evidence, not project truth.

The fresh Planning Agent and its explorer trio MUST retrieve only intake-relevant authorities and records and classify each prompt item. They produce an intake-only plan whose `prompt_intake` field identifies the message and instance, item-to-owner routes, proposed dispositions, the admission or supersession basis, required doc changes, existing-content or exclusion witnesses, and the parent continuation. Independent Plan Review and its fresh trio MUST verify this evidence before Main accepts any disposition or authorizes a write. All affected substantive work MUST stay suspended until intake resolution.

`OWNER_UPDATED` also requires the confirmation gate; a fresh Execution Agent with its trio that persists only admitted owner changes, verifies them, and returns owner locations and evidence; and a frozen-result Review Agent with its trio. The disposition is final only after that review. `OWNER_CURRENT` and `EXCLUDED` end at Plan Review with no write. An intake finishes only when every item has its required evidence. Missing authorization or evidence is HOLD.

A successful intake returns its item dispositions and witnesses to the saved continuation. An initial request then starts substantive work, and compatible steering resumes the same parent phase with its plan and evidence intact. Intake completion is not completion of the user task: the root task reaches DONE only after substantive acceptance and final review. A HOLD or failed intake MUST block dependent work and go to Main's STOP handling. An incompatible replacement or invalidated confirmed scope takes the existing terminal and new-workflow path.

After context loss, Main and the affected parents MUST re-establish the current foundations, controlling messages, verified owner locations, item dispositions and parent continuation before dependent work resumes. Missing continuation or intake evidence is HOLD. Only verified evidence releases the barrier, never summaries or assumed prior capture.

### Plan

Main dispatches one Planning Agent, which coordinates its explorer trio and returns the YAML plan. The plan remains untracked and ephemeral. A plan that cannot resolve scope, authority, assignments, verification, or terminal criteria leads to `STOP`.

### Principle review

Main dispatches exactly one separate Plan Review Agent, which owns its source-separated explorer council and integrates their independent dispositions. Main questions that consolidated response without inspecting underlying sources.

Material unresolved objections lead to `STOP`. Review agents MUST leave the plan unchanged. Main may obtain bounded clarification of an existing report, but there is no review/replan loop.

### Main and user confirmation

Main presents the stable plan and material review dispositions to the user and records the authorization witness under `AGENTS.md` FP-30. Existing explicit authorization in the active workflow satisfies this gate when the reviewed scope and side effects stay within it. Request each confirmation only once. If the reviewed plan requires an action outside that authorization, Main MUST obtain explicit confirmation before that action. Rejection or missing required authorization ends this instance as `STOP`. Message changes follow User-message intake; an incompatible replacement or invalidated confirmed scope ends the parent before a separate workflow.

### Execute

Main dispatches only fresh Execution Agents with disjoint confirmed assignments. Main tracks results without reading raw diffs. An Execution Agent `HOLD`, assignment overlap, unauthorized mutation, or failed required evidence leads to `STOP`.

### Final review

After all execution assignments finish, mutations freeze. Main dispatches fresh independent Review Agent(s) to compare the frozen result only with the confirmed plan and intent. A conforming result proceeds to `DONE`. A noncritical discrepancy or any change that would broaden scope proceeds to `STOP`.

### Critical correction and final verification

Main may authorize this branch exactly once, only for a Review Agent finding in one of the five contract-declared critical classes. The correction must be narrow, preserve the confirmed intent and authorized side effects, and use a fresh Execution Agent with an explicit correction assignment.

After that correction, Main dispatches one fresh Review Agent for one final verification limited to the correction and confirmed plan. That verification leads directly to `DONE` or `STOP`. Only one correction is allowed. Any additional defect, failed verification, missing authority, or need to expand scope leads to `STOP`.

### Terminal decisions

`DONE` means Main has confirmed that the plan's acceptance criteria, authorized mutations, required verification, and final review evidence are complete.

`STOP` means the workflow ended without completion. It is terminal: it never triggers retry, repair, replan, correction beyond the single allowed branch, or new agents. A later user request after STOP begins a new workflow. Compatible steering of an active parent follows User-message intake.

## Durable truth and simplicity

Durable capture and ephemeral-record boundaries follow `AGENTS.md` User Prompt Intake and Durable Project Truth and the documentation jurisdiction.

## Checker-readable contract

The following block is the sole machine-readable projection of this file's narrative contract.

`state_roles` lists only Main-dispatched phase participants. Explorer descendants derive from `delegation`. Structural validation checks declaration shape, outcome partitions, and role/state/plan-field links only. Contract changes apply prospectively: an accepted in-flight plan retains its originating contract, authorization, and evidence, and future plans use the current contract. The transition graph governs substantive instances. `message_intake.return_after` returns successful intake items after their required phase, and `failure_terminal` routes intake failure to Main. Neither declares root DONE.

```orchestration-contract
{
  "version": 3,
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
      "verification", "done_evidence", "stop_conditions", "authority_application", "prompt_intake"
    ]
  },
  "message_intake": {
    "trigger": "USER_MESSAGE",
    "plan_field": "prompt_intake",
    "item_outcomes": ["OWNER_UPDATED", "OWNER_CURRENT", "EXCLUDED", "HOLD"],
    "mutation_outcome": "OWNER_UPDATED",
    "no_mutation_outcomes": ["OWNER_CURRENT", "EXCLUDED"],
    "failure_outcome": "HOLD",
    "phase_roles": {
      "PLAN": "PLANNING_AGENT",
      "PRINCIPLE_REVIEW": "PLAN_REVIEW_AGENT",
      "EXECUTE": "EXECUTION_AGENT",
      "FINAL_REVIEW": "REVIEW_AGENT"
    },
    "dependent_work_barrier": true,
    "return_after": {"OWNER_UPDATED": "FINAL_REVIEW", "OWNER_CURRENT": "PRINCIPLE_REVIEW", "EXCLUDED": "PRINCIPLE_REVIEW"},
    "failure_terminal": "STOP"
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
