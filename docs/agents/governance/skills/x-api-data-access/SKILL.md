---
name: x-api-data-access
description: Use for X API retrieval or integration, such as finding posts, exporting bookmarks, inspecting profiles or messages, or managing resources, when the task requires resolving authentication, request shape, pagination, and access limits through official endpoint contracts.
---

# X API Data Access

Translate the user's requested data or action into a verified X API contract.

## Source authority
Current `docs.x.com` endpoint documentation and the authenticated account's service contract own supported operations, auth flows, scopes, fields, pagination, retention, quotas, and plan access. Local references are discovery aids, not a capability catalog.

## Request contract
Before API execution, resolve:
- requested data or action, account/resource scope, and authorized side effects;
- exact endpoint and method, source URL, and verification date;
- supported auth flow and required scopes for that endpoint and account;
- requested fields, related-object expansion rules, and response/error shape;
- pagination parameters, continuation mechanism, workload bounds, and termination condition;
- applicable rate, retention, and plan constraints, with any unresolved access outcome.

Use the official [authentication mapping](https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping) to resolve auth support. A locally unlisted capability requires authoritative discovery; missing or conflicting contract evidence requires an explicit unsupported or unresolved outcome with correction guidance. It does not permit guessing or alternate auth execution.

## Reference routing
- [Capabilities](references/capabilities/capabilities_index.md): documentation entrypoints for discovering the requested operation.
- [Auth and scopes](references/auth-and-scopes/auth-and-scopes_index.md): official authentication routes.
- [Limitations and gotchas](references/limitations-and-gotchas/limitations-and-gotchas_index.md): response, pagination, and completeness facts.

## Completeness
HTTP success alone does not establish complete retrieval; verify returned data and errors against the resolved response contract.
