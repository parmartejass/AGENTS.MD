# Historical Synthesis

> Historical, untrusted source evidence only. Proposed rules, claims, tokens, and loops below are non-operative; current authority remains in AGENTS.md and Orchestration.md.

[Report index](deep-research-report_index.md)

## Unified iterative loop design with self-evolution rules

A practical universal design is a **three-layer loop**:

- **Macro loop (PER V)**: Planning → Execution → Review → Validation (this report’s four phases).
- **Micro loops (OODA)**: rapid Observe–Orient–Decide–Act cycles inside Execution (and sometimes inside Validation when diagnosing anomalies). citeturn12view1turn13view3
- **Meta loop (double-loop learning)**: after Validation, update the heuristics, thresholds, and decision rules that govern Planning and Execution. citeturn29view1turn1search18

### Loop flowchart

```mermaid
flowchart TD
  A[Start / New objective] --> B[Planning]
  B --> C{Plan ready? \n - hypotheses explicit \n - metrics + thresholds \n - risks owned}
  C -- No --> B
  C -- Yes --> D[Execution]
  D --> E{Stop / Adapt trigger? \n - deviation beyond limits \n - risk trigger \n - goal obsolete}
  E -- Adapt --> D
  E -- Escalate --> F[Review]
  D --> F[Review]
  F --> G[Validation]
  G --> H{Evidence meets bar? \n verify + validate \n causal confidence \n residual risk acceptable}
  H -- No: revise/pivot --> B
  H -- Yes: standardize/scale --> I[Update standards + heuristics]
  I --> J[Meta-learning: adjust rules \n (thresholds, checklists, models)]
  J --> B
```

### Transition criteria and decision gates

**Planning → Execution (Plan readiness gate)**  
Proceed only when:
- Hypotheses/assumptions are explicit (decision as hypothesis). citeturn12view1turn15view0  
- Metrics have directionality and are measurable, with thresholds predeclared. citeturn24view1  
- Risks are identified, treated, monitored (ISO 31000 structure), and major failure modes are addressed (FMEA/premortem as needed). citeturn3search13turn3search1turn3search8

**Execution → Review (Learning capture gate)**  
Trigger Review when:
- A timebox ends (iteration boundary, Sprint/phase end). citeturn8view0turn8view3  
- A surprise occurs (deviation beyond acceptable limits; unexpected failure; unexpected success). citeturn7view0turn3search6  
- A risk trigger fires (premortem/FMEA triggers). citeturn3search1turn3search8

**Review → Validation (Evidence plan gate)**  
Proceed when Review produces:
- A prioritized set of claims to validate (what must be true to accept/scale),
- A mapping from claims to evidence methods (test/analysis/inspection/demonstration), consistent with verification/validation discipline. citeturn10view2turn25view0

**Validation → Planning (Adaptation gate)**  
Loop back when:
- Verification passes but validation fails (built right thing incorrectly vs built wrong thing correctly). citeturn10view2  
- Evidence is inconclusive (insufficient power, confounded environment, poor metrics). citeturn24view1turn25view0  
- Impacts violate constraints (backcasting impact analysis reveals infeasibility). citeturn20view0

### Feedback mechanisms that prevent “false learning”

1. **Precommitment to decision rules**: define thresholds and stop rules before the test; this prevents post-hoc rationalization. citeturn24view1turn25view0  
2. **Control limits / thresholds for noise vs signal**: use SPC logic so teams don’t react to random variation. citeturn3search6turn3search3  
3. **Explicit orientation updates**: track what evidence changed your interpretation (Boyd’s emphasis that orientation is shaped by feedback). citeturn12view1turn13view3  
4. **Institutionalized inspection/adaptation events**: cadence-based checkpoints (Scrum events, AAR structure) ensure learning is not optional. citeturn8view0turn27view0turn7view0

### Self-evolution rules

