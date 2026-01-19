---
name: Claude/Ralph Learnings Implementation
overview: Analyze d4m1n's learnings from Claude Code and Ralph experiments, categorize by implementability, and enhance the AGENTS.MD governance pack with applicable patterns.
todos:
  - id: create-hooks-automation-doc
    content: Create docs/agents/95-hooks-automation.md for PostToolUse/PreToolUse patterns
    status: pending
  - id: create-custom-commands-doc
    content: Create docs/agents/96-custom-commands.md for slash command workflows
    status: pending
  - id: create-agentic-loops-doc
    content: Create docs/agents/97-agentic-loops.md for loop/subagent patterns
    status: pending
  - id: update-prompting-playbook
    content: Update ai-coding-prompt-template.md with thinking depth and loop prompts
    status: pending
  - id: add-rules-evolution-section
    content: Add self-improvement rules section to AGENTS.md
    status: pending
  - id: update-manifest-profiles
    content: Add agentic_task profile to agents-manifest.yaml
    status: pending
  - id: create-state-management-doc
    content: Create docs/agents/98-state-lookup-tables.md for context persistence
    status: pending
  - id: update-index
    content: Update docs/agents/index.md with new documents
    status: pending
---

# Claude/Ralph Learnings Implementation Plan

## Source Analysis

Learnings extracted from d4m1n's X posts, threads, and blog on Claude Code and Ralph experiments (January 2026).

---

## Category 1: Already Covered by This Repo

These patterns are already implemented in the AGENTS.MD governance pack:

| Learning | Current Coverage | Location |
|----------|-----------------|----------|
| "Force real testing: avoid 'should work'; always run, trigger, observe results" | Mandatory Execution Loop step 6: "Verify with deterministic tools" | `AGENTS.md` |
| "From first principles: Break down PRDs into atomic tasks with success criteria" | Mandatory Execution Loop steps 1-3 | `AGENTS.md` |
| "Verify each implementation; human in loop for decisions" | Prime Directive: "Verify, Then Trust" | `AGENTS.md` |
| "Essential rules: Code style preferences, Dependencies summary, Project structure" | Discovery Pass + Repo Discovery doc | `docs/agents/10-repo-discovery.md` |
| "Use AI to review AI: Critical personality for feedback" | Implicit in restart prompt template | `docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md` |
| "No internet in agents; rely on MCPs for docs" | Context injection procedure + semantic queries | `agents-manifest.yaml` |
| "Flag tasks as 'passed' only after success criteria met" | Verification-first philosophy throughout | `AGENTS.md` |
| "Break down large files" | Not explicit but follows SSOT/minimal diff principles | `AGENTS.md` |
| "Always include project summary in prompt loop" | Covered by context injection + restart prompts | `docs/agents/playbooks/ai-coding-prompt-template.md` |

---

## Category 2: Directly Implementable (New Docs/Patterns)

These learnings can be added as new supporting documents or profile additions:

### 2.1 Hooks/Automation Patterns (HIGH PRIORITY)

**Source learnings:**
- "Run mcp_ide_getDiagnostics after edits to check linting, types, encoding"
- "Add PostToolUse hook on Edit|Write|MultiEdit to run code formatter"
- "Add PostToolUse hook on Task|Bash to play sound on completion"
- "PreToolUse: Validation before tools (e.g., backups)"
- "PostToolUse: After tools (e.g., format on edits)"
- "Pre-tool verification: Run script to enforce 'Always Works' context"

**Implementation:** Create `docs/agents/95-hooks-automation.md`

**Content outline:**
- Hook types: PreToolUse, PostToolUse, UserPromptSubmit, Stop
- Common patterns: linting after edits, formatting, sound notifications
- Integration with verification philosophy
- Example configurations

---

### 2.2 Custom Commands/Workflows (HIGH PRIORITY)

**Source learnings:**
- "Create custom slash commands in .claude/commands/ as MD files"
- "Examples: Git workflows, debugging, analysis, refactoring, documentation"
- "Automate releases with /release: Analyze changes, bump version, update changelog"

**Implementation:** Create `docs/agents/96-custom-commands.md`

**Content outline:**
- Directory structure for command definitions
- Command file format (MD with workflow steps)
- Common command patterns: /release, /review, /debug, /refactor
- Integration with AGENTS.md execution loop
- Must reference SSOT owners (not duplicate logic)

---

### 2.3 Agentic Loop Patterns (HIGH PRIORITY)

**Source learnings:**
- "Use loops: 'Go through each file in X dir and refactor to Y lib'"
- "'Run build in loop until fix all type errors'"
- "Spawn subagents: 'Use subagents to complete task in parallel'"
- "Create custom subagents with /agents for personalities"
- "Handle complexity better with fresh context per task"
- "For full projects, break into specs; not one-go for production"

**Implementation:** Create `docs/agents/97-agentic-loops.md`

**Content outline:**
- Loop patterns: iteration loops, fix-until-pass loops
- Subagent patterns: parallel execution, specialized personalities
- Fresh context strategy (when to clear/restart)
- Breaking large projects into specs with checkpoints
- Integration with stuck-loop detection (`docs/agents/15-...`)

---

### 2.4 State Management / Lookup Tables (MEDIUM PRIORITY)

**Source learnings:**
- "Use text files for state and lookup table to maintain context"
- "Check and approve each task manually; don't skim"

**Implementation:** Create `docs/agents/98-state-lookup-tables.md`

**Content outline:**
- File-based state tracking (run_confirmation.xml pattern already exists)
- Lookup tables for cross-task context
- Task approval checkpoints
- Integration with workflow registry

---

