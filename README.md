# AGENTS.MD

Master repository for best practices when working with AI coding agents.

## Purpose

This repository serves as a central hub for:
- Best practices for coding with AI agents
- Guidelines for prompting, context management, and workflow optimization
- Team-shareable rules, commands, and patterns

## What's Inside

### [`agent.md`](./agent.md)

A comprehensive guide covering:

- **Understanding Agent Harnesses** — How instructions, tools, and user messages work together
- **Start with Plans** — Using Plan Mode for complex tasks
- **Managing Context** — When to start new conversations and how to reference past work
- **Extending the Agent** — Creating rules and skills for your project
- **Common Agent Tasks** — Test-driven development, codebase understanding, git workflows
- **Reviewing Code** — Strategies for reviewing AI-generated code
- **Running Agents in Parallel** — Using worktrees and multiple models
- **Delegating to Cloud Agents** — Background task automation
- **Debug Mode** — Systematic debugging with instrumentation
- **Developing Your Workflow** — Key traits of effective agent users

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/parmartejass/AGENTS.MD.git
   ```

2. Read the [agent.md](./agent.md) guide to learn best practices

3. Apply these patterns in your own projects by:
   - Creating `.cursor/rules/` folders with `RULE.md` files
   - Adding `.cursor/commands/` for reusable workflows
   - Saving plans to `.cursor/plans/` for documentation

## Key Takeaways

| Principle | Action |
|-----------|--------|
| **Plan first** | Use Plan Mode for complex tasks |
| **Trust the search** | Let agents find context on their own |
| **Keep conversations focused** | Start fresh when switching tasks |
| **Extend thoughtfully** | Add rules only for repeated mistakes |
| **Review everything** | AI code can be subtly wrong |
| **Be specific** | Detailed prompts get better results |

## Contributing

Contributions are welcome! Please follow standard git workflows when making changes.

## References

- [Cursor's Best Practices for Coding with Agents](https://cursor.com/blog/agent-best-practices)
- [Cursor Documentation](https://cursor.com/docs)

## License

MIT
