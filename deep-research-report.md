# Self-Evolving Decision Loops for Domain-Agnostic Planning, Execution, Review, and Validation

## Executive summary

A universal decision loop can be designed as a **learning system**: every cycle converts uncertainty into knowledge, then converts knowledge into better decisions. The most durable cross-domain pattern is “**hypothesize → act/test → observe → learn → adapt**,” which appears in quality improvement (PDSA/PDCA), competitive decision-making (OODA), iterative product delivery (Agile/Scrum), and empirically grounded experimentation (controlled experiments). citeturn15view0turn12view1turn8view0turn2search1turn25view0

A practical four-phase loop—**Planning → Execution → Review → Validation**—works best when it (a) keeps **decisions explicit and testable**, (b) separates **signal vs. noise** so teams don’t “tamper” based on randomness, and (c) distinguishes **internal learning (Review)** from **external correctness (Validation)** using verification/validation discipline. citeturn15view0turn3search6turn10view2turn27view0turn8view3

To become **self-evolving**, the loop needs a meta-layer (a “loop about the loop”): after each cycle, update not only the plan and tactics, but also the **heuristics, thresholds, and decision rules**—the essence of double-loop learning. citeturn29view1turn1search18turn12view2

## Foundational principles behind domain-agnostic reasoning loops

A robust universal loop rests on a small set of principles that recur across authoritative frameworks:

**Iteration as a scientific learning process.** The quality improvement lineage explicitly ties improvement cycles to the scientific method: Shewhart’s “specification–production–inspection” is framed as hypothesis–experiment–test, and later Deming variants emphasize studying results and iterating “around and around the cycle.” citeturn15view0turn15view1turn0search16

**Decisions as hypotheses; actions as tests.** In Boyd’s OODA sketch, “Decision (Hypothesis)” and “Action (Test)” are explicit, and “Orientation” is depicted as the core synthesizing filter shaped by feedback and environment. That framing generalizes: treat any commitment (design choice, policy, plan, process change) as a hypothesis with observable consequences. citeturn12view1turn13view3

**Transparency → inspection → adaptation.** Scrum’s theory is explicit: progress must be visible (transparency), frequently inspected, and adapted when deviations exceed acceptable limits or when results are unacceptable—an operational definition of a healthy feedback loop. citeturn7view0turn8view0turn8view2

**Separate internal learning from external correctness.** Systems engineering distinguishes:
- **Verification**: evidence the product meets stated requirements (“building the product right”).  
- **Validation**: evidence the product accomplishes its intended purpose in its intended environment (“building the right product”). citeturn10view2  
That distinction cleanly maps to “Review” (internal learning) versus “Validation” (external evidence).

**Avoid false learning by managing uncertainty and variability.** Statistical process control emphasizes control limits and “out-of-control” signals; a key universal lesson is: do not overreact to normal variation—use thresholds and rules to decide when a change is meaningful. citeturn3search6turn3search3

**First principles and axioms for clarity.** The philosophical idea of “first principles” emphasizes that any systematic inquiry depends on foundational, not-further-derived starting points; practically, this becomes: explicitly state assumptions/constraints/axioms before deriving plans. citeturn2search19turn2search0

## Framework landscape and comparison

The following eight frameworks are commonly used as “reasoning primitives.” They are not mutually exclusive; a well-designed loop composes them.