### 2.5 Thinking Depth / Prompting Techniques (MEDIUM PRIORITY)

**Source learnings:**
- "Control thinking depth: 'think about it' < 'think harder' < 'ultrathink'"
- "Always Works philosophy: Test thoroughly, bet $100 it works, no assumptions"

**Implementation:** Update `docs/agents/playbooks/ai-coding-prompt-template.md`

**Additions:**
- Thinking depth keywords section
- "Always Works" verification contract
- Loop prompt patterns (already partially covered)

---

### 2.6 Self-Improvement Rules (MEDIUM PRIORITY)

**Source learnings:**
- "Self-improvement rule: Update rules on new patterns, bugs, feedback"
- "Evolve setup: Continuous rule updates from codebase patterns"
- "Generate rules: Prompt to analyze package.json for stack, src for structure"

**Implementation:** Add section to `AGENTS.md` or create `docs/agents/99-rule-evolution.md`

**Content outline:**
- When to update rules (new patterns, recurring bugs, feedback)
- How to update rules (propose, verify, commit)
- Bootstrapping rules from codebase analysis
- Must maintain SSOT (rules in one place)

---

### 2.7 Manifest Profile Addition

**Implementation:** Add `agentic_task` profile to `agents-manifest.yaml`

```yaml
agentic_task:
  detect:
    keywords:
      - "loop"
      - "iterate"
      - "parallel"
      - "subagent"
      - "batch"
      - "until"
      - "each file"
    code_patterns: []
    file_globs: []
  inject:
    - "docs/agents/97-agentic-loops.md"
    - "docs/agents/98-state-lookup-tables.md"
    - "docs/agents/15-stuck-in-loop-generate-fresh-restart-prompt.md"
```

---

## Category 3: Tool-Specific (Out of Scope for This Repo)

These learnings are specific to Claude Code or IDE integrations and cannot be directly implemented in a governance pack:

| Learning | Why Out of Scope |
|----------|-----------------|
| "Install Claude Code as an extension" | IDE/tool installation |
| "Keyboard shortcuts: CMD/CTRL + ESC, CMD/CTRL + L, etc." | Tool-specific keybindings |
| "Configure /config for auto-connect IDE" | Tool-specific config |
| "Use /init to bootstrap existing codebases" | Tool-specific command |
| "/resume to continue interrupted sessions" | Tool-specific command |
| "Drag and drop images into prompts" | Tool-specific feature |
| "Track usage with npx ccusage" | Tool-specific utility |
| "Add rules dynamically with # 'Rule text'" | Tool-specific syntax |
| "Nest Claude.md files for directory-specific rules" | Already supported via loader stubs |
| "Run claude -p for scripting in CI/CD" | Tool-specific CLI |
| "TaskMaster AI MCP" | External MCP configuration |
| "Playwright MCP" | External MCP configuration |
| "Context7 MCP" | External MCP configuration |
| "Bell sound on Stop with afplay" | Hook configuration (doc it, don't implement) |
| "Auto-format: npx prettier --write" | Hook configuration (doc it, don't implement) |
| "$200 Claude Max ~3-4 days looping with Opus 4.5" | Pricing/operational info |

**Note:** While these cannot be implemented, the hooks/commands docs can **reference** these patterns as examples.

---

## Category 4: Operational Learnings (Document as Warnings/Tips)

These are operational insights that should be documented as warnings or tips:

| Learning | Where to Document |
|----------|------------------|
| "Check and approve each task manually; don't skim" | `docs/agents/97-agentic-loops.md` |
| "Run in sandbox for safety" | `AGENTS.md` Security Baseline (already covers "safe environment") |
| "Issues: Large E2E files (e.g., 11k lines) cause loops; specify splitting" | `docs/agents/97-agentic-loops.md` |
| "AI good for tech demos; production needs steering" | `docs/agents/00-principles.md` |
| "Clear context with /clear after major tasks" | `docs/agents/97-agentic-loops.md` |

---

## Implementation Priority

### Phase 1 (Core - This PR)
1. `docs/agents/95-hooks-automation.md` - Document hook patterns
2. `docs/agents/97-agentic-loops.md` - Document loop/subagent patterns
3. Update `docs/agents/playbooks/ai-coding-prompt-template.md` - Add thinking depth, "Always Works"
4. Update `agents-manifest.yaml` - Add `agentic_task` profile

### Phase 2 (Enhancement)
5. `docs/agents/96-custom-commands.md` - Document slash command patterns
6. `docs/agents/98-state-lookup-tables.md` - Document state management

### Phase 3 (Evolution)
7. Add self-improvement rules section (location TBD)
8. Update `docs/agents/index.md` with all new docs

---

## Acceptance Criteria

- [ ] New docs follow SSOT header format (doc_type, ssot_owner, update_trigger)
- [ ] No duplication of rules/constants from AGENTS.md
- [ ] All new docs referenced in `docs/agents/index.md`
- [ ] All injected files in manifest exist and are valid
- [ ] Validation scripts pass: `check_docs_ssot.ps1`, `check_agents_manifest.ps1`

---

## Key Insights Summary

1. **Hooks are documentation, not implementation** - This repo documents patterns; actual hook configs are tool-specific.

2. **Loop patterns complement stuck-loop detection** - The existing restart prompt template handles failures; new docs cover intentional iteration.

3. **State management extends run_confirmation.xml** - The existing pattern in ai-coding-prompt-template.md can be generalized.

4. **Self-improvement must not violate SSOT** - Rule evolution must update the canonical location, not create parallel rules.

5. **"Always Works" is a verification contract** - This reinforces the existing "verify with deterministic tools" mandate.
