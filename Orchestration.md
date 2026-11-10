# Orchestration - Agent Lifecycle and Finite Workflow

## Authority

- This file is the single owner of agent roles, delegation, planning, council separation, execution, review, correction, and terminal decisions in repositories governed by `AGENTS.md`. Support docs, manifests, prompts, and project docs route to it and never redefine it; no role may create a parallel workflow, role taxonomy, plan authority, review loop, or terminal state.
- `AGENTS.md` owns the Fundamental Principles and wins any conflict; when a task cannot satisfy both files, Main decides `STOP`.
- Every dispatch carries the complete controlling user intent, the bounded role, and the assignment.

## Foundations

- Before role work or dispatch, Main and every task parent MUST fully read the foundations declared in `AGENTS.md` Mandatory Foundations, in declaration order, and apply their relevant obligations. A profile match, fallback, summary, or read acknowledgment never replaces a read or proves application.
- Each parent keeps the resolved source identities and full-read evidence, and uses the authority-application witness owned by `docs/agents/governance/evidence/evidence.md` for decision-critical work and acceptance; a non-applicability claim names its scoped basis. Main stays accountable across phases, and each task parent for its assignment and explorer integration.
- A parent passes owner-derived obligations to its source-isolated leaves without forbidden source payloads; applying a foundation never widens a leaf's read permission. Missing domain authority is retrieved through the explorer that owns that source jurisdiction and reconciled by the parent before dependent work or acceptance.
- After context loss, an owner change, or a change to this loading contract, the affected parent re-establishes complete current foundation evidence before resuming, accepting results, or dispatching; a full read is reused only while its complete evidence is still available, a summary never replaces a missing read, and a re-read after a contract change is prospective evidence only.
- A missing, invalid, conflicting, or inaccessible required foundation blocks dependent work: name the exact source and the correction needed, ask the user for text only when repository access cannot supply it, and return `HOLD`.

## Main

Main is the user's single communication and decision hub and represents the user in every phase. It:

- preserves the complete controlling user intent without dropping binding details;
- challenges scope drift, unsupported conclusions, incomplete evidence, and role-boundary violations;
- questions every task response from first principles before accepting it: whether it meets the user's actual objective, which assumptions and evidence support it, what omissions, conflicts, or dependencies remain, and whether completion is demonstrated. It asks for concise evidence-based rationale, never hidden reasoning or source dumps, and an unresolved decision-critical gap is never acceptance;
- dispatches top-level task agents and bounded clarification helpers;
- tracks the active phase, plan version, agent identity, assignment, status, findings, correction use, and terminal evidence;
- reads only the AGENTS-declared foundations, user messages, and concise agent reports, never code, task-specific project docs, raw diffs, or hidden reasoning;
- never discovers the repository, creates or edits the plan, implements, mutates, or reviews, and never reuses a used or completed agent for new work, though it may ask one a bounded clarification about its existing result;
- alone decides and communicates `DONE` or `STOP`.

## Task agents and explorers

- The contract declares the task roles. Every task assignment, including critical correction and final verification, spawns exactly one fresh explorer per declared explorer jurisdiction. The task parent owns the children's identities, bounded source assignments, status, findings, and integration, and reports that lineage and sufficient evidence to Main without raw contexts; Main never dispatches or relays explorer assignments.
- Explorers are fresh, read-only, non-delegating leaves that report only to their task parent and never coordinate with siblings or Main:
  - Governance Agent: governance sources only, including `agents-manifest.yaml` and routed authorities; no repository code, task-specific project sources, or raw diffs.
  - Code Explorer: relevant main implementation code and code dependencies; no governance documents or remaining-sources material.
  - Remaining Sources Explorer: the explicitly bounded relevant sources outside governance and main code, including applicable project documentation, configuration, source artifacts, and verification records.
