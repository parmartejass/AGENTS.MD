---
doc_type: policy
ssot_owner: docs/agents/governance/security/security.md
update_trigger: secret handling, redaction, injection or transport rules, or permission boundaries change
---

# Security

Jurisdiction: secret handling, redaction, injection and transport safety, and permission boundaries for repo-owned assets.

## Baseline

```yaml
baseline:
  interface: the operating system's user-scoped credential store reached through its native credential API
  pattern: secret retrieved at point of use by service and account name; never persisted in process environment, config, fixtures, or logs
  reason: "the OS credential store encrypts at rest under the user's own key and is scoped to the user; it avoids environment inheritance into owned subprocesses, crash-dump capture, and plaintext files"
  exception: "a CI or headless runner without a user credential store uses the runner's managed secret injection for that run only; Record the boundary"
```

## Rules

- MUST NOT hardcode secrets in code, config, docs, prompts, fixtures, or repo-owned assets.
- Machine-local secret files and overrides MUST stay untracked and user-owned.
- Committed history MUST be verifiably secret-free.
- A leaked secret MUST be rotated at its issuer; suppressing the finding is not remediation.
- MUST redact secrets and personal data in every log, report, evidence, handoff, tracked fixture, and tracked doc.
- Untrusted values MUST be passed as data, never as executable shell, SQL, or template text.
- Security weakening, including disabled TLS validation, MUST NOT occur without explicit user risk acceptance, confined to and recorded with the environment the user named.
- Repo-owned server and tool definitions MUST NOT grant implicit tool-execution permission; the consuming client runtime enforces permission scope.
- Reading session logs, transcripts, or user-home files MUST NOT occur without explicit user authorization of the root.
