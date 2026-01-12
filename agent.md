# Agent Best Practices

A comprehensive guide to working effectively with AI coding agents, based on [Cursor's best practices](https://cursor.com/blog/agent-best-practices).

## Table of Contents

- [Understanding Agent Harnesses](#understanding-agent-harnesses)
- [Start with Plans](#start-with-plans)
- [Managing Context](#managing-context)
- [Extending the Agent](#extending-the-agent)
- [Common Agent Tasks](#common-agent-tasks)
- [Reviewing Code](#reviewing-code)
- [Running Agents in Parallel](#running-agents-in-parallel)
- [Delegating to Cloud Agents](#delegating-to-cloud-agents)
- [Debug Mode](#debug-mode)
- [Developing Your Workflow](#developing-your-workflow)

---

## Understanding Agent Harnesses

An agent harness is built on three components:

| Component | Description |
|-----------|-------------|
| **Instructions** | The system prompt and rules that guide agent behavior |
| **Tools** | File editing, codebase search, terminal execution, and more |
| **User messages** | Your prompts and follow-ups that direct the work |

The harness matters because different models respond differently to the same prompts. Modern agent systems tune instructions and tools specifically for each frontier model.

---

## Start with Plans

**The most impactful change you can make is planning before coding.**

Research shows that experienced developers are more likely to plan before generating code. Planning forces clear thinking about what you're building and gives the agent concrete goals.

### Using Plan Mode

Toggle Plan Mode (Shift+Tab in Cursor) to have the agent:

1. Research your codebase to find relevant files
2. Ask clarifying questions about your requirements
3. Create a detailed implementation plan with file paths and code references
4. Wait for your approval before building

### Tips for Plans

- **Save plans** to `.cursor/plans/` for documentation and to resume interrupted work
- **Edit plans directly** to remove unnecessary steps, adjust approaches, or add context
- **Not every task needs a plan** — for quick changes, jump straight to the agent
- **Start over from a plan** if the agent builds something wrong; revert, refine the plan, and run again

---

## Managing Context

Your job becomes giving each agent the context it needs to complete its task.

### Let the Agent Find Context

- Don't manually tag every file in your prompt
- The agent has powerful search tools and pulls context on demand
- Keep prompts simple: if you know the exact file, tag it; if not, let the agent find it
- Including irrelevant files can confuse the agent about what's important

### When to Start a New Conversation

**Start fresh when:**
- Moving to a different task or feature
- The agent seems confused or keeps making the same mistakes
- You've finished one logical unit of work

**Continue the conversation when:**
- Iterating on the same feature
- The agent needs context from earlier in the discussion
- Debugging something it just built

> ⚠️ Long conversations can cause the agent to lose focus. After many turns and summarizations, context accumulates noise. If effectiveness decreases, start a new conversation.

### Reference Past Work

Use `@Past Chats` to reference previous work rather than copy-pasting entire conversations. The agent can selectively read chat history to pull in only needed context.

---

## Extending the Agent

### Rules: Static Context for Your Project

Rules provide persistent instructions that shape how the agent works with your code. Create rules as folders in `.cursor/rules/` containing a `RULE.md` file:

```markdown
# Commands
- `npm run build`: Build the project
- `npm run typecheck`: Run the typechecker
- `npm run test`: Run tests (prefer single test files for speed)

# Code style
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports when possible: `import { foo } from 'bar'`
- See `components/Button.tsx` for canonical component structure

# Workflow
- Always typecheck after making a series of code changes
- API routes go in `app/api/` following existing patterns
```

### What to Include in Rules

✅ **Do include:**
- Commands to run
- Patterns to follow
- Pointers to canonical examples in your codebase

❌ **Avoid:**
- Copying entire style guides (use a linter instead)
- Documenting every possible command
- Instructions for edge cases that rarely apply

> 💡 **Tip:** Start simple. Add rules only when you notice the agent making the same mistake repeatedly.

### Skills: Dynamic Capabilities

Skills give the agent additional capabilities it can use when relevant. Unlike rules, skills are activated based on context.

---

## Common Agent Tasks

### Test-Driven Development

Agents excel when they have a clear target to iterate against. Use this workflow:

1. **Describe what you want to build** and ask the agent to write tests (even if the code doesn't exist yet)
2. **Tell the agent to run tests and confirm they fail** — no implementation code yet
3. **Commit the tests** when satisfied
4. **Ask the agent to write code that passes the tests** — don't modify the tests
5. **Commit the implementation** once all tests pass

### Codebase Understanding

Use the agent for learning and exploration. Ask questions like:

- "How does logging work in this project?"
- "How do I add a new API endpoint?"
- "What edge cases does `CustomerOnboardingFlow` handle?"
- "Why are we calling `setUser()` instead of `createUser()` on line 1738?"

This is one of the fastest ways to ramp up on unfamiliar code.

### Git Workflows

Agents can search git history, resolve merge conflicts, and automate workflows.

**Example `/pr` command:**

```markdown
Create a pull request for the current changes.

1. Look at the staged and unstaged changes with `git diff`
2. Write a clear commit message based on what changed
3. Commit and push to the current branch
4. Use `gh pr create` to open a pull request with title/description
5. Return the PR URL when done
```

**Other useful commands:**
- `/fix-issue [number]`: Fetch issue details, find relevant code, implement a fix, open a PR
- `/review`: Run linters, check for common issues, summarize what needs attention
- `/update-deps`: Check for outdated dependencies and update them one by one, running tests after each

Store commands as Markdown files in `.cursor/commands/` and check them into git for your whole team.

---

## Reviewing Code

AI-generated code needs review.

### During Generation

- Watch the agent work in the diff view
- If heading in the wrong direction, press **Escape** to interrupt and redirect

### Agent Review

- Click **Review** → **Find Issues** for a dedicated review pass
- The agent analyzes proposed edits line-by-line and flags potential problems
- Use Agent Review in Source Control tab to compare against your main branch

### Architecture Diagrams

For significant changes, ask the agent to generate diagrams:

> "Create a Mermaid diagram showing the data flow for our authentication system, including OAuth providers, session management, and token refresh."

Diagrams are useful for documentation and can reveal architectural issues before code review.

---

## Running Agents in Parallel

### Native Worktree Support

Each agent can run in its own git worktree with isolated files and changes:

- Agents can edit, build, and test code without stepping on each other
- Select the worktree option from the agent dropdown
- Click **Apply** to merge changes back to your working branch

### Run Multiple Models at Once

Run the same prompt across multiple models simultaneously:

- Compare results side by side
- The system can suggest which solution is best
- Especially useful for:
  - Hard problems where different models might take different approaches
  - Comparing code quality across model families
  - Finding edge cases one model might miss

> 💡 **Tip:** Configure notifications and sounds to know when parallel agents finish.

---

## Delegating to Cloud Agents

Cloud agents work well for tasks you'd otherwise add to a todo list:

- Bug fixes that came up while working on something else
- Refactors of recent code changes
- Generating tests for existing code
- Documentation updates

### How Cloud Agents Work

1. Describe the task and any relevant context
2. The agent clones your repo and creates a branch
3. It works autonomously, opening a pull request when finished
4. You get notified when it's done (Slack, email, or web)
5. Review the changes and merge when ready

Cloud agents run in remote sandboxes — you can close your laptop and check results later.

---

## Debug Mode

For tricky bugs, Debug Mode provides a different approach:

1. **Generates multiple hypotheses** about what could be wrong
2. **Instruments your code** with logging statements
3. **Asks you to reproduce the bug** while collecting runtime data
4. **Analyzes actual behavior** to pinpoint the root cause
5. **Makes targeted fixes** based on evidence

### Best For

- Bugs you can reproduce but can't figure out
- Race conditions and timing issues
- Performance problems and memory leaks
- Regressions where something used to work

> 💡 **Tip:** Provide detailed context about how to reproduce the issue. The more specific you are, the more useful instrumentation the agent adds.

---

## Developing Your Workflow

Developers who get the most from agents share these traits:

### 1. Write Specific Prompts

The agent's success rate improves significantly with specific instructions.

| ❌ Vague | ✅ Specific |
|---------|------------|
| "add tests for auth.ts" | "Write a test case for auth.ts covering the logout edge case, using the patterns in `__tests__/` and avoiding mocks." |

### 2. Iterate on Your Setup

- Start simple
- Add rules only when the agent makes the same mistake repeatedly
- Add commands after you've figured out workflows you want to repeat
- Don't over-optimize before you understand your patterns

### 3. Review Carefully

- AI-generated code can look right while being subtly wrong
- Read the diffs carefully
- The faster the agent works, the more important your review process becomes

### 4. Provide Verifiable Goals

Agents can't fix what they don't know about:

- Use typed languages
- Configure linters
- Write tests
- Give the agent clear signals for whether changes are correct

### 5. Treat Agents as Capable Collaborators

- Ask for plans
- Request explanations
- Push back on approaches you don't like

---

## Summary

| Principle | Action |
|-----------|--------|
| **Plan first** | Use Plan Mode for complex tasks |
| **Trust the search** | Let agents find context on their own |
| **Keep conversations focused** | Start fresh when switching tasks |
| **Extend thoughtfully** | Add rules only for repeated mistakes |
| **Review everything** | AI code can be subtly wrong |
| **Parallelize** | Run multiple agents/models for hard problems |
| **Delegate** | Use cloud agents for background tasks |
| **Be specific** | Detailed prompts get better results |

---

*This guide is based on [Cursor's Best Practices for Coding with Agents](https://cursor.com/blog/agent-best-practices).*
