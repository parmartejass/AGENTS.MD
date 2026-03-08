# X API Auth and Scopes

## Contents

- Choose the auth model
- Common scope bundles
- Endpoint-specific auth rules
- Token-handling rules
- Official docs

## Choose the Auth Model

- App-only bearer auth
  - Use for public-read routes when the official docs explicitly allow application-only access.
  - Good fit for public profile lookup, public timelines, public post lookup, recent search, and public graph routes that the auth mapping marks as app-only compatible.
  - Do not use it as a fallback for bookmarks, `/users/me`, DMs, or other private account data.

- OAuth 2.0 Authorization Code with PKCE
  - Use for most user-context reads and writes.
  - Required whenever the endpoint needs account-private data or explicit scopes such as bookmarks, likes, follows, lists, DMs, or write actions.
  - Prefer this for modern user-context integrations.

- OAuth 1.0a user context
  - Use only when the official endpoint docs still require or explicitly support it for the specific route.
  - Do not assume OAuth 1.0a is required unless the docs say so.

## Common Scope Bundles

- Public read baseline
  - `tweet.read`
  - `users.read`

- Bookmarks
  - `tweet.read`
  - `users.read`
  - `bookmark.read`

- Likes
  - `tweet.read`
  - `users.read`
  - `like.read`

- Follows
  - `users.read`
  - `follows.read`

- Lists
  - `users.read`
  - `list.read`
  - add write scopes only if the workflow mutates lists

- Spaces
  - `space.read`
  - often paired with `users.read`

- Direct messages
  - `dm.read`
  - add `dm.write` only for send/manage workflows
  - pair with the user scopes required by the endpoint docs

- Posting and media
  - `tweet.write`
  - `media.write`
  - pair with read scopes if the workflow also verifies created content

- Long-lived user sessions
  - `offline.access`
  - use when refresh tokens are needed

## Endpoint-Specific Auth Rules

- Before locking auth, verify the exact route in the official auth mapping.

- `/2/users/me`
  - Always user context.
  - Use PKCE and `users.read`.

- Bookmarks
  - Always user context.
  - Use PKCE with `bookmark.read` plus the read baseline.

- User liked posts
  - Public `GET /2/users/:id/liked_tweets` is documented in the auth mapping with OAuth 2.0 App Only support.
  - Use PKCE with `like.read` when the workflow needs authenticated-user context, private access, or other user-scoped reads beyond the public route contract.

- Followers and following
  - Public `GET /2/users/:id/followers` and `GET /2/users/:id/following` are documented in the auth mapping with OAuth 2.0 App Only support.
  - Use PKCE with `follows.read` when the workflow needs authenticated-user context or route docs require user scopes.

- Direct messages
  - Use PKCE.
  - Do not attempt app-only auth.

- Media upload and posting
  - Treat as user-context write flows.
  - Use write scopes and verify whether OAuth 1.0a is still documented for the exact flow.

## Token-Handling Rules

- Store secrets in environment variables or a secret store, not in code or checked-in files.
- Never print bearer tokens, refresh tokens, OAuth client secrets, cookies, or full `Authorization` headers.
- When debugging auth, log only the auth method, endpoint, scopes, and sanitized status codes.
- Refresh or re-consent instead of repeatedly retrying a `401` with the same bad token.
- When you need user-private data, fail fast if the session is app-only rather than pretending the endpoint is broken.

## Official Docs

- Auth mapping: `https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping`
- App-only auth: `https://docs.x.com/fundamentals/authentication/oauth-2-0/application-only`
- OAuth 2.0 scopes: `https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code`
- User lookup integration: `https://docs.x.com/x-api/users/lookup/integrate`
- Bookmarks introduction: `https://docs.x.com/x-api/posts/bookmarks/introduction`
- Likes introduction: `https://docs.x.com/x-api/posts/likes/introduction`
- Follows introduction: `https://docs.x.com/x-api/users/follows/introduction`
- Direct messages introduction: `https://docs.x.com/x-api/direct-messages/lookup/introduction`