| Framework | Scope | Strengths | Weaknesses | Best-use cases |
|---|---|---|---|---|
| PDCA / PDSA | Continuous improvement cycle | Simple, general, explicitly iterative; aligned with scientific method lineage | Can degrade into checkbox compliance (“do/check” without real learning) if hypotheses, measures, and standards are weak | Process/product improvement; operations; recurring work; incremental change citeturn15view0turn0search16turn0search11 |
| OODA | Real-time decision + adaptation under uncertainty | Emphasizes feedback, tempo, and the centrality of orientation; treats decisions as hypotheses and actions as tests | Often oversimplified into a 4-step circle; can become reactive if orientation is shallow | Dynamic environments, incident response, strategy under competition/uncertainty citeturn12view1turn13view3turn13view1 |
| DMAIC | Structured problem-solving for improving existing processes | Strong structure for diagnosing underperformance and root causes; forces measurement discipline | Heavyweight for highly exploratory/novel problems; can over-focus on measurable proxies | Optimization of existing processes with defined defects/metrics citeturn0search2 |
| Agile (values + iterative delivery) | Delivery philosophy emphasizing responsiveness | Institutionalizes iteration, stakeholder collaboration, and adaptability | “Agile” can be adopted superficially; may under-invest in upfront risk analysis for high-stakes systems | Complex work with evolving requirements; learning during delivery citeturn1search0turn1search19 |
| Hypothesis-driven (experimentation cycles) | Learning via explicit assumptions and tests | Makes uncertainty explicit; supports pivot/persevere decisions; reduces costly over-planning | Needs good instrumentation and experimental rigor; experiments can answer “what” but not always “why” | New products/strategies; uncertain causality; fast learning loops citeturn2search1turn25view0turn24view1 |
| First principles reasoning | Problem decomposition from axioms/constraints | Clarifies assumptions; avoids inherited “solution bias”; improves transfer across domains | Can be slow; risk of neglecting empirical constraints if too abstract | Novel design, strategy reset, when analogies/benchmarks fail citeturn2search19turn2search0 |
| 5 Whys | Root-cause probing via iterative “why” questions | Fast, teachable, forces causality chains | Can be arbitrary depth; results can be non-repeatable; may stop at symptoms or single-cause narratives | Quick diagnosis; complement to deeper RCA tools; incident learning citeturn2search11turn2search26 |
| Backcasting | Normative scenario planning from desired end-state backward | Strong for long-horizon direction; clarifies feasibility and policy/action implications; explicitly iterative | Not predictive; can be misinterpreted as forecast; can be resource-intensive (scenario + impact analysis) | Strategy with long horizons; transformation; “future state → pathway” planning citeturn19view0turn20view2turn23view0 |

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["OODA loop sketch John Boyd diagram","PDCA cycle diagram Deming Shewhart","DMAIC cycle define measure analyze improve control diagram","Scrum sprint planning daily scrum sprint review retrospective diagram"],"num_per_query":1}

## Phase playbooks

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

### Review

Review turns execution history into reusable learning. It should surface (1) what happened vs intended, (2) why, and (3) what to change next.

#### After Action Review (AAR) / structured debrief

**When to apply**
Use after meaningful events (deliveries, incidents, launches, negotiations, experiments) and especially after surprises. The entity["organization","United States Army","us army"] formalizes AAR practice with explicit agendas and steps. citeturn27view0turn27view2

**Procedure**
1. Review what was supposed to happen.
2. Establish what happened.
3. Determine what was right/wrong with what happened.
4. Determine how to perform better next time. citeturn27view0  

The Army also frames an AAR process as: Plan, Execute, Evaluate, Integrate/share lessons learned. citeturn27view0turn27view2

**Decision gates**
- **Closure gate**: every review ends with specific changes, owners, and integration into next iteration.
- **No-blame gate**: keep focus on performance against standards and improvement (AAR guidance emphasizes professional discussion and learning, not critique). citeturn27view1turn27view2

**Common pitfalls**
Storytelling without evidence; outcome bias (judging quality of decision by outcome); lack of follow-through integration. citeturn27view2turn29view1

**Prompt/template**
```text
AAR (15–30 minutes)
Intent/expected outcome:
What actually happened (timeline + data):
What went well (and why):
What went poorly (and why):
Key decision points + assumptions:
Actions to change next time (owner + due date):
What to monitor to ensure the change sticks:
```

#### PDCA/PDSA “Study” and standardization learning

**When to apply**
Use when you want continuous improvement and recurrence prevention. Deming’s lineage emphasizes studying results and repeating cycles with accumulated knowledge. citeturn15view2turn15view1turn0search16

