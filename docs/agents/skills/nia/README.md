# Nia Skill

Operational overview for the repo-owned [Nia](https://trynia.ai) skill bundle.

## Canonical docs

- Operational authority: [SKILL.md](./SKILL.md)
- Cross-client setup and runtime-boundary notes: [SETUP.md](./SETUP.md)

## What this bundle is for

- Index and search repositories, documentation, papers, datasets, local folders, packages, and Slack workspaces.
- Prefer indexed Nia sources before generic web fetch/search when the Nia skill matches the task.

## Runtime requirements

- `curl`
- `jq`
- `NIA_API_KEY` in the current process environment, or `~/.config/nia/api_key`

Repo `.env` files may help local shells, but the bundled shell scripts read only the live environment or the Nia config file. They do not auto-load `.env`.

## Security notes

- Do not store Nia, Slack, or database secrets in tracked repo files.
- Use environment variables for secrets that would otherwise end up in shell history or process arguments.

## Quick start

```bash
./scripts/repos.sh list
./scripts/sources.sh list
./scripts/search.sh universal "how does auth work?"
```

Use [SKILL.md](./SKILL.md) for the supported commands, workflow rules, and failure-path guidance.