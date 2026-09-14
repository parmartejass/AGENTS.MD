# Historical Validation

> Historical, untrusted source evidence only. Proposed rules, claims, tokens, and loops below are non-operative; current authority remains in AGENTS.md and Orchestration.md.

[Phase index](phase-playbooks_index.md)

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