**Procedure**
1. Compare results to predictions (did the hypothesis hold?).
2. Identify what changed in the system (not just the output).
3. If successful, standardize (update standard work/checklists/definitions).
4. If not, revise theory and plan the next test. citeturn15view2turn15view0

**Decision gate**
Do not “scale” a change until you can articulate: what was learned, what will be standardized, and what risk remains.

**Common pitfalls**
Confusing “checking” with superficial inspection; changing standards without evidence; repeating tests without updating hypotheses. citeturn15view2turn15view0

#### Root cause analysis with 5 Whys (as a lightweight RCA)

**When to apply**
Use for quick causal exploration, especially when coupled with stronger tools (data, fishbone, fault trees, FMEA).

**Procedure**
1. State the problem in observable terms (what, where, when, magnitude).
2. Ask “why?” and answer with evidence.
3. Repeat until you reach an actionable cause that can be changed by your system (not a vague label like “human error”).
4. Validate the cause by checking whether it predicts other observations (avoid single-path narratives).

Lean sources define 5 Whys as repeatedly asking why to get beyond symptoms to root cause, associated with entity["people","Taiichi Ohno","toyota production leader"]’s practice. citeturn2search11turn2search26

**Decision gate**
Stop only when the identified cause is (a) actionable, (b) supported by observed evidence, and (c) linked to a prevention/control change.

**Common pitfalls**
Arbitrary depth; different investigators producing different causes; stopping at symptoms; forcing a single root cause. These critiques are documented in medical quality literature criticizing 5 Whys as a weak RCA tool if used alone. citeturn2search26

**Prompt/template**
```text
5 WHYS (EVIDENCE-BASED)
Problem statement (observable):
Why #1 (evidence):
Why #2 (evidence):
Why #3 (evidence):
Why #4 (evidence):
Why #5 (evidence):
Candidate fix (system/process change):
How we’ll verify the fix prevents recurrence:
```

#### Double-loop learning as “review of the rules”

**When to apply**
Use when you see repeated failure modes, defensive routines, or when improvements plateau. Double-loop learning changes not just actions but the governing variables and decision rules. citeturn29view1turn1search18

**Procedure**
1. Identify recurring failure patterns across cycles.
2. Ask: “What decision rule, incentive, metric, or assumption made this likely?”
3. Propose a change to the rule itself (e.g., change the gate threshold, redefine the metric, alter who decides).
4. Test the new rule in the next cycles, and keep evidence of whether it improved outcomes.

Argyris distinguishes models that produce “single loop learning” versus “double loop learning,” with “testable processes” and more public testing in a more learning-oriented model. citeturn29view1turn29view0

### Validation

Validation is the evidence phase: you establish whether outputs/outcomes are correct *in the intended environment* and whether causal claims hold.

#### Verification vs validation discipline

**When to apply**
Always for high-stakes work; particularly when delivering to users/customers, releasing changes that affect safety, or meeting formal requirements.

**Procedure**
1. **Verify**: show compliance with “shall” requirements via test/analysis/inspection/demonstration (or combination). citeturn10view2  
2. **Validate**: show the product accomplishes intended purpose in intended environment and meets stakeholder expectations (again via test/analysis/inspection/demonstration). citeturn10view2  
3. Maintain traceability: which evidence supports which requirement/purpose.
4. Decide on release/acceptance using predeclared acceptance criteria.

**Decision gates**
- **Release gate**: no release without passing verification criteria and a defined validation argument (what evidence proves real-world purpose). citeturn10view2  
- **Safety gate**: if residual risk is high, require stronger evidence (larger tests, independent review, redundancy). citeturn3search13turn3search1

**Common pitfalls**
Validating against the wrong environment; skipping validation because verification passed; “requirements” that are incomplete or not actually tied to stakeholder intent. citeturn10view2

#### Controlled experiments and causal validation

**When to apply**
Use when you need causal evidence for changes (A/B tests, randomized trials, controlled pilots). Controlled experiments can tell you which variant won, but they may not fully explain why—so complement them with theory and qualitative investigation. citeturn25view0turn24view1

