---
name: x-api-data-access
description: Plan and execute X API retrieval and integration tasks using the official X API docs. Use when the agent needs to determine what X data can be read or managed, map needs like posts, profiles, timelines, bookmarks, likes, follows, lists, spaces, direct messages, trends, usage, or media to the right endpoints, choose auth flows and scopes, and account for fields, expansions, pagination, retention windows, rate limits, or plan limits.
---

# X API Data Access

## Overview

Use this skill to turn a vague X data request into a correct retrieval plan before writing code or calling the API. Keep `SKILL.md` focused on workflow; load the reference files when you need endpoint coverage, auth details, or limitation checks.

## Workflow

1. Classify the request before choosing endpoints.
   - Public read: profile lookup, public posts, search, public timelines, spaces, trends.
   - User-private read: bookmarks, `/users/me`, direct messages, and account-scoped list/follow or moderation views.
   - Write/manage: posting, liking, bookmarking, following, list management, media upload.
   - Usage/analytics: API usage counters or plan monitoring.

2. Pick the auth model before drafting requests.
   - Use app-only bearer auth for public-read endpoints when the docs explicitly allow it.
   - Use OAuth 2.0 Authorization Code with PKCE for user-context reads or writes that require scopes.
   - Use OAuth 1.0a only when an endpoint still documents it as required or supported.
   - Check the official auth mapping first, then read [references/auth-and-scopes.md](references/auth-and-scopes.md) before assuming bookmarks, likes, follows, lists, or DMs will work with app-only auth.

3. Map the user need to a capability family.
   - Read [references/capabilities.md](references/capabilities.md) for the fastest route from "I need X data" to endpoint families, auth expectations, and official docs.

4. Shape the request correctly.
   - Request only the fields you need.
   - Add `expansions` plus the matching `user.fields`, `media.fields`, `poll.fields`, `place.fields`, or `list.fields` needed to hydrate included objects.
   - Set `max_results` deliberately and loop on `next_token`.
   - Keep retries bounded and inspect rate-limit headers instead of hammering the endpoint.

5. Check limitations before implementing.
   - Search windows, DM retention, private-data rules, plan gating, and usage caps change outcomes materially.
   - Read [references/limitations-and-gotchas.md](references/limitations-and-gotchas.md) before claiming an endpoint can return data you have not verified.

## Fast Routing

- Need posts by ID, quotes, replies, reposts, search, timelines, or bookmarks: start with [references/capabilities.md](references/capabilities.md).
- Need to know whether app-only auth is enough: start with [references/auth-and-scopes.md](references/auth-and-scopes.md).
- Need to know why an endpoint is failing or returning less data than expected: start with [references/limitations-and-gotchas.md](references/limitations-and-gotchas.md).

## Operating Rules

- Treat `docs.x.com` as the authority for current endpoint coverage, auth support, plan availability, and rate-limit details.
- Do not guess scopes, field names, or endpoint families from older Twitter/X API memory.
- Do not assume default responses contain `created_at`, entities, media, or user context; request fields explicitly.
- Do not log bearer tokens, refresh tokens, cookies, or full `Authorization` headers.
- Prefer bounded pagination and explicit stop conditions over open-ended crawls.
- Surface plan or retention limits before coding around them.

## References

- Official auth mapping: `https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping`
- [references/capabilities.md](references/capabilities.md)
- [references/auth-and-scopes.md](references/auth-and-scopes.md)
- [references/limitations-and-gotchas.md](references/limitations-and-gotchas.md)