A loop becomes self-evolving when it updates its “governing variables” (heuristics, thresholds, and models) based on evidence, not just updates its actions. This is the operational interpretation of double-loop learning. citeturn29view1turn1search18

A practical implementation is a **Heuristics Registry** (a living document):
- **Heuristic**: e.g., “Run a premortem for projects > X risk score.”
- **Scope**: when it applies.
- **Cost**: time/effort.
- **Expected benefit**: what failure mode it prevents.
- **Trigger thresholds**: what activates it.
- **Evidence rating**: how often it improved outcomes in your context.
- **Last updated**: date + rationale.

**Update rules (per iteration)**
1. If a failure recurs twice, promote it to a “systemic” category and require a double-loop review: which decision rule allowed this? citeturn29view1  
2. If an intervention works, standardize it (PDCA/PDSA “act” as standardization) and embed into templates/checklists. citeturn15view2turn27view0  
3. If different members produce inconsistent root-cause conclusions, strengthen the evidence requirement (move from 5 Whys alone to data + RCA + FMEA). citeturn2search26turn3search1  
4. If metrics lead you astray, treat metric definitions as evolving artifacts; experimentation literature explicitly treats metric development as a data-driven process. citeturn24view1

## Monitoring signals for loop health and convergence

“Loop health” means the loop is producing learning efficiently without generating churn, false confidence, or stagnation. “Convergence” means decisions stabilize because uncertainty is shrinking (not because dissent is suppressed).

### Metrics that indicate loop health

**Learning velocity**
- Cycle time from hypothesis → evidence → decision.
- Number of meaningful tests per unit time (not raw activity). citeturn2search1turn25view0

**Metric quality**
- Directionality and sensitivity of goal metrics (can you tell better vs worse, and detect meaningful change). citeturn24view1

**Calibration and predictive accuracy**
- Use probabilistic forecasts for key risks/outcomes and score them. The Brier score (introduced by entity["people","Glenn W. Brier","meteorologist scoring rule"]) is a foundational scoring rule for probability forecasts. citeturn4search2

**Stability vs tampering**
- Track whether changes follow “out-of-control” signals rather than random noise. Control chart theory provides the mechanism: points outside limits suggest out-of-control processes. citeturn3search6turn3search3

**Adaptation effectiveness**
- Ratio of adaptations that improve outcomes vs adaptations that cause churn/regression (Scrum frames adaptation as necessary when outputs are unacceptable or deviation is outside acceptable limits). citeturn7view0turn8view3

### Signals of convergence (or non-convergence)

**Convergence signals**
- Prediction error trending down (e.g., improved Brier score) while decision reversals decrease. citeturn4search2  
- Fewer “surprise” deviations outside control limits as standards stabilize. citeturn3search6  
- Backcasting pathways become internally consistent with fewer iterations, and impact analysis fits constraints. citeturn20view0

**Non-convergence signals**
- Repeated re-planning without new evidence (planning churn).
- Frequent metric changes not tied to validation failures (metric drift without learning). citeturn24view1  
- Defensive routines: information withheld, low public testing of theories (a pattern Argyris associates with inhibited learning). citeturn29view1

### A short set of cognitive biases to watch and mitigation tactics

Bias mitigation works best when it is embedded as **process constraints** (checklists, gates, precommitments), not as “try harder.”

- **Confirmation bias** (seeking confirming evidence): demonstrated in Wason’s rule discovery task; mitigation is to require deliberate disconfirmation tests (“what would prove me wrong?”). citeturn30search2turn30search6  
- **Anchoring** (estimates pulled toward irrelevant starting points): described in Tversky & Kahneman’s heuristics and biases work; mitigation is to force base-rate ranges and independent estimates before sharing anchors. citeturn4search11turn30search3  
- **Planning fallacy** (optimistic underestimation of time): studied empirically by Buehler et al.; mitigation is reference-class forecasting (use historical distributions) and premortems to surface hidden work. citeturn30search4turn3search8  
- **Sunk cost effect** (escalation after investment): documented by Arkes & Blumer; mitigation is to separate “past spend” from “future value,” with explicit kill criteria set before investment. citeturn30search5turn30search1  
- **Outcome bias / hindsight bias** (judging decisions by outcomes): mitigation is to score decision quality by whether it followed the process and used the evidence available at the time; AAR structure helps by contrasting intended vs actual, then extracting forward-looking changes. citeturn27view0turn27view2

