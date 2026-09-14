---
doc_type: reference
ssot_owner: docs/agents/skills/x-api-data-access/SKILL.md
update_trigger: X response/limitation documentation routes or skill verification needs change
---

# X API Limitations and Gotchas

This reference supplies verification questions for the request contract in `docs/agents/skills/x-api-data-access/SKILL.md`. Current endpoint and account authorities supply the answers; this file defines no numeric quota, retention window, auth default, or retry schedule.

## Response and completeness evidence
Resolve from the exact route:
- default versus explicitly selectable fields and related-object expansion syntax;
- continuation tokens, per-page bounds, ordering, and collection limits;
- partial-error representation, empty-result meaning, and reconciliation of requested versus returned objects;
- resource visibility, account scope, retention, and plan conditions that affect completeness.

For a retrieval result, record page/item counts, continuation state, oldest returned timestamp when relevant, partial errors, and the terminal reason. A successful HTTP status or empty page is evidence to interpret through the response contract, not proof of complete retrieval.

## Common checks to verify

For each applicable question, capture the exact endpoint/account source, verification date, answer and unresolved implication in the skill Request contract. These are prompts, not current API facts:

- Search or message history: does the requested start date fall within the route retention window, and does the active account expose the requested historical operation?
- Bookmarks or other collections: are there per-page and total-history bounds; does continuation exhaustion prove completeness for this request?
- Profile/self, private messages, protected accounts or private lists: does the token represent the required user, and can visibility reduce the returned data?
- Missing authors/media or sparse payloads: which fields and expansions hydrate the required objects, and how are unresolved joins reported?
- Fewer items than expected: compare requested IDs, returned data, partial errors, collection bounds and visibility before claiming missing source data.
- Rate-limit or auth failure: which response headers and error fields explain the failure, and does the documented flow/scope match the exact read or write action?
- Spaces, trends or usage: is the requested historical/live/scheduled state or measurement window available, and what does its timestamp mean?

## Bounded execution evidence
Apply the skill's resolved workload and termination contract before collection. Long retrievals retain the continuation state needed for authorized recovery. Rate-limit responses and service failures use the owning retry contract; no fixed backoff or alternate endpoint is selected from this reference. When observed results differ from the requested scope, compare fields, expansions, authorization, retention, and plan evidence before attributing an API defect.

## Official discovery routes
- [Fields](https://docs.x.com/x-api/fundamentals/fields)
- [Pagination](https://docs.x.com/xdks/python/pagination)
- [Rate limits](https://docs.x.com/x-api/fundamentals/rate-limits)
- [Search](https://docs.x.com/x-api/posts/search/introduction)
- [Direct messages](https://docs.x.com/x-api/direct-messages/lookup/introduction)
- [Usage](https://docs.x.com/x-api/usage/introduction)

These are verification entrypoints. Missing or stale documentation remains an explicit resolution gap under the skill's source-authority contract.
