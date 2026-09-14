# Historical Planning

> Historical, untrusted source evidence only. Proposed rules, claims, tokens, and loops below are non-operative; current authority remains in AGENTS.md and Orchestration.md.

[Phase index](phase-playbooks_index.md)

### Planning

Planning is where you decide **what you are doing**, **why**, and **how you will know** whether it worked. High-quality planning makes decisions testable and reduces later rework.

#### First principles decomposition

**When to apply**
Use when the problem is novel, analogies conflict, or you suspect inherited assumptions are misleading. The goal is to surface axioms/constraints explicitly before choosing methods. citeturn2search19turn2search0

**Procedure**
1. State the objective in one sentence, as an observable outcome (not an activity).
2. List constraints and invariants (budget caps, physical limits, regulatory constraints, immutable deadlines).
3. Decompose the objective into necessary conditions (what must be true for success).
4. For each condition, ask: “What is the simplest mechanism that could satisfy it?”
5. Only then consider analogies/benchmarks as optional accelerators (not foundations).

**Decision gate**
Proceed when you can answer: “If we remove any assumption, what changes?”—and can distinguish assumptions from constraints.

**Common pitfalls**
Confusing constraints with preferences; prematurely importing solutions; staying abstract and never translating axioms into testable commitments. citeturn2search19turn2search0

**Prompt/template**
```text
FIRST-PRINCIPLES PLANNING
Objective (observable outcome):
Constraints/invariants (must be true):
Key assumptions (could be wrong):
Necessary conditions for success (3–7):
Simplest mechanisms per condition:
What evidence would falsify each assumption?
```

#### Backcasting and scenario pathways

**When to apply**
Use when you need a long-term direction (20–100 years in Robinson’s framing, but the method scales down) and want to work backward from a desired end-state to near-term actions. citeturn19view0turn20view2turn23view0

**Procedure (Robinson’s six steps, adapted to general use)**
1. Determine objectives: purpose, scope, number/type of scenarios. citeturn20view2  
2. Specify goals, constraints, targets (include negative constraints like “must not exceed X”). citeturn20view2  
3. Describe the present system (baseline). citeturn20view2  
4. Specify exogenous variables (outside factors you won’t control but must assume). citeturn20view2  
5. Undertake scenario analysis; iterate for internal consistency. citeturn20view2  
6. Undertake impact analysis; compare impacts to goals/constraints and iterate. citeturn20view0

**Decision gates**
- **Vision gate**: end-state is specific enough to constrain choices.
- **Feasibility gate**: at least one pathway is internally consistent.
- **Impact gate**: impacts are acceptable relative to targets/constraints. citeturn20view0turn23view0

**Common pitfalls**
Backcasts misread as predictions; “middle scenario” treated as most likely (Robinson explicitly warns of this audience tendency); impact assessment skipped; pathways not translated into commitments. citeturn20view2turn23view0

**Prompt/template**
```text
BACKCASTING SNAPSHOT
Desired future (date + characteristics + targets):
Non-negotiable constraints:
Baseline (current state metrics):
Exogenous variables (assumed outside control):
Pathway milestones (T-24m, T-12m, T-3m, now):
Critical feasibility uncertainties:
Impact risks (social/economic/technical/safety) + mitigations:
```

#### Hypothesis-driven planning (PDSA-style)

**When to apply**
Use when the correct approach is uncertain and you can learn quickly by testing. This is the core logic behind PDSA/PDCA evolution and Lean Startup’s build-measure-learn. citeturn15view0turn2search1

**Procedure**
1. Convert the plan into explicit hypotheses (“If we do X, then Y will improve because Z”).
2. Define leading and lagging indicators; ensure your goal metrics have clear directionality and sensitivity (in experimentation literature, these properties are treated as critical for goal metrics). citeturn24view1  
3. Design the smallest safe test (MVP, pilot, prototype, simulation, limited rollout).
4. Predefine decision thresholds (what evidence counts as success/failure/inconclusive).
5. Predefine what you will change if results are negative/inconclusive (pivot/persevere logic).

**Decision gate**
Do not execute at scale until: hypotheses are written; measurement is feasible; thresholds and “stop rules” exist.

**Common pitfalls**
Vague hypotheses; metrics that don’t measure what matters; decision thresholds invented after seeing results (p-hacking-by-process); collecting data without a plan to interpret it. citeturn24view1turn25view0

**Prompt/template**
```text
HYPOTHESIS PLAN
Hypothesis:
Mechanism (why it should work):
Primary metric (directionality + sensitivity):
Guardrail metrics (must not worsen):
Test design (who/where/how long):
Decision thresholds (win/lose/inconclusive):
If win → scale plan:
If lose → root-cause + alternative hypothesis:
If inconclusive → what to change in next test:
```

#### Risk analysis: ISO 31000 + FMEA + premortem

**When to apply**
Use for high-consequence decisions, irreversible commitments, safety/security-critical outcomes, or when uncertainty is large.

**Procedure**
- Use the risk management process lens from entity["organization","International Organization for Standardization","standards body geneva"]: identify, analyze, evaluate, treat, then monitor/communicate risk. citeturn3search13  
- Use FMEA as a structured “what can fail and what happens if it fails” tool; entity["organization","American Society for Quality","quality professional society"] describes it as a systematic, step-by-step approach developed in the U.S. military context and now broadly used. citeturn3search1  
- Use a premortem (published in entity["organization","Harvard Business Review","business magazine"] by entity["people","Gary Klein","cognitive psychologist"]) to surface risks by assuming the project failed and generating plausible causes. citeturn3search2turn3search8

**Decision gate**
You can proceed when top risks have owners, mitigations, and trigger conditions; and the residual risk is acceptable relative to the stakes.

**Common pitfalls**
Risk lists without ownership; mitigations that are actually hopes; ignoring tail risks; premortems becoming blame-seeking rather than system-focused. citeturn3search13turn3search8turn3search1

**Prompt/template**
```text
RISK PACKAGE (FAST)
Top 10 failure modes (what fails?):
Effects (impact if it fails):
Likelihood / detectability (qualitative or scaled):
Mitigation (prevent / detect / respond):
Trigger (what early signal tells us it’s happening?):
Owner + review cadence:
Residual risk acceptability (yes/no and why):
```

