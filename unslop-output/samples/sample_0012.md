# Prompt Engineering for Reliable Backend Code Generation

## Core Problem

AI coding errors in backend logic cluster around a few root causes: ambiguous requirements, missing context, no validation loop, and prompts that optimize for "something that compiles" rather than "something correct." The techniques below target each.

---

## 1. Specification-First Prompting

Never ask for code directly. Ask for a spec, validate it, then ask for code.

```
Step 1:
"Before writing any code, describe in plain English what this function should do,
its inputs/outputs, edge cases it must handle, and any invariants that must hold.
Don't write code yet."

Step 2 (after reviewing):
"Now implement exactly what you described above."
```

**Why it works:** Code generation from a validated spec has a forcing function — the model can't silently reinterpret requirements mid-generation.

---

## 2. Constraint Anchoring

Embed hard constraints directly in the prompt, not as suggestions.

**Weak:**
> "Write a payment processor, make sure it's safe."

**Strong:**
> "Write a payment processor with these non-negotiable constraints:
> - All DB writes must be in a single ACID transaction
> - No amount can be negative or exceed MAX_AMOUNT
> - Idempotency key must be checked before any mutation
> - On failure, state must be identical to pre-call state
> Violating any constraint is a bug, not a tradeoff."

List constraints as a numbered checklist — the model can verify against them during generation.

---

## 3. Persona + Anti-Persona Technique

Assign two competing roles in one prompt.

```
"You are two engineers reviewing this design:
- Engineer A: Implement this order processing system efficiently.
- Engineer B: Find every race condition, failure mode, and edge case in
  Engineer A's approach before any code is written.

Have them debate, then produce a final implementation that addresses
all of Engineer B's objections."
```

This elicits self-critique without a separate prompt round.

---

## 4. Context Saturation

Backend bugs often come from the model making assumptions about your environment. Eliminate assumption surface area.

Include in every backend prompt:

```
Environment:
- Language/runtime: Go 1.22, standard library only
- DB: PostgreSQL 16, using pgx/v5 driver
- Concurrency model: goroutines, no shared mutable state allowed
- Error handling convention: wrap with fmt.Errorf("%w"), never swallow
- Auth context: always present in ctx, type auth.Claims
- Existing patterns: [paste 1-2 examples from your codebase]
```

**Paste real code from your codebase.** The model will mirror your patterns instead of inventing its own.

---

## 5. Decomposition Before Implementation

For complex logic, force decomposition as a precondition.

```
"Break this task into independent subtasks where each subtask:
1. Has a clear input/output contract
2. Can be tested in isolation
3. Has no implicit dependencies on other subtasks

List the subtasks, their contracts, and the integration points.
Do not implement anything yet."
```

Then implement subtask by subtask with separate prompts. This prevents the model from conflating concerns and producing untestable monoliths.

---

## 6. Failure Mode Enumeration

Explicitly demand error path coverage.

```
"For every external call, IO operation, and state mutation in this function,
enumerate:
- What can fail
- What state the system is in after failure
- How the caller is informed
- Whether partial state needs rollback

Write this as a table, then implement with those failure modes handled."
```

Models default to the happy path. This makes failure paths a first-class requirement.

---

## 7. Test-Driven Prompt Inversion

Instead of "write code, then tests," flip it:

```
"Write the test cases first. Include:
- Normal cases
- Boundary values
- Failure/error cases
- Concurrent/race conditions if applicable

Don't implement the function yet. I will review the tests and confirm
they cover my intent before you write any implementation."
```

The test cases reveal misunderstood requirements before any code is written.

---

## 8. Incremental Verification Checkpoints

For long implementations, insert explicit verification gates.

```
"Implement this in phases. After each phase, stop and output:
✓ What was implemented
✓ Assumptions made
✓ What is NOT yet handled
✓ Any design decisions where you chose between alternatives

Wait for my approval before proceeding to the next phase."
```

Without checkpoints, the model silently makes decisions that compound into large diffs that are hard to review.

---

## 9. Antipattern Blacklisting

Explicitly ban known AI-generated antipatterns for your stack.

