# Reviewing AI-Generated Code Before Merging to Production

**Audience:** Engineers reviewing PRs that contain AI-assisted code
**Why this matters:** AI tools generate plausible-looking code that can contain subtle bugs, security issues, and architectural drift that bypass normal pattern recognition during review.

---

## Treat It Like Code from a Junior Engineer You've Never Met

AI-generated code is often syntactically correct and stylistically confident, which creates a false sense of reliability. Approach it with more skepticism than usual, not less.

---

## Before You Start

- **Ask the author:** What prompt(s) were used? Was output accepted verbatim or edited? Which tool?
- **Check the diff scope:** AI often generates more code than necessary. Flag anything not required by the ticket.

---

## What to Verify

**Correctness**
- Trace the logic manually for at least one non-trivial path. Don't trust that it "looks right."
- Check edge cases explicitly: empty inputs, nulls, off-by-one, concurrent access.
- Verify return values and error paths are actually handled, not just silently swallowed.

**Security**
- Look for injection vectors: SQL, shell, HTML, path traversal. AI frequently inlines user input unsafely.
- Check authentication and authorization logic carefully — AI tends to implement the happy path and skip enforcement.
- Flag any hardcoded secrets, tokens, or credentials (AI sometimes inserts placeholder values that look real).

**Dependencies and imports**
- Verify every imported package exists, is already in the project, and is the expected version.
- Watch for hallucinated method names on real libraries (e.g., `sdk.doTheThing()` that doesn't exist).

**Tests**
- AI-generated tests frequently assert that the code does what it does, not that it does what it should.
- Check that tests would actually fail if the logic were broken.
- Verify test data is realistic and covers failure modes.

**Architecture and ownership**
- Does the code follow existing patterns in the codebase, or introduce a new approach without justification?
- Are responsibilities placed in the right layer? AI often puts business logic in the wrong abstraction.
- Does it handle cleanup, resource release, and lifecycle correctly?

---

## Red Flags That Warrant a Full Rewrite

- Logic that is technically functional but unexplainable by the author
- Comments that describe code that doesn't match what the code actually does
- Duplicated logic that already exists elsewhere in the codebase
- Error handling that logs and continues where it should fail loudly
- Overly general solutions to a specific problem (unnecessary abstraction, unused parameters)

---

## Approval Checklist

- [ ] Author can explain every non-trivial block of logic
- [ ] Security-sensitive paths reviewed line by line
- [ ] All imports and external calls verified to exist and behave as expected
- [ ] Tests would catch a regression if logic changed
- [ ] No scope creep beyond what the ticket required

---

## A Note on Velocity

Reviewing AI code thoroughly often takes longer than reviewing hand-written code of the same size. Budget for this. A fast merge of confidently wrong code costs more than a slow review.