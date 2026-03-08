# X API Limitations and Gotchas

## Contents

- Sparse defaults and expansions
- Pagination
- Rate limits and usage
- Retention windows and plan limits
- Private data and protected resources
- Reliability rules
- Official docs

## Sparse Defaults and Expansions

- Many X API routes return minimal default payloads.
- If you need timestamps, entities, conversation IDs, attachments, or included user/media objects, request them explicitly.
- `expansions` only point to related objects; you still need the matching `user.fields`, `media.fields`, `poll.fields`, `place.fields`, or `list.fields`.
- Do not invent nested field syntax; use the field names documented by the route and the fields guide.

## Pagination

- Treat `next_token` as the normal continuation mechanism for timelines, search, and many collection endpoints.
- Recent search `max_results` is bounded to 100 per page.
- Full-archive search `max_results` is bounded to 500 per page when the plan exposes the route.
- Bookmark retrieval is capped to the most recent 800 saved posts.
- Trends lookup caps `max_trends` at 50.
- Usage endpoints cap `days` at 90.
- Always set a page cap, item cap, or time-window stop condition before crawling.
- Persist progress for long runs instead of restarting from page one after failures.
- Successful empty pages can still happen; treat them as explicit outcomes, not parser bugs.

## Rate Limits and Usage

- Read the response headers before retrying:
  - `x-rate-limit-limit`
  - `x-rate-limit-remaining`
  - `x-rate-limit-reset`
- Back off until reset when `remaining` approaches zero.
- Use exponential backoff only for transient `429` or `5xx` responses, and keep retries bounded.
- Use the usage endpoints when you need to reason about plan consumption instead of relying on stale pricing or cap memory.

## Retention Windows and Plan Limits

- Recent search is a rolling seven-day window.
- Full-archive search requires a plan that exposes it.
- DM retrieval is documented around a last-30-days window for recent message history.
- Scheduled Spaces can only be created up to 14 days ahead.
- Ended Spaces are not available forever; re-check the live docs before depending on post-end retrieval.
- Some endpoint families and quotas vary by plan; re-check the official docs before promising availability.

## Private Data and Protected Resources

- Bookmarks are private to the authenticated user.
- `/users/me` is user-context only.
- DMs are user-private and require PKCE plus DM scopes.
- Relationship, list, or moderation endpoints can differ for public versus account-private views.
- Protected users or private resources can reduce what a route returns even when the endpoint itself exists.

## Reliability Rules

- Prefer official `docs.x.com` links over memory whenever endpoint names, scopes, or plan access matter.
- A `200 OK` response can still include populated `errors[]`; inspect both the top-level errors and returned data before treating the response as clean success.
- Fail fast on auth mismatches:
  - app-only token used against bookmarks or `/users/me`
  - missing `like.read`, `bookmark.read`, `follows.read`, or `dm.read`
  - write flow attempted with read-only scopes
- When a request returns less data than expected, check fields, expansions, scopes, and retention windows before assuming the API is broken.
- Keep page count, oldest item timestamp, and stop reason in logs for long-running pulls.

## Official Docs

- Fields guide: `https://docs.x.com/x-api/fundamentals/fields`
- Pagination guide: `https://docs.x.com/xdks/python/pagination`
- Rate limits fundamentals: `https://docs.x.com/x-api/fundamentals/rate-limits`
- Search introduction: `https://docs.x.com/x-api/posts/search/introduction`
- Direct messages introduction: `https://docs.x.com/x-api/direct-messages/lookup/introduction`
- Usage introduction: `https://docs.x.com/x-api/usage/introduction`