- Each child receives the complete binding user intent and constraints (a summary never replaces binding details), its jurisdiction, the question to resolve, and relevant context, never unrelated source payloads or sibling transcripts. The parent partitions source assignments with no overlap and no unassigned relevant source, and keeps the broader task picture.
- The parent questions and reconciles child findings before concluding: evidence, constraints, dependencies, conflicts, uncertainty, and missing coverage survive integration. Dissent stays attributed to its child with an explicit disposition and evidence, never presented as consensus, and cross-jurisdiction questions pass through the parent.
- An empty jurisdiction still gets its explorer, which returns `SKIPPED + reason` with evidence of the empty scope and never switches jurisdiction. A missing required source or an unresolved material conflict returns explicit findings or `HOLD`, never a guess.
- Task agents read only the sources their task requires. The explorers of a planning or execution parent cannot approve that parent's work; independent review uses fresh task agents with fresh explorers.
- Self-performed exploration (`AGENTS.md` FP-07): only when no authorized interface can spawn child agents that report back to it, the accountable task agent performs each explorer jurisdiction itself as a separate read-only pass within that jurisdiction's source boundary and disjoint source assignment, keeps each pass's sources, findings, and dissent attributed to that jurisdiction, and reports the unavailability evidence and the reduced context isolation; explorer duties apply to those passes.
- A Clarification Agent is read-only and non-delegating. Main uses one only for a bounded question about already supplied evidence or an existing agent result; it never begins source investigation, bypasses a task agent's explorers, expands scope, revises the plan, authorizes a mutation, reassigns a completed agent, or continues a stopped workflow.

## Workflow

The path is intake, plan, principle review, confirmation, execution, final review, and Main's terminal decision. Each intake instance uses the same phases serially before the affected parent continues.

### User-message intake

- A user message that affects authorized repository work makes Main suspend the affected work and open one fresh intake instance under `AGENTS.md` User Prompt Intake and Durable Project Truth. Agent-generated plans, reports, summaries, and artifacts never trigger intake. Messages are processed serially: no concurrent intake and no parent mutation meanwhile.
- Before dispatch, Main records the message identity, the intake-instance identity, and the parent continuation: phase, plan identity and version, authorization witness, completed evidence, and exact resume target. An initial request marks absent parent values as initial and resumes at substantive PLAN. This record is ephemeral task control evidence, not project truth.
- A fresh Planning Agent retrieves only intake-relevant authorities and records, classifies each prompt item, and returns an intake-only plan whose `prompt_intake` field names the message and instance, item-to-owner routes, proposed dispositions, admission or supersession basis, required doc changes, existing-content or exclusion witnesses, and the parent continuation. An independent Plan Review Agent verifies that evidence before Main accepts any disposition or authorizes a write; affected substantive work stays suspended until intake resolves.
- `OWNER_UPDATED` also needs the confirmation gate, a fresh Execution Agent that persists only the admitted owner changes, verifies them, and returns owner locations and evidence, and a frozen-result Review Agent; it is final only after that review. `OWNER_CURRENT` and `EXCLUDED` end at plan review with no write. An intake finishes only when every item has its required evidence; missing authorization or evidence is `HOLD`.
- Successful intake returns its dispositions and witnesses to the saved continuation: an initial request starts substantive work, and compatible steering resumes the same parent phase with its plan and evidence preserved. Intake completion is not task completion; the root task reaches `DONE` only after substantive acceptance and final review. A `HOLD` or failed intake blocks dependent work and goes to Main's `STOP` handling; an incompatible replacement or invalidated confirmed scope ends the parent, and a new workflow starts.
- After context loss, Main and the affected parents re-establish the current foundations, controlling messages, verified owner locations, item dispositions, and parent continuation before dependent work resumes. Missing continuation or intake evidence is `HOLD`; a summary or assumed prior capture never releases the barrier.

### Plan

- Main dispatches one read-only Planning Agent, which receives the complete controlling intent and returns one stable plan per lifecycle instance: one YAML mapping in its report carrying every field in `plan.required_fields` of the contract.
- The plan preserves complete intent, objective acceptance, explicit side effects, disjoint execution assignments, dependencies and risks, deterministic verification, terminal evidence, and the constitutional authority-application witness. Every required field carries a meaningful task-specific value, and the plan is specific enough that conforming execution needs no per-file approval. For a substantive plan, `prompt_intake` references the completed intake dispositions, owner locations, and review witnesses; a generated plan is never a new user message.
- The plan stays ephemeral and untracked: the Planning Agent never mutates the repository, and never creates a tracked plan or a parallel Markdown plan. When a file is needed, the same mapping is saved as a `.yaml` file at a chosen temporary location outside the repository. It is a task control artifact, not a policy authority.
- Missing authority, material ambiguity, overlapping mutation ownership, an empty applicable field, or unverifiable completion is a plan failure, never permission to guess. A plan that cannot resolve scope, authority, assignments, verification, or terminal criteria leads to `STOP`.

