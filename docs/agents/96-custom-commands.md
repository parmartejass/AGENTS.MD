---
doc_type: reference
ssot_owner: AGENTS.md
update_trigger: custom command patterns or workflow automation expectations change
---

# 96 — Custom Commands and Workflow Automation

Goal: document patterns for creating reusable command workflows that integrate with the AGENTS.md execution model.

## What Are Custom Commands?

Custom commands (slash commands) are predefined workflows stored as files. They provide:
- Consistent execution of common tasks
- Reusable prompt patterns
- Integration with verification and SSOT principles

## Directory Structure (Tool-Specific)

Different tools use different locations. Common patterns:

```
.claude/commands/          # Claude Code
.cursor/commands/          # Cursor
.agent-commands/           # Generic / portable
```

Each command is typically a Markdown file defining the workflow.

## Command File Format

### Basic Structure

```markdown
# Command: <name>

## Description
<what this command does>

## Prerequisites
- <required state/files/tools>

## Workflow Steps
1. <step 1>
2. <step 2>
...

## Verification
- <how to verify success>

## SSOT References
- <paths to authoritative sources this command uses>
```

### Example: /release Command

```markdown
# Command: release

## Description
Prepare and publish a release: analyze changes, bump version, update changelog, build, test, create GitHub release.

## Prerequisites
- Clean working tree (no uncommitted changes)
- On main/release branch
- CI passing

## Workflow Steps
1. Analyze commits since last tag
2. Determine version bump (major/minor/patch) based on conventional commits
3. Update version in package.json / pyproject.toml / version file
4. Update CHANGELOG.md with categorized changes
5. Run build command
6. Run test suite
7. Commit version bump and changelog
8. Create annotated git tag
9. Push tag to remote
10. Create GitHub release with changelog content

## Verification
- [ ] Version file updated correctly
- [ ] CHANGELOG.md has new section
- [ ] Tests pass
- [ ] Tag created and pushed
- [ ] GitHub release visible

## SSOT References
- Version: <path to version file>
- Changelog: CHANGELOG.md
- Build command: <path to build script or package.json>
```

### Example: /review Command

```markdown
# Command: review

## Description
Perform a critical code review of specified files or recent changes.

## Prerequisites
- Files to review are specified or diff is available

## Workflow Steps
1. Identify files in scope (specified or from git diff)
2. For each file:
   - Check for SSOT violations (duplicated constants, parallel implementations)
   - Check for logging violations (print statements, silent catches)
   - Check for resource safety issues
   - Check for security concerns
3. Compile findings with severity and location
4. Suggest fixes (do not auto-apply)

## Verification
- All findings documented with severity
- No false positives from misunderstanding context

## SSOT References
- Review criteria: AGENTS.md Non-Negotiables
- Logging rules: docs/agents/30-logging-errors.md
```

### Example: /debug Command

```markdown
# Command: debug

## Description
Systematic debugging of a reported issue.

## Prerequisites
- Error message or reproduction steps provided

## Workflow Steps
1. Reproduce the issue with exact steps
2. Capture error output / stack trace
3. Grep for error message in codebase
4. Read relevant source files (with context)
5. Identify root cause
6. Propose fix (minimal diff)
7. Verify fix resolves issue
8. Check for regressions (run related tests)

## Verification
- Issue no longer reproduces
- Related tests pass
- No new lint/type errors

## SSOT References
- Error handling: docs/agents/30-logging-errors.md
- Bugfix template: docs/agents/playbooks/bugfix-template.md
```

## Integration with AGENTS.md

Custom commands must follow the Mandatory Execution Loop:

1. **Goal/AC** — Command file defines these
2. **Discover** — Command may specify files to read; still consult manifest
3. **Decompose** — Command defines steps
4. **Ambiguity gate** — If command input is ambiguous, ask before proceeding
5. **Implement** — Follow command steps
6. **Verify** — Use command's verification criteria
7. **Report** — Output what was done

Commands do **not** bypass:
- Context injection procedure
- SSOT adoption rules
- Verification requirements

## Creating Project-Specific Commands

1. Identify repetitive workflows in your project
2. Document the workflow as a command file
3. Reference SSOT owners (do not duplicate values)
4. Include verification criteria
5. Place in appropriate commands directory

## Anti-Patterns (Reject)

| Anti-Pattern | Problem |
|--------------|---------|
| Command duplicates SSOT values | Creates drift risk; reference by path instead |
| Command skips verification | Violates AGENTS.md verification mandate |
| Command has no prerequisites check | May fail unexpectedly mid-workflow |
| Command auto-commits without verification | May commit broken code |

## Checklist for Custom Commands

- [ ] Command has clear description and prerequisites
- [ ] Steps follow logical order with dependencies noted
- [ ] Verification criteria are explicit and testable
- [ ] SSOT references point to paths, not duplicated content
- [ ] Command integrates with AGENTS.md execution loop
- [ ] Command is documented in project setup or README
