---
doc_type: reference
ssot_owner: docs/agents/skills/x-api-data-access/SKILL.md
update_trigger: official X documentation routes or skill discovery needs change
---

# X API Capability Discovery

This is a documentation entrypoint map for `docs/agents/skills/x-api-data-access/SKILL.md`, not an exhaustive supported-capability list. Current official endpoint and account contracts own availability, auth, fields, retention, and limits. A missing local entry requires discovery through [X documentation](https://docs.x.com/), not rejection based on this map.

## Requested-outcome examples

Use these non-exhaustive questions to locate the exact official route; they assert no current capability:

| Example request | Endpoint-discovery question | Evidence to capture in the skill Request contract |
|---|---|---|
| Retrieve posts already identified by IDs | Does lookup accept this identity set and expose the required related objects? | Method/route, ID bounds, fields, expansion joins and partial errors |
| Find discussion over a requested period | Does search cover the period and query, or is another explicitly supported historical operation required? | Verified time coverage, account access, query syntax and continuation contract |
| Export saved posts or inspect messages | Which account owns the resource, and which documented user-context flow permits the requested read? | Account scope, auth mapping, visibility and completeness conditions |
| Inspect a list, relationship or profile | Is this lookup, membership, timeline, public view or account-private state? | Exact resource/view and route-specific access evidence |
| Upload media or manage a resource | Which requested actions write externally, and what prerequisites does each official operation require? | Authorized side effects, operation order and errors |
| Inspect usage, trends or live resources | What metric, time window or resource state does the returned data actually represent? | Metric definition, coverage, timestamp and plan evidence |

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

A topic link does not prove the requested operation exists or is authorized. Resolve the exact method and route, auth and account contract, response shape, pagination, and limitations using the owning skill's request contract. Preserve the user's requested operation when a link is stale; discover its current authoritative route or report the unresolved outcome.
