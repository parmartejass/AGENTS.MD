---
doc_type: policy
ssot_owner: docs/agents/governance/security/security.md
update_trigger: secret handling, the redaction list, injection or transport rules, or permission boundaries change
---

# Security

Jurisdiction: secret handling, the redaction list, injection and transport safety, and permission boundaries for repo-owned assets.

## Baseline

```yaml
baseline:
  interface: the operating system's user-scoped credential store reached through its native credential API
  pattern: secret retrieved at point of use by service and account name; never persisted in process environment, config, fixtures, or logs
  reason: "the OS credential store encrypts at rest under the user's own key and is scoped to the user; it avoids environment inheritance into owned subprocesses, crash-dump capture, and plaintext files"
  exception: "a CI or headless runner without a user credential store uses the runner's managed secret injection for that run only; Record the boundary"
```

## Secrets

- Secrets MUST stay out of code, config, docs, prompts and fixtures.
- MUST retrieve secrets at runtime from the OS user-scoped credential store.
- The CI or headless-runner exception is the only case for process environment injection.
- Repo-owned assets and config JSON MUST contain no secrets.
- Machine-local secret files and machine-local overrides MUST stay untracked and user-owned.
- Only project-scoped, non-secret, intentionally shared assets are repo-owned.
- The canonical owner of a reusable asset MUST be a secret-free root.
- Secret scanning MUST run on staged changes before commit and over full history in the repository's checks.
- A leaked secret MUST be rotated at its issuer.
- Suppressing or allowlisting the finding MUST NOT count as remediation.

## Redaction

- MUST redact these by default: `token`, `password`, `secret`, `key`, `credential`, cookies, auth headers, emails, phone numbers, account IDs, full user-home paths.
- Default redaction applies to logs, reports, evidence, handoffs and tracked docs.
- Large payloads MUST be stored as a size, hash or path reference, not as raw dumps.
- MUST replace private absolute roots with `<governance-root>`, `<project-root>`, `{HOME}`, or relative-path evidence.
- Config mutation and failure records MUST redact sensitive key names and summarize large payloads.

## Injection and transport

- MUST avoid shell, SQL and template injection by passing untrusted values as data only.
- Prohibited: string concatenation of untrusted input into commands, queries or templates.
- MUST refuse security weakening, including disabling TLS validation, unless the user explicitly accepts the risk.
- An accepted weakening MUST stay confined to the safe environment the user named.
- Record the acceptance and the boundary.

## Permissions

- Repo-owned server and tool definitions MUST carry no implicit tool-execution permission.
- Tool permission scope is enforced by the consuming client runtime, not by the repo-owned definition.
- Session logs, transcripts and user-home files are local evidence.
- Reading them requires explicit user authorization of the root.
- Evidence scans of the home, a drive or the repo root MUST be explicitly authorized.
