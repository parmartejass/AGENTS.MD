---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: hook patterns or automation expectations change
---

# 95 — Hooks and Automation Patterns

Goal: document common automation hooks that enforce quality gates and reduce manual verification overhead, while maintaining SSOT principles.

## Hook Types (Tool-Specific)

Different agent tools support different hook mechanisms. This doc describes **patterns**, not tool-specific configs.

| Hook Type | When Triggered | Common Use Cases |
|-----------|---------------|------------------|
| PreToolUse | Before tool executes | Validation, backups, confirmation gates |
| PostToolUse | After tool completes | Formatting, linting, diagnostics |
| UserPromptSubmit | On prompt submission | Context injection, rule reminders |
| Stop/Notification | On task completion | Sound alerts, webhooks, status updates |

## Recommended PostToolUse Patterns

### 1. Lint/Diagnostics After Edits

After any file edit (Edit, Write, MultiEdit tools), run linting/type-checking to catch issues immediately.

**Pattern:**
- Matcher: `Edit|Write|MultiEdit`
- Action: Run linter/type-checker on modified file(s)
- Rationale: Aligns with `AGENTS.md` verification-first philosophy; catches errors before they propagate

**Example (pseudo-config):**
```yaml
hook: PostToolUse
matcher: "Edit|Write|MultiEdit"
action: "run_diagnostics_on_modified_files"
```

### 2. Code Formatting After Edits

Auto-format code after edits to maintain consistent style without manual intervention.

**Pattern:**
- Matcher: `Edit|Write|MultiEdit`
- Action: Run formatter (e.g., Prettier, Black, rustfmt) on modified file(s)
- Rationale: Eliminates style drift; keeps diffs focused on logic changes

**Example (pseudo-config):**
```yaml
hook: PostToolUse
matcher: "Edit|Write|MultiEdit"
action: "npx prettier --write $FILE"
# Or: "black $FILE" for Python
```

### 3. Git Checkpoint After Task Completion

Commit changes at natural checkpoints to enable rollback and progress tracking.

**Pattern:**
- Matcher: `Task|Stop`
- Action: Stage and commit with descriptive message
- Rationale: Creates rollback points; enables "try, fail, revert" workflows

**Warning:** Do not auto-commit on every edit—only at logical task boundaries.

## Recommended PreToolUse Patterns

### 1. Backup Before Destructive Operations

Create backups before operations that could lose data.

**Pattern:**
- Matcher: `Delete|Write` (on critical files)
- Action: Copy file to backup location
- Rationale: Enables recovery from mistakes

### 2. "Always Works" Verification Gate

Before claiming a task is complete, enforce verification.

**Pattern:**
- Matcher: `Stop|TaskComplete`
- Action: Run verification script; block completion if it fails
- Rationale: Prevents "should work" claims; enforces deterministic proof

**Verification contract:**
> "Would you bet $100 this works?" — If no, verification is incomplete.

## Notification Patterns

### Task Completion Sound

Play a sound when long-running tasks complete.

**Pattern:**
- Matcher: `Stop|SubagentStop`
- Action: Play sound file
- Platform-specific: `afplay` (macOS), PowerShell `[System.Media.SystemSounds]` (Windows), `paplay` (Linux)

### Webhook on Completion

Notify external systems when tasks complete.

**Pattern:**
- Matcher: `Stop`
- Action: POST to webhook URL with task summary
- Use case: CI/CD integration, team notifications

## Integration with AGENTS.md

Hooks must **reinforce**, not replace, the Mandatory Execution Loop:

1. **Hooks cannot skip verification** — They automate checks, not bypass them.
2. **Hooks must not create SSOT violations** — Auto-formatting is fine; auto-generating duplicate configs is not.
3. **Hook failures should be explicit** — Log failures; do not silently continue.

## Anti-Patterns (Reject)

| Anti-Pattern | Problem |
|--------------|---------|
| Auto-commit on every edit | Creates noisy history; makes rollback harder |
| Skip verification if hook passes | Hooks catch some issues, not all; verification still required |
| Auto-generate code without review | Violates "verify, then trust" principle |
| Suppress hook errors | Violates explicit failure requirement |

## Checklist for Hook Configuration

- [ ] Hook action aligns with AGENTS.md principles
- [ ] Hook does not create duplicate SSOT owners
- [ ] Hook failures are logged and surfaced
- [ ] Hook does not auto-approve/skip verification steps
- [ ] Hook is documented in team/project setup guide
