---
doc_type: playbook
ssot_owner: docs/agents/playbooks/config/config.md
update_trigger: config location, value ownership, or validated consumption rules change
---

# Config

Jurisdiction: where configurable values live and how consumers receive them.

```yaml
baseline:
  interface: "the standard-library JSON reader (the standard-library TOML reader for a hand-edited, read-only file) over one app-owned config file"
  pattern: "one owner validates the config file; consumers read only its validated values"
  reason: "the standard-library parser is the direct, dependency-free interface; a settings framework or a second validator creates a parallel validation authority"
  exception: "none without a recorded supersession"
```

- Repo-owned shared platform settings are outside this jurisdiction; they belong to the settings standard.
