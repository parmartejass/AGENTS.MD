---
doc_type: reference
ssot_owner: docs/agents/governance/skills/x-api-data-access/SKILL.md
update_trigger: X authentication documentation routes or skill contract evidence requirements change
---

# X API Auth and Scopes

This reference supports the request contract in `docs/agents/governance/skills/x-api-data-access/SKILL.md`. The endpoint's current official authentication mapping owns supported auth methods and scopes; this file maintains no local scope bundles or endpoint-specific auth defaults.

## Authentication evidence
For the requested route, capture:
- supported application or user-context auth methods;
- account/resource visibility and authorization requirements;
- exact scope set required for the authorized operation;
- token lifetime, refresh or consent requirements when relevant;
- sanitized evidence that available credentials match the route contract.

Public visibility alone does not establish application-only support. An endpoint's existence does not establish access for the current account. Resolve both through the official route and account contract before execution. Authentication failures use the resolved workflow's failure/retry contract; they do not authorize a different auth method, repeated bad-token requests, or new consent scope.

Credential storage and redaction route to the host's secret owner and `AGENTS.md` Security Baseline. Evidence records auth method, endpoint, required scopes, and sanitized status without credential values.

## Official discovery routes
These links are entrypoints for verification, not assertions that every linked route or auth method remains available:
- [Authentication mapping](https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping)
- [Application-only authentication](https://docs.x.com/fundamentals/authentication/oauth-2-0/application-only)
- [Authorization code and scopes](https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code)
- [User lookup](https://docs.x.com/x-api/users/lookup/integrate)
- [Bookmarks](https://docs.x.com/x-api/posts/bookmarks/introduction)
- [Likes](https://docs.x.com/x-api/posts/likes/introduction)
- [Follows](https://docs.x.com/x-api/users/follows/introduction)
- [Direct messages](https://docs.x.com/x-api/direct-messages/lookup/introduction)
