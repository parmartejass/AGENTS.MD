# X API Capabilities

## Contents

- Posts and search
- Users and profiles
- Relationships and lists
- Spaces, trends, and communities
- Direct messages
- Media and usage
- Official docs index

## Posts and Search

- Post lookup
  - Use for single-post or multi-post retrieval, quote/repost/reply graph work, or fetching public post metadata.
  - Typical docs: post lookup and fields/expansions guides.
  - Auth: public-read flows often work with app-only auth; verify against the auth mapping for the exact route.
  - Caveats: default payloads are sparse; request `tweet.fields` plus `expansions`.

- User timelines
  - Use for authored posts, mentions, or timeline-style retrieval from a known user.
  - Docs: `https://docs.x.com/x-api/posts/timelines/introduction`
  - Auth: public user timelines can work with app-only auth; home/private views need user context where documented.
  - Caveats: timelines paginate with `next_token`; replies and reposts can change result shape if not filtered.

- Recent search
  - Use for keyword, hashtag, cashtag, URL, or author-based discovery across recent public posts.
  - Docs: `https://docs.x.com/x-api/posts/search/introduction`
  - Auth: public-read flow; check current plan support.
  - Caveats: recent search is a rolling seven-day window.

- Full-archive search
  - Use when the request needs older historical posts beyond the recent-search window.
  - Docs: `https://docs.x.com/x-api/posts/search/introduction`
  - Auth: public-read flow, but plan gated.
  - Caveats: full-archive search is not available on every plan.

- Bookmarks
  - Use to retrieve the authenticated user's saved posts.
  - Docs: `https://docs.x.com/x-api/posts/bookmarks/introduction`
  - Auth: user context only.
  - Scope highlights: `tweet.read`, `users.read`, `bookmark.read`.
  - Caveats: bookmarks are private; app-only auth will not work.

- Liked posts and liking users
  - Use to retrieve a user's liked posts or the users who liked a post.
  - Docs: `https://docs.x.com/x-api/posts/likes/introduction`
  - Auth: some public lookup routes are app-only compatible in the auth mapping, while authenticated-user or private-account access still needs user context and the route-specific scopes.
  - Scope highlights: `tweet.read`, `users.read`, `like.read` when the route docs require authenticated like-history access.
  - Caveats: docs note all-time liking-user retrieval with paginated limits on specific routes.

## Users and Profiles

- User lookup
  - Use for profile data by ID, username, or the authenticated user.
  - Docs: `https://docs.x.com/x-api/users/lookup/integrate`
  - Auth: public lookup routes support app-only auth; `/2/users/me` is user-context only.
  - Caveats: if you need `/users/me`, scopes and user context are mandatory.

- User-owned metadata
  - Use for the authenticated user's own profile-linked data or account-scoped flows.
  - Docs: user lookup plus auth mapping docs.
  - Auth: PKCE or other user-context flow.
  - Caveats: app-only auth is not a fallback for owner-only endpoints.

## Relationships and Lists

- Followers and following
  - Use for social graph reads such as who a user follows or who follows them.
  - Docs: `https://docs.x.com/x-api/users/follows/introduction`
  - Auth: public graph lookup routes can be app-only compatible, while authenticated-user or protected-account flows still need user context and the route-specific scopes.
  - Scope highlights: `users.read`, `follows.read` when the route docs require authenticated graph access.
  - Caveats: protected/private relationship data may not be available without the right user context.

- Blocks and mutes
  - Use for moderation-state reads or writes tied to the authenticated account.
  - Docs: `https://docs.x.com/x-api/users/blocks/introduction` and `https://docs.x.com/x-api/users/mutes/introduction`
  - Auth: user context.
  - Caveats: these are account-private actions, not general public graph reads, and the blocks docs note Enterprise-only availability for some block routes.

