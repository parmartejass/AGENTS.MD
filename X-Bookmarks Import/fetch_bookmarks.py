"""
X Bookmarks Fetcher - Last 15 days with full data.
OAuth 2.0 PKCE user context. Zero external dependencies.

First run: opens browser for one-time auth, saves token.
Subsequent runs: reuses saved token (auto-refreshes if expired).

Usage: python3 fetch_bookmarks.py
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from x_bookmarks_auth import AuthConfig, get_access_token
from x_bookmarks_bookmarks import enrich, fetch_bookmarks, fetch_current_user, save_bookmarks
from x_runtime import configure_logging, load_env


configure_logging()
logger = logging.getLogger(__name__)

DAYS_BACK = 15
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
TOKEN_FILE = SCRIPT_DIR / ".x_token.json"
REDIRECT_URI = "http://127.0.0.1:8765/callback"
SCOPES = "bookmark.read tweet.read users.read offline.access"

load_env(SCRIPT_DIR)
CLIENT_ID = os.environ.get("X_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("X_CLIENT_SECRET", "")


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("X_CLIENT_ID and X_CLIENT_SECRET are required in .env.")
        raise SystemExit(1)

    since = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    auth_config = AuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scopes=SCOPES,
        token_file=TOKEN_FILE,
    )

    token = get_access_token(auth_config)
    user_id, username = fetch_current_user(token)
    logger.info("Logged in as @%s (ID: %s)", username, user_id)

    tweets, users, media, ref_tweets, polls = fetch_bookmarks(user_id, token, since)
    if not tweets:
        logger.info("No bookmarks in the last %s days.", DAYS_BACK)
        return

    enriched = enrich(tweets, users, media, ref_tweets, polls)
    enriched.sort(key=lambda tweet: tweet.get("created_at", ""), reverse=True)
    save_bookmarks(OUTPUT_DIR, enriched, since, days_back=DAYS_BACK)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
