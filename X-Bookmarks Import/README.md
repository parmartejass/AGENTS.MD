# X Bookmarks Import (local harness)

OAuth 2.0 PKCE helper to export your X (Twitter) bookmarks into `data/` (gitignored). SSOT for X API capability planning remains **`docs/agents/skills/x-api-data-access/`**; this folder does not ship a second copy of that bundle.

## Setup

1. Create a developer app and obtain OAuth 2.0 client ID and secret.
2. Set credentials (see repo root **`/.env.example`**): `X_CLIENT_ID`, `X_CLIENT_SECRET`. You can place `.env` in the repo root or in this folder (`x_runtime.load_env` loads the script directory).
3. Run:

```bash
cd "X-Bookmarks Import"
python3 fetch_bookmarks.py
```

First run opens a browser for authorization; tokens are stored in **`.x_token.json`** (gitignored) beside this README.

## Layout

- `fetch_bookmarks.py` — entrypoint (default: last 15 days of bookmarks).
- `x_bookmarks_auth.py`, `x_bookmarks_bookmarks.py`, `x_runtime.py` — auth, API, IO/logging helpers.
- `skills/x-research/`, `skills/governance-autoresearch/` — companion agent skills used with this workflow.
- `data/` — outputs only (ignored); do not commit.

For endpoint scopes and limits, follow the canonical skill references under `docs/agents/skills/x-api-data-access/`.
