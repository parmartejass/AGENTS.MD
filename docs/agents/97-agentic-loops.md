---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: loop patterns, subagent strategies, or context management expectations change
---

# 97 — Agentic Loops and Parallel Execution

Goal: document patterns for iterative/looping tasks and parallel subagent execution, with guardrails to prevent infinite loops and context pollution.

## When to Use Loop Patterns

Use loops when:
- Processing multiple files with the same transformation
- Running build/test until errors are fixed
- Iterating through a checklist of independent tasks
- Batch-processing items from a list or directory

Do **not** use loops when:
- Tasks have complex interdependencies (use sequential execution)
- A single failure should halt all work (use fail-fast)
- Context accumulation will exceed limits (use fresh context per task)

## Loop Pattern Types

### 1. Iteration Loop (For-Each)

Process each item in a collection.

**Prompt pattern:**
```
Go through each file in <directory> and <action>.
For each file:
1. <step 1>
2. <step 2>
3. Verify <condition>
Report: file path, action taken, verification result.
```

**Example:**
```
Go through each *.py file in src/validators/ and add type hints.
For each file:
1. Read the file
2. Add type hints to function signatures
3. Run mypy on the file
Report: file path, functions updated, mypy result (pass/fail).
```

**Guardrails:**
- Define explicit scope (glob pattern, file list)
- Define verification per item
- Define what to do on item failure (skip + log, or halt)

### 2. Fix-Until-Pass Loop

Iterate until a condition is satisfied.

**Prompt pattern:**
```
Run <command> in a loop until <success condition>.
On each iteration:
1. Run <command>
2. If success: stop and report
3. If failure: <fix strategy>
4. Limit: <max iterations>
```

**Example:**
```
Run `npm run build` in a loop until it passes.
On each iteration:
1. Run the build
2. If success: stop and report
3. If failure: read the error, fix the indicated file
4. Limit: 10 iterations (then stop and report stuck)
```

**Guardrails (mandatory):**
- **Maximum iteration limit** — Prevent infinite loops
- **Distinct fix strategy** — Do not retry the same fix twice
- **Stuck-loop detection** — If same error repeats twice, invoke restart protocol (see `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md`)

### 3. Batch Processing Loop

Process items in batches to manage context size.

**Prompt pattern:**
```
Process <items> in batches of <N>.
For each batch:
1. Load batch items
2. <action>
3. Clear context / commit checkpoint
4. Continue to next batch
```

**Guardrails:**
- Checkpoint after each batch (commit, save state)
- Clear context between batches if context is large
- Track progress externally (file-based state)

## Subagent / Parallel Execution Patterns

### When to Use Subagents

- Independent tasks that can run in parallel
- Tasks requiring different "personalities" (reviewer, implementer)
- Large task decomposition with clear boundaries

### Parallel Subagent Pattern

**Prompt pattern:**
```
Use subagents to complete in parallel:
- Subagent A: <task A>
- Subagent B: <task B>
- Subagent C: <task C>

Coordination:
- Each subagent works independently
- Results are merged after all complete
- Conflicts are resolved by <strategy>
```

**Guardrails:**
- Subagents must not edit the same files (causes conflicts)
- Define merge/conflict resolution strategy upfront
- Each subagent follows AGENTS.md independently

### Specialized Personality Subagents

**Use cases:**
- Code reviewer (critical, finds issues)
- Implementer (builds features)
- Tester (writes and runs tests)
- Documenter (updates docs)

**Pattern:**
```
Spawn a reviewer subagent with critical personality.
Task: Review <files> for <criteria>.
Output: List of issues with severity and location.
```

**Guardrails:**
- Reviewer subagent should not auto-fix (separation of concerns)
- Implementer should address reviewer findings explicitly

## Context Management

### When to Clear Context

Clear context (start fresh) when:
- Switching to an unrelated task
- Context has accumulated errors/confusion
- Previous task is fully complete and verified
- Context size approaches limits

**Signal phrases:**
```
/clear  (tool-specific)
Start a fresh context for the next task.
```

### Fresh Context Per Task Strategy

For large projects, process each task with fresh context:

1. Break project into independent task specs
2. For each task:
   - Start fresh context
   - Load only relevant files/docs
   - Implement and verify
   - Commit checkpoint
3. Final integration pass with fresh context

**Rationale:** Prevents context pollution; each task gets full attention without accumulated confusion.

## File-Based State Tracking

For multi-step or multi-session workflows, track state in files.

### Task Status File

```yaml
# .agent-state/tasks.yaml
tasks:
  - id: task-001
    description: "Add type hints to validators"
    status: completed  # pending | in_progress | completed | blocked
    verification: "mypy src/validators/ passed"
  - id: task-002
    description: "Update logging to structured format"
    status: in_progress
    verification: null
```

### Lookup Table for Cross-Task Context

```yaml
# .agent-state/lookup.yaml
constants:
  sheet_name_ssot: "src/constants.py::SHEET_NAMES"
  config_ssot: "src/config.py::AppConfig"
decisions:
  - date: "2026-01-15"
    decision: "Use pydantic for config validation"
    rationale: "Type safety, existing team familiarity"
blockers:
  - id: blocker-001
    description: "API rate limit on external service"
    status: unresolved
```

**Guardrails:**
- State files are operational; they do not replace SSOT
- State files should be `.gitignore`d or cleaned before merge
- Reference SSOT owners by path, not by duplicating values

## Operational Warnings

### Large Files Cause Loops

Files exceeding ~10k lines often cause context overflow and stuck loops.

**Prevention:**
- Before processing, check file size
- If large: split into logical chunks first
- Specify in prompt: "If any file exceeds 500 lines, split it before processing"

### Manual Approval Checkpoints

For critical tasks, insert manual approval gates:

```
After completing <phase>, pause and summarize:
- What was done
- Verification results
- Proposed next steps

Wait for explicit approval before continuing.
```

### Costs and Timeboxing

Agentic loops consume tokens. For cost-sensitive environments:
- Set iteration limits
- Set token/cost budgets
- Checkpoint frequently to enable resume

## Integration with Existing Docs

| Scenario | Reference |
|----------|-----------|
| Loop fails with same error twice | `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md` |
| Need verification commands | `docs/agents/05-context-retrieval.md` |
| Task involves workflows | `docs/agents/workflow-registry.md` |
| Task involves GUI threading | `docs/agents/60-gui-threading.md` |
| Final release check | `docs/agents/90-release-checklist.md` |

## Checklist Before Starting Agentic Loop

- [ ] Scope is bounded (file list, max iterations, etc.)
- [ ] Verification defined for each iteration/task
- [ ] Failure strategy defined (skip + log, or halt)
- [ ] Stuck-loop detection enabled (same failure twice → restart)
- [ ] Checkpoint/commit strategy defined
- [ ] Context clear strategy defined (if long-running)
- [ ] Subagent file ownership is non-overlapping (if parallel)