**Procedure (general causal validation)**
1. Specify the comparison: control vs treatment (or baseline vs change).
2. Define the overall evaluation criterion (primary metric) and guardrails.
3. Ensure randomization or credible counterfactual design (when randomization isn’t possible, use weaker but explicit quasi-experimental logic and treat conclusions as less certain).
4. Run long enough for meaningful detection; interpret with uncertainty bounds.
5. Re-check instrumentation and data integrity before celebrating large effects (experimentation practice explicitly warns to “find the flaw” for “amazing” results). citeturn25view2turn24view1

**Decision gate**
Adopt the change only if:
- Primary metric improves beyond threshold,
- Guardrails do not regress,
- Result is credible (no major integrity threats),
- External validation context matches intended deployment.

**Common pitfalls**
Metric gaming; running tests without clear directionality/sensitivity; misinterpreting statistical significance as practical significance; assuming causality from observational changes. citeturn24view1turn25view0

**Prompt/template**
```text
VALIDATION EXPERIMENT BRIEF
Claim to validate (causal statement):
Primary metric + minimum meaningful effect:
Guardrails:
Population + environment match to real use? (Y/N)
Design (randomized / controlled pilot / other):
Integrity checks (logging, assignment, missing data):
Decision rule:
What additional evidence explains “why” if needed:
```

#### Backcasting impact analysis as validation for long-horizon plans

Backcasting explicitly includes an impact analysis step and requires comparison of scenario results and impacts back to the goals/constraints, iterating if inconsistent. This is a “validation layer” for strategic plans: it tests feasibility and implications rather than predicting likelihood. citeturn20view0turn19view0

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

## Key references

The sources below are “load-bearing” for the loop design and were prioritized because they are primary, seminal, or authoritative.

- entity["people","Walter A. Shewhart","statistical quality pioneer"] and entity["people","W. Edwards Deming","quality management pioneer"] lineage of improvement as scientific method; history and evolution of PDSA/PDCA in Deming Institute materials (Moen). citeturn15view0turn15view1turn15view2  
- entity["people","John R. Boyd","u.s. air force strategist"] OODA sketch emphasizing orientation, feedback, and decisions-as-hypotheses/actions-as-tests; contextualized in Air University Press edition. citeturn12view1turn12view2turn13view1turn13view3  
- entity["organization","NASA","us civil space agency"] systems engineering distinction between verification and validation. citeturn10view2  
- Backcasting method steps and iterative impact analysis in entity["people","John B. Robinson","futures researcher"] (1990) and participatory framework in entity["people","Jaco Quist","sustainability researcher"] and entity["people","Philip Vergragt","technology assessment scholar"] (2006). citeturn20view2turn20view0turn23view0  
- entity["organization","United States Army","us army"] After Action Review structure and agenda (FM 7-0 Appendix K). citeturn27view0turn27view2  
- Scrum inspect-and-adapt events (planning, daily scrum, review, retrospective) and pillars (transparency/inspection/adaptation) by entity["people","Ken Schwaber","scrum co-creator"] and entity["people","Jeff Sutherland","scrum co-creator"]. citeturn8view0turn8view2turn8view3turn7view0  
- DMAIC definition from entity["organization","American Society for Quality","quality professional society"] as structured improvement approach. citeturn0search2  
- Experimentation practice and cautions (e.g., “winner not why,” integrity skepticism) in work by entity["people","Ron Kohavi","online experimentation researcher"] and metric quality concepts (directionality/sensitivity) in KDD work by Alex Deng & coauthors. citeturn25view0turn25view2turn24view1  
- Double-loop learning: Argyris’ Model I vs Model II differences and the concept of changing governing variables, with Exhibit contrasting single- vs double-loop learning. citeturn29view1turn29view0  
- Core bias literature: entity["people","Amos Tversky","cognitive psychologist"] & entity["people","Daniel Kahneman","psychologist nobel laureate"] (heuristics/biases), Wason (confirmation-seeking in hypothesis tests), Arkes & Blumer (sunk cost), Buehler et al. (planning fallacy). citeturn4search11turn30search2turn30search5turn30search4