### Principle review

- Main dispatches exactly one separate, read-only, independent Plan Review Agent after the plan and before confirmation; its three explorers are the independent council.
- It checks the candidate plan against the complete controlling intent, internal consistency, authorized scope, assignment disjointness, failure conditions, verification, and terminal criteria, and for silent-failure paths, unhandled edge cases, and resource, security, and performance risks (the review intents). It integrates the source-separated council dispositions and reports findings to Main; it cannot edit the plan or invent scope.
- Main questions that consolidated response without inspecting underlying sources and may obtain a bounded clarification of an existing report. A material unresolved objection leads to `STOP`; there is no review and replan loop.

### Confirmation

- Main presents the stable plan and the material review dispositions to the user and records the authorization witness under `AGENTS.md` FP-12. Explicit authorization already given in the active workflow satisfies this gate while the reviewed scope and side effects stay within it, and duplicate confirmation is prohibited. An action outside that authorization needs explicit confirmation first; user silence is never authorization.
- Rejection or missing required authorization ends the instance as `STOP`. Message changes follow user-message intake.

### Execute

- Only Execution Agents mutate. Each is fresh, dispatched only after confirmation, and assigned a disjoint portion of the confirmed plan.
- An Execution Agent reads only what its assignment and governing constraints require, performs only the authorized mutations and side effects, preserves unrelated and concurrent work, runs the assignment's confirmed verification, and returns a concise result: changed surfaces, side effects, evidence, residual risks, and any `HOLD`. Conforming work needs no per-file approval.
- When the assignment is impossible, unsafe, conflicting, or cannot meet its acceptance evidence, when the same failure recurs with the same root cause after one correction, or when verification contradicts a claimed result, the agent returns exactly one concise terminal `HOLD` with the reason and required action. It never negotiates, loops, broadens scope, or attempts substitute execution.
- Main tracks results without reading raw diffs. An Execution Agent `HOLD`, assignment overlap, unauthorized mutation, or failed required evidence leads to `STOP`.

### Final review

- After all execution assignments finish, mutations freeze and Main dispatches fresh, independent, read-only Review Agents.
- They compare the frozen changes and evidence only against the confirmed plan and preserved user intent, under the review intents, and report to Main only. They cannot edit, invent scope, impose preferences, or turn an optional improvement into a blocker.
- Each finding is classed as plan conformance, a critical finding within the allowed correction classes, or non-blocking or out of scope. A conforming result proceeds to `DONE`; a noncritical discrepancy or any change that would broaden scope proceeds to `STOP`.

### Critical correction and final verification

- Main may authorize this branch exactly once, only for a Review Agent finding in one of the contract-declared critical classes. The correction is narrow, preserves the confirmed intent and authorized side effects, and uses a fresh Execution Agent with an explicit correction assignment.
- One fresh Review Agent then verifies only the correction against the confirmed plan, leading directly to `DONE` or `STOP`. A second correction is prohibited; any further defect, failed verification, missing authority, or need to expand scope leads to `STOP`.

### Terminal decisions

- `DONE`: Main has confirmed that the plan's acceptance criteria, authorized mutations, required verification, and final review evidence are complete.
- `STOP`: the workflow ended without completion. It is terminal and never triggers retry, repair, replan, correction beyond the single allowed branch, or new agents. A later user request starts a new workflow; compatible steering of an active parent follows user-message intake.

## Checker-readable contract

The block below is the sole machine-readable projection of this file. `state_roles` lists Main-dispatched phase participants only; explorer descendants derive from `delegation`. Structural validation checks declaration shape, outcome partitions, and role, state, and plan-field links only. Contract changes apply prospectively: an accepted in-flight plan keeps its originating contract, authorization, and evidence. The transition graph governs substantive instances; `message_intake.return_after` returns successful intake items after their required phase and `failure_terminal` routes intake failure to Main; neither declares root `DONE`.

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
