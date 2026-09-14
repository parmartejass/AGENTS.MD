# X Bookmarks Import (local workflow)

OAuth 2.0 PKCE helper to export your X (Twitter) bookmarks into `data/` (gitignored). SSOT for X API capability planning remains **`docs/agents/skills/x-api-data-access/`**; this folder does not ship a second copy of that bundle.

## Setup

1. Create a developer app and obtain OAuth 2.0 client ID and secret.
2. Supply `X_CLIENT_ID` and `X_CLIENT_SECRET` as process environment variables or in an untracked `.env` in this workspace folder. `fetch_bookmarks.py` passes its script directory to `x_runtime.load_env`, which searches upward for the first `.env`; a repo-root `.env` is used only if no nearer file is found. Existing process variables take precedence and separate `.env` files are not merged. Credential values remain local.
3. Run:

```bash
cd "X-Bookmarks Import"
python3 fetch_bookmarks.py
```

First run opens a browser for authorization; tokens are stored in **`.x_token.json`** (gitignored) beside this README.

## Layout

- `fetch_bookmarks.py` — entrypoint; `DAYS_BACK`, `OUTPUT_DIR`, and `TOKEN_FILE` own the local lookback and output locations.
- `x_bookmarks_auth.py`, `x_bookmarks_bookmarks.py`, `x_runtime.py` — auth, API, IO/logging helpers.
- `skills/x-research/`, `skills/governance-autoresearch/` — workspace research interfaces; governance authority and lifecycle remain in repository-root `AGENTS.md` and `Orchestration.md`.
- `data/` — outputs only (ignored); do not commit.

For endpoint scopes and limits, follow the canonical skill references under `docs/agents/skills/x-api-data-access/`.
