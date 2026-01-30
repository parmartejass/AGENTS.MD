Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, ask before doing any work.
- Follow the Mandatory Execution Loop and Context Injection Procedure.
- Do NOT edit `.governance/` from a parent repo. Propose governance changes only.

Task type: feature

Goal:
- Read the priority report at `{{PRIORITY_REPORT}}` and implement the top item.
- Use the latest learnings from `{{LEARNING_DOC}}`.

Acceptance criteria:
- The top priority item is implemented with a minimal, verifiable diff.
- Deterministic verification is run or explicit manual checks are provided.

Constraints:
- Minimal diff; no unrelated refactors.
- No new dependencies unless explicitly required by the task.

Verification:
- Run the tightest deterministic check available.
- If no tests exist, provide deterministic manual steps.

Output:
- List files changed and why.
- Summarize verification evidence.
- Call out open questions or unknowns.