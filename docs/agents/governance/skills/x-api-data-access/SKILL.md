---
name: x-api-data-access
description: Use for X API retrieval or integration, such as finding posts, exporting bookmarks, inspecting profiles or messages, or managing resources, when the task requires resolving authentication, request shape, pagination, and access limits through official endpoint contracts.
---

# X API Data Access

Translate the user's requested data or action into a verified X API contract. For work in a governed repository, apply its resolved `AGENTS.md` and `Orchestration.md`; this skill supplies X-specific discovery and request mechanics only.

## Request classification examples
Examples include public-data research, account-scoped retrieval, resource management, and usage analysis. Classify the actual requested action and side effects; a subject name alone does not resolve access. "Export my bookmarks" raises account ownership and visibility questions, while "find discussion about this topic" raises search scope and time coverage.

Use the auth/scopes reference to evaluate documented app-only bearer, OAuth 2.0 Authorization Code with PKCE, or OAuth 1.0a support for the exact route. These are discovery cases, not permission to select a flow from memory. The capabilities reference owns outcome-to-discovery examples; the limitations reference owns completeness and failure-diagnosis prompts.

## Source authority
Current `docs.x.com` endpoint documentation and the authenticated account's service contract own supported operations, auth flows, scopes, fields, pagination, retention, quotas, and plan access. Local references are discovery aids, not an exhaustive capability catalog or a substitute for those authorities.

## Request contract
Before implementation or API execution, resolve and record:
- requested data or action, account/resource scope, and authorized side effects;
- exact endpoint and method, source URL, and verification date;
- supported auth flow and required scopes for that endpoint and account;
- requested fields, related-object expansion rules, and response/error shape;
- pagination parameters, continuation mechanism, workload bounds, and termination condition;
- applicable rate, retention, and plan constraints, with any unresolved access outcome.

Use the official [authentication mapping](https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping) to resolve auth support. A locally unlisted capability requires authoritative discovery; missing or conflicting contract evidence requires an explicit unsupported or unresolved outcome with correction guidance. It does not permit guessing or alternate auth execution.

## Reference routing
- [Capabilities](references/capabilities/capabilities_index.md): documentation entrypoints for discovering the requested operation.
- [Auth and scopes](references/auth-and-scopes/auth-and-scopes_index.md): evidence needed to resolve credentials and account scope.
- [Limitations and gotchas](references/limitations-and-gotchas/limitations-and-gotchas_index.md): response, pagination, completeness, and access verification.

## Execution evidence
Requests MUST consume the resolved endpoint contract. Collect page/item counts, continuation state, error details, and the stop reason needed to reconcile the requested work. HTTP success alone does not establish complete retrieval; verify returned data and errors against the resolved response contract.

Credential handling, retry authorization, resource bounds, and external-action authorization remain governed by the applicable host contract and `AGENTS.md`; this skill adds no permission or retry default. Verify one bounded authorized request and a relevant failure path when execution is in scope. When the task is planning only, report execution as unverified and retain the source-backed request contract as its evidence.
