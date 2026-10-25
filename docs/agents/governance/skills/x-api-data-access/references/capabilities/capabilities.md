---
doc_type: reference
ssot_owner: docs/agents/governance/skills/x-api-data-access/SKILL.md
update_trigger: official X documentation routes or skill discovery needs change
---

# X API Capability Discovery

This is a documentation entrypoint map for `docs/agents/governance/skills/x-api-data-access/SKILL.md`, not an exhaustive supported-capability list. Current official endpoint and account contracts own availability, auth, fields, retention, and limits. A missing local entry requires discovery through [X documentation](https://docs.x.com/), not rejection based on this map.

## Requested-outcome examples

Use these non-exhaustive questions to locate the exact official route. They assert no current capability:

| Example request | Endpoint-discovery question | Evidence to capture in the skill Request contract |
|---|---|---|
| Retrieve posts already identified by IDs | Does lookup accept these IDs and return the required related objects? | Method and route, ID bounds, fields, expansion joins, partial errors |
| Find discussion over a requested period | Does search cover the period and query, or does the request need another explicitly supported historical operation? | Verified time coverage, account access, query syntax, continuation contract |
| Export saved posts or inspect messages | Which account owns the resource? Which documented user-context flow permits the requested read? | Account scope, auth mapping, visibility and completeness conditions |
| Inspect a list, relationship or profile | Is this a lookup, membership, timeline, public view or account-private state? | Exact resource or view, route-specific access evidence |
| Upload media or manage a resource | Which requested actions write externally? What does each official operation need first? | Authorized side effects, operation order, errors |
| Inspect usage, trends or live resources | What metric, time window or resource state does the returned data represent? | Metric definition, coverage, timestamp, plan evidence |

## Discovery routes
| Requested subject | Official documentation entrypoints |
| --- | --- |
| Posts and search | [Search](https://docs.x.com/x-api/posts/search/introduction), [timelines](https://docs.x.com/x-api/posts/timelines/introduction), [fields](https://docs.x.com/x-api/fundamentals/fields) |
| Saved or liked posts | [Bookmarks](https://docs.x.com/x-api/posts/bookmarks/introduction), [likes](https://docs.x.com/x-api/posts/likes/introduction) |
| Profiles and relationships | [User lookup](https://docs.x.com/x-api/users/lookup/integrate), [follows](https://docs.x.com/x-api/users/follows/introduction), [blocks](https://docs.x.com/x-api/users/blocks/introduction), [mutes](https://docs.x.com/x-api/users/mutes/introduction) |
| Lists | [Lookup](https://docs.x.com/x-api/lists/list-lookup/introduction), [members](https://docs.x.com/x-api/lists/list-members/introduction), [management](https://docs.x.com/x-api/lists/manage-lists/introduction), [pinned lists](https://docs.x.com/x-api/lists/pinned-lists/introduction) |
| Spaces, trends, or communities | [Spaces](https://docs.x.com/x-api/spaces/introduction), [trends](https://docs.x.com/x-api/trends/introduction), [community lookup](https://docs.x.com/x-api/communities/lookup/introduction), [community search](https://docs.x.com/x-api/communities/search/introduction) |
| Direct messages | [Message lookup](https://docs.x.com/x-api/direct-messages/lookup/introduction) |
| Media or usage | [Media upload](https://docs.x.com/x-api/media/quickstart/media-upload-chunked), [usage](https://docs.x.com/x-api/usage/introduction) |

A topic link does not prove the requested operation exists or is authorized. Resolve the exact method and route, auth and account contract, response shape, pagination, and limitations using the owning skill's request contract. When a link is stale, preserve the user's requested operation. Discover its current authoritative route, or report the unresolved outcome.