- Lists
  - Use for list lookup, members, followers, pinned lists, or list timelines.
  - Docs: `https://docs.x.com/x-api/lists/list-lookup/introduction`, `https://docs.x.com/x-api/lists/list-members/introduction`, `https://docs.x.com/x-api/lists/manage-lists/introduction`, and `https://docs.x.com/x-api/lists/pinned-lists/introduction`
  - Auth: mixed; public list lookup differs from private list/member actions, so verify per route.
  - Scope highlights: list reads and writes use list scopes in user-context flows.
  - Caveats: do not assume public list endpoints imply access to private list data.

## Spaces, Trends, and Communities

- Spaces
  - Use for space lookup, search, buyers, tweets, invited users, or live-state work.
  - Docs: `https://docs.x.com/x-api/spaces/introduction`
  - Auth: mostly public-read style plus `space.read` where documented.
  - Caveats: live state and participant-specific data can vary by route and scope.

- Trends
  - Use for current and historical trend exploration.
  - Docs: `https://docs.x.com/x-api/trends/introduction`
  - Auth: verify current availability and plan support from the docs.
  - Caveats: trend coverage is not a substitute for full post search.

- Communities
  - Use when the request is about community lookup, rules, moderators, or membership-related reads.
  - Docs: `https://docs.x.com/x-api/communities/lookup/introduction` and `https://docs.x.com/x-api/communities/search/introduction`
  - Auth: verify per route.
  - Caveats: community endpoints are separate from lists or spaces.

## Direct Messages

- DM events and conversation data
  - Use for message retrieval, DM event lookup, or DM conversation workflows.
  - Docs: `https://docs.x.com/x-api/direct-messages/lookup/introduction`
  - Auth: OAuth 2.0 Authorization Code with PKCE.
  - Scope highlights: `dm.read` and related user scopes.
  - Caveats: DM APIs are user-private and the docs note a last-30-days retrieval window for recent message history.

## Media and Usage

- Media upload
  - Use when the workflow must upload media before creating or managing posts.
  - Docs: `https://docs.x.com/x-api/media/quickstart/media-upload-chunked`
  - Auth: user-context write flow.
  - Scope highlights: `media.write`, often paired with `tweet.write`.
  - Caveats: media upload is not a read endpoint; it is a prerequisite for posting workflows.

- Usage tracking
  - Use to inspect monthly or rolling usage instead of guessing whether a plan cap was hit.
  - Docs: `https://docs.x.com/x-api/usage/introduction`
  - Auth: verify current auth support in the usage docs.
  - Caveats: plan and billing rules change; usage APIs are safer than stale pricing memory.

## Official Docs Index

- User lookup: `https://docs.x.com/x-api/users/lookup/integrate`
- Timelines: `https://docs.x.com/x-api/posts/timelines/introduction`
- Search: `https://docs.x.com/x-api/posts/search/introduction`
- Bookmarks: `https://docs.x.com/x-api/posts/bookmarks/introduction`
- Likes: `https://docs.x.com/x-api/posts/likes/introduction`
- Follows: `https://docs.x.com/x-api/users/follows/introduction`
- Lists lookup: `https://docs.x.com/x-api/lists/list-lookup/introduction`
- List members: `https://docs.x.com/x-api/lists/list-members/introduction`
- Manage lists: `https://docs.x.com/x-api/lists/manage-lists/introduction`
- Pinned lists: `https://docs.x.com/x-api/lists/pinned-lists/introduction`
- Spaces: `https://docs.x.com/x-api/spaces/introduction`
- Direct messages: `https://docs.x.com/x-api/direct-messages/lookup/introduction`
- Trends: `https://docs.x.com/x-api/trends/introduction`
- Media upload: `https://docs.x.com/x-api/media/quickstart/media-upload-chunked`
- Usage: `https://docs.x.com/x-api/usage/introduction`
- Communities lookup: `https://docs.x.com/x-api/communities/lookup/introduction`
- Communities search: `https://docs.x.com/x-api/communities/search/introduction`