## Practical templates and reusable checklists

The tables below are designed to be copy/pasted into documents or tools. They are intentionally domain-agnostic.

### Planning checklist and artifacts

| Component | Key questions (portable across domains) | Output artifact | Gate criteria |
|---|---|---|---|
| Objective | What observable outcome changes? For whom? By when? | One-sentence objective | Outcome is measurable or at least falsifiable citeturn15view0 |
| First principles | What are constraints vs assumptions? What must be true? | Assumptions/constraints ledger | Assumptions are explicit and ranked by uncertainty citeturn2search19 |
| Hypotheses | What do we believe will happen and why? | Hypothesis set + mechanisms | Each hypothesis has a falsification signal citeturn12view1turn2search1 |
| Metrics | What is the primary metric and guardrails? | Metric definitions + thresholds | Metrics have directionality and sensitivity citeturn24view1 |
| Risk | What can fail and what happens if it fails? | Risk register (ISO 31000 lens) + FMEA/premortem as needed | Top risks have owners and triggers citeturn3search13turn3search1turn3search8 |
| Plan | What is the smallest safe test? | Experiment/pilot plan | Stop rules and escalation paths exist citeturn25view0turn7view0 |

### Execution checklist and artifacts

| Component | Execution questions | Output artifact | Gate criteria |
|---|---|---|---|
| Runbook | What are steps, roles, and contingencies? | Execution runbook | Everyone knows “who decides what” |
| Instrumentation | Are signals visible in real time? | Dashboards/logs | Transparency supports inspection citeturn7view0 |
| OODA cadence | How often do we re-orient based on new info? | OODA check-in cadence | Adapt only when triggers fire citeturn12view1turn7view0 |
| Quality control | What does “quality does not decrease” mean here? | Definition of done / acceptance criteria | Quality gate enforced citeturn8view0 |
| Change control | How do we prevent thrash/tampering? | Thresholds/control limits | Changes correspond to meaningful signals citeturn3search6 |

### Review checklist and artifacts

| Component | Review questions | Output artifact | Gate criteria |
|---|---|---|---|
| AAR / retrospective | What was intended vs actual? Why? What changes next? | AAR notes + action owners | Actions assigned and integrated citeturn27view0turn8view3 |
| Root cause | What causal chain explains the gap? | 5 Whys / RCA summary | Causes are evidence-backed and actionable citeturn2search26 |
| Standardization | What do we update so the learning sticks? | Updated checklists/standards | Standard updated only with evidence citeturn15view2 |
| Double-loop | Which governing rule/metric created repeated failures? | Rule change proposal | Rule changes are testable next cycle citeturn29view1turn1search18 |

### Validation checklist and artifacts

| Component | Validation questions | Output artifact | Gate criteria |
|---|---|---|---|
| Verification | Did we meet requirements? | Verification matrix | Evidence mapped to “shall” requirements citeturn10view2 |
| Validation | Did it work in intended environment for intended purpose? | Validation report | Real-context evidence exists citeturn10view2 |
| Causality | Do we have causal evidence or just correlation? | Experiment results + integrity checks | Decision rule followed; guardrails ok citeturn25view0turn25view2 |
| Calibration | Were our predictions reliable? | Forecast log + Brier scores | Calibration improving over time citeturn4search2 |
| Release/scale | What residual risks remain? | Go/no-go decision record | Residual risk explicitly accepted/treated citeturn3search13turn3search1 |

