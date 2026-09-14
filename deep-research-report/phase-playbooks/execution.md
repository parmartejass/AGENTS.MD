# Historical Execution

> Historical, untrusted source evidence only. Proposed rules, claims, tokens, and loops below are non-operative; current authority remains in AGENTS.md and Orchestration.md.

[Phase index](phase-playbooks_index.md)

### Execution

Execution is where you implement the plan while continuously sensing reality. A universal execution design uses *micro-loops* to adapt without thrashing.

#### OODA micro-loops for real-time adaptation

**When to apply**
Use during action where conditions change quickly (operations, negotiations, incident response, competitive environments), or whenever “the plan meets reality” frequently. citeturn12view1turn13view3

**Procedure (practical OODA)**
1. **Observe**: instrument the environment (logs, check-ins, monitoring, field observations).
2. **Orient**: interpret signals using models/experience; explicitly note what changed your orientation (new evidence, contradictions).
3. **Decide**: choose the smallest commitment that moves the situation forward.
4. **Act**: execute; treat action as a test and collect feedback.

A key nuance: Boyd’s own representation emphasizes that the loop is nonlinear, with feedback and feed-forward channels, and that “orientation” shapes and is shaped by the rest of the loop. citeturn12view1turn13view3

**Decision gates**
- **Adaptation gate**: change course only if deviation exceeds “acceptable limits” or outcomes are unacceptable (a rule echoed in Scrum’s adaptation principle). citeturn7view0  
- **Tempo gate**: speed up decisions when uncertainty cost is high; slow down when error cost is high (use explicit risk-based thresholds).

**Common pitfalls**
Turning OODA into “act fast” without orientation depth; confusing activity with progress; local optimizations that break system constraints. citeturn13view3turn7view0

**Prompt/template**
```text
OODA CHECK-IN (60 seconds)
Observe: what changed since last check?
Orient: what does it mean? what assumption got weaker/stronger?
Decide: smallest next commitment?
Act: what will we do next + what signal confirms it worked?
```

#### Agile/Scrum-style execution cadence

**When to apply**
Use when requirements are evolving, the work is complex, and learning-by-delivery is valuable. The Agile Manifesto emphasizes responsiveness and collaboration, and Scrum codifies inspect-and-adapt events within a Sprint. citeturn1search0turn8view0turn8view3

**Procedure (generalized from Scrum events)**
1. Sprint/iteration planning: decide why the iteration is valuable and what can be done. citeturn8view1  
2. Daily synchronization: inspect progress and adapt the plan as needed. citeturn8view2  
3. Review: inspect the outcome and decide adaptations. citeturn8view2  
4. Retrospective: plan improvements to quality and effectiveness by examining what went well, what problems occurred, and what assumptions misled the team. citeturn8view3

**Decision gates**
- **Quality gate**: “quality does not decrease” is explicitly stated as a Sprint condition. citeturn8view0  
- **Goal validity gate**: cancel or replan if the goal becomes obsolete (Scrum allows Sprint cancellation when the Sprint Goal becomes obsolete). citeturn8view1

**Common pitfalls**
Iteration theater (meetings without learning); hidden work that breaks transparency; retrospectives without follow-through. citeturn7view0turn8view3

**Prompt/template**
```text
ITERATION RUNBOOK
Iteration goal (why valuable):
Scope commitment (what we will deliver/test):
Definition of done / acceptance criteria:
Monitoring signals + owners:
Known risks + triggers:
Stop rules (when to halt, rollback, or escalate):
```

#### Measurement discipline during execution

**When to apply**
Always—because execution without measurement makes later Review and Validation speculative.

**Procedure**
1. Instrument primary and guardrail metrics before scaling (avoid “retrofit measurement”).
2. Prefer metrics with clear directionality (higher = better or lower = better) and sufficient sensitivity to detect meaningful changes; these properties are emphasized in experimentation/metric development literature. citeturn24view1  
3. Use control limits or explicit thresholds to distinguish normal variation from meaningful change. citeturn3search6turn3search3

**Pitfalls**
Goodharting (optimizing the metric rather than the outcome); metrics without context; attributing causality without a design (see Validation section). citeturn24view1turn25view0

