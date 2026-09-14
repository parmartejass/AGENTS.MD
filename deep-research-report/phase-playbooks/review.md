# Historical Review

> Historical, untrusted source evidence only. Proposed rules, claims, tokens, and loops below are non-operative; current authority remains in AGENTS.md and Orchestration.md.

[Phase index](phase-playbooks_index.md)

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

