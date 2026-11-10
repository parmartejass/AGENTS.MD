---
doc_type: reference
ssot_owner: docs/agents/governance/skills/x-api-data-access/SKILL.md
update_trigger: X response or limitation documentation routes change
---

# X API Limitations and Gotchas

- Related objects are returned only for explicitly requested fields and expansions.
- Search and message history are bounded by route retention windows and plan access.
- Collections can have per-page and total-history bounds; continuation exhaustion alone does not prove completeness.
- Protected accounts, private lists, and visibility can reduce returned data.
- An empty page is not proof of absent data.

## Official routes
- [Fields](https://docs.x.com/x-api/fundamentals/fields)
- [Pagination](https://docs.x.com/xdks/python/pagination)
- [Rate limits](https://docs.x.com/x-api/fundamentals/rate-limits)
- [Search](https://docs.x.com/x-api/posts/search/introduction)
- [Direct messages](https://docs.x.com/x-api/direct-messages/lookup/introduction)
- [Usage](https://docs.x.com/x-api/usage/introduction)