```
"Do not use:
- panic() for recoverable errors
- interface{} where a typed struct is possible  
- goroutines without explicit lifecycle management
- string concatenation for SQL queries
- time.Sleep for synchronization
- global variables for request-scoped state

If you find yourself reaching for any of these, explain why and propose
an alternative before using them."
```

Models that know what to avoid produce better first drafts.

---

## 10. Schema and Contract Pinning

For APIs and data models, provide exact schemas.

```
"This function must accept exactly this input (do not add or remove fields):
{
  "user_id": "uuid",
  "amount_cents": "int64 > 0",
  "idempotency_key": "string, 1-128 chars"
}

And return exactly:
{
  "transaction_id": "uuid",
  "status": "enum: pending|completed|failed"
}

No additional fields. No field renaming. No type coercion."
```

Ambiguous schemas are a primary source of integration bugs.

---

## 11. The "Rubber Duck" Verification Pass

After getting an implementation, use a separate verification prompt.

```
"Here is a function I received. Do not explain what it does —
instead, trace through it with these specific inputs and tell me
the exact output and any side effects at each step:

Input 1: [normal case]
Input 2: [boundary case]
Input 3: [failure case]

If you cannot trace it with certainty, flag which parts are unclear."
```

This catches logical bugs that look correct syntactically.

---

## 12. Concurrency and State Prompt Patterns

Concurrency bugs are the hardest for models to get right. Use structured prompts.

```
"This code will run with N concurrent callers sharing [resource].
Before implementing:
1. Identify every shared mutable state
2. Identify every critical section
3. Specify the synchronization primitive for each critical section
4. Explain why deadlock cannot occur

Then implement with those protections in place."
```

---

## 13. Prompt Layering for Complex Systems

For multi-component systems, use a layered prompt strategy:

```
Layer 1 (Architecture):
"Design the component boundaries and contracts. No implementation."

Layer 2 (Data model):
"Define the data structures each component works with. No logic."

Layer 3 (Implementation):
"Implement [component X] using the contracts and data models above."

Layer 4 (Integration):
"Show how components X and Y connect at their boundary."
```

Each layer gates the next. This mirrors how experienced engineers actually design systems.

---

## 14. Explicitness Over Inference

Eliminate words that require inference: "appropriate," "reasonable," "standard," "typical," "best practice."

| Vague | Explicit |
|---|---|
| "Handle errors appropriately" | "Return error to caller, log at WARN with request ID, no retry" |
| "Use reasonable timeouts" | "5s for DB queries, 30s for external HTTP calls" |
| "Follow REST conventions" | "POST /resources returns 201 + Location header, 400 for validation errors, 409 for conflicts" |
| "Secure the endpoint" | "Require JWT in Authorization header, validate expiry and audience claim 'api.myservice.com'" |

---

## 15. Post-Generation Review Prompt

Always close with an adversarial review prompt on the generated code.

```
"Review the code you just wrote and answer:
1. What assumptions did you make that I haven't validated?
2. What inputs would cause incorrect behavior?
3. What would break under high concurrency?
4. What would break if [downstream service] returns an unexpected response?
5. What did you not implement that I might expect to be there?

Be specific. Do not give reassurances."
```

---

## Putting It Together: A Prompt Template

```
## Context
[Runtime, DB, framework, existing patterns]

## Task
[Single, specific function or component]

## Hard Constraints
[Numbered list — violations are bugs]

## Antipatterns to Avoid
[Stack-specific list]

## Success Criteria
[How I will know this is correct]

## Process
1. Enumerate edge cases and failure modes
2. Write test cases for review
3. Wait for approval
4. Implement with explicit phase checkpoints
5. Self-review against constraints
```

---

## Summary: The Five Meta-Principles

1. **Spec before code** — validate intent before generating implementation
2. **Explicit over inferred** — eliminate every word that allows silent assumption
3. **Checkpoint everything** — never let the model run past a decision point without review
4. **Failure paths are first-class** — demand them explicitly or they won't appear
5. **Adversarial review** — end every session with a prompt designed to break what was built

The biggest leverage is `spec → test → implement`, not `implement → fix → fix → fix`.