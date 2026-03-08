---
doc_type: policy
ssot_owner: docs/agents/acp/00-acp-standards.md
update_trigger: ACP runtime mappings or supported asset shapes change
---

# ACP Standards (SSOT)

## Definition
- ACP-related reusable, non-secret assets may live under `docs/agents/acp/`.
- This folder is reserved so ACP artifacts can travel with the repo once a verified runtime mapping is adopted.

## Invariants
- Do not store secrets, bearer tokens, client secrets, or local machine identities here.
- Do not auto-link ACP assets until a verified runtime path and config contract are documented.
- When ACP support is added, update this file, `docs/agents/link_repo_assets.ps1`, and the docs index together.
