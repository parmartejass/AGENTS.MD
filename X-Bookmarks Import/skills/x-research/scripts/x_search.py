"""
X Research Tool — search recent tweets on any topic with full data.
Uses app-only bearer token (recent search, 7-day window).
Zero external dependencies.

Usage:
  python3 x_search.py "topic" [--days=7] [--limit=100] [--no-retweets] [--lang=en] [--emit=full|compact|json]

Reads X_BEARER_TOKEN from .env (walks up from script dir to find it).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


X_BOOKMARKS_ROOT = Path(__file__).resolve().parents[3]
if str(X_BOOKMARKS_ROOT) not in sys.path:
    sys.path.insert(0, str(X_BOOKMARKS_ROOT))

from x_runtime import (  # noqa: E402
    UsageError,
    configure_logging,
    load_env,
    parse_int_arg,
    parse_retry_delay_seconds,
    request_json,
    summarize_payload,
    write_json_stdout,
    write_stdout_line,
)


configure_logging()
logger = logging.getLogger(__name__)

load_env(Path(__file__).resolve().parent)
BEARER = os.environ.get("X_BEARER_TOKEN", "")
MAX_RATE_LIMIT_RETRIES = 2
EMIT_MODES = {"full", "compact", "json"}


def api_get(url: str, params: dict[str, str] | None = None):
    response = request_json(
        "GET",
        url,
        headers={"Authorization": f"Bearer {BEARER}"},
        params=params,
        context=f"GET {url}",
    )
    return response.status, response.data, response.headers


def parse_args():
    args = sys.argv[1:]
    opts = {"topic": "", "days": 7, "limit": 100, "no_retweets": False, "lang": "", "emit": "full"}
    positional = []
    for arg in args:
        if arg.startswith("--days="):
            opts["days"] = parse_int_arg(arg.split("=", 1)[1], flag_name="--days", minimum=1, maximum=7)
        elif arg.startswith("--limit="):
            opts["limit"] = parse_int_arg(arg.split("=", 1)[1], flag_name="--limit", minimum=1, maximum=1000)
        elif arg == "--no-retweets":
            opts["no_retweets"] = True
        elif arg.startswith("--lang="):
            opts["lang"] = arg.split("=", 1)[1]
        elif arg.startswith("--emit="):
            emit_mode = arg.split("=", 1)[1]
            if emit_mode not in EMIT_MODES:
                raise UsageError("--emit must be one of: full, compact, json.")
            opts["emit"] = emit_mode
        else:
            positional.append(arg)
    opts["topic"] = " ".join(positional)
    return opts


TWEET_FIELDS = "id,text,author_id,created_at,conversation_id,public_metrics,entities,referenced_tweets,attachments,lang,note_tweet,context_annotations"
EXPANSIONS = "author_id,referenced_tweets.id,attachments.media_keys"
USER_FIELDS = "id,name,username,description,public_metrics,verified,verified_type,profile_image_url,location"
MEDIA_FIELDS = "media_key,type,url,preview_image_url,alt_text,height,width,variants"


def search(topic, days, limit, no_retweets, lang):
    query = topic
    if no_retweets:
        query += " -is:retweet"
    if lang:
        query += f" lang:{lang}"

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "query": query,
        "max_results": str(min(limit, 100)),
        "start_time": since,
        "sort_order": "relevancy",
        "tweet.fields": TWEET_FIELDS,
        "expansions": EXPANSIONS,
        "user.fields": USER_FIELDS,
        "media.fields": MEDIA_FIELDS,
    }

    all_tweets = []
    users = {}
    media = {}
    ref_tweets = {}
    pag = None
    page = 0
    rate_limit_retries = 0

    while len(all_tweets) < limit:
        page += 1
        request_params = dict(params)
        request_params["max_results"] = str(max(10, min(limit - len(all_tweets), 100)))
        if pag:
            request_params["pagination_token"] = pag

        status, data, headers = api_get("https://api.x.com/2/tweets/search/recent", request_params)

        if status == 429:
            rate_limit_retries += 1
            if rate_limit_retries > MAX_RATE_LIMIT_RETRIES:
                raise RuntimeError("Search rate limit persisted after bounded retries.")
            delay = parse_retry_delay_seconds(headers, default_seconds=60)
            logger.warning(
                "Search rate limited; waiting %s seconds before retry %s/%s.",
                delay,
                rate_limit_retries,
                MAX_RATE_LIMIT_RETRIES,
            )
            time.sleep(delay)
            page -= 1
            continue

        rate_limit_retries = 0
        if status in {401, 403}:
            raise RuntimeError(f"Search authentication failed ({status}): {summarize_payload(data)}")
        if status != 200:
            raise RuntimeError(f"Search failed ({status}): {summarize_payload(data)}")

        if "data" not in data:
            break

        includes = data.get("includes", {})
        for user in includes.get("users", []):
            users[user["id"]] = user
        for media_item in includes.get("media", []):
            media[media_item["media_key"]] = media_item
        for tweet in includes.get("tweets", []):
            ref_tweets[tweet["id"]] = tweet

        all_tweets.extend(data["data"])
        logger.info("  Page %s: +%s tweets (total: %s)", page, len(data["data"]), len(all_tweets))

        pag = data.get("meta", {}).get("next_token")
        if not pag:
            break

    return all_tweets, users, media, ref_tweets


def score_tweet(tweet):
    metrics = tweet.get("public_metrics", {})
    likes = metrics.get("like_count", 0)
    retweets = metrics.get("retweet_count", 0)
    replies = metrics.get("reply_count", 0)
    quotes = metrics.get("quote_count", 0)
    bookmarks = metrics.get("bookmark_count", 0)
    views = metrics.get("impression_count", 1)

    engagement = likes + retweets * 2 + replies * 1.5 + quotes * 3 + bookmarks * 2
    velocity = engagement / max(views, 1) * 1000

    recency = 1.0
    created_at = tweet.get("created_at")
    if created_at:
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            hours_ago = (datetime.now(timezone.utc) - created).total_seconds() / 3600
            recency = max(0.5, 1.5 - (hours_ago / 168))
        except ValueError:
            logger.warning("Could not parse created_at for tweet %s; using neutral recency.", tweet.get("id", "?"))

    return round((engagement * 0.6 + velocity * 100 * 0.4) * recency, 2)


def enrich(tweets, users, media, ref_tweets):
    for tweet in tweets:
        author_id = tweet.get("author_id")
        if author_id and author_id in users:
            tweet["author"] = users[author_id]
        if "attachments" in tweet and "media_keys" in tweet["attachments"]:
            tweet["media"] = [media[key] for key in tweet["attachments"]["media_keys"] if key in media]
        if "referenced_tweets" in tweet:
            for ref in tweet["referenced_tweets"]:
                ref_id = ref.get("id")
                if ref_id and ref_id in ref_tweets:
                    ref["tweet_data"] = ref_tweets[ref_id]
        username = users.get(author_id, {}).get("username", "")
        if username:
            tweet["tweet_url"] = f"https://x.com/{username}/status/{tweet['id']}"
        tweet["_score"] = score_tweet(tweet)
    tweets.sort(key=lambda item: item["_score"], reverse=True)
    return tweets


def emit_full(tweets, topic, days):
    write_stdout_line(f"# X Research: {topic}")
    write_stdout_line(f"**Last {days} days** | {len(tweets)} results | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    write_stdout_line()

    themes = {}
    for tweet in tweets:
        for annotation in tweet.get("context_annotations", []):
            name = annotation.get("entity", {}).get("name", "")
            if name:
                themes[name] = themes.get(name, 0) + 1
    if themes:
        top_themes = sorted(themes.items(), key=lambda item: -item[1])[:10]
        write_stdout_line("## Trending Themes")
        for name, count in top_themes:
            write_stdout_line(f"- {name} ({count})")
        write_stdout_line()

    links = {}
    for tweet in tweets:
        for url_info in tweet.get("entities", {}).get("urls", []):
            expanded = url_info.get("expanded_url", "")
            if expanded and "twitter.com" not in expanded and "x.com" not in expanded:
                title = url_info.get("title", expanded[:60])
                links[expanded] = {"title": title, "count": links.get(expanded, {}).get("count", 0) + 1}
    if links:
        top_links = sorted(links.items(), key=lambda item: -item[1]["count"])[:10]
        write_stdout_line("## Most Shared Links")
        for url, info in top_links:
            write_stdout_line(f"- [{info['title']}]({url}) (shared {info['count']}x)")
        write_stdout_line()

    write_stdout_line(f"## Top {min(len(tweets), 25)} Posts")
    write_stdout_line()
    for index, tweet in enumerate(tweets[:25], 1):
        author = tweet.get("author", {})
        text = tweet.get("note_tweet", {}).get("text") or tweet.get("text", "")
        metrics = tweet.get("public_metrics", {})
        url = tweet.get("tweet_url", "")
        created = tweet.get("created_at", "")[:16].replace("T", " ")

        write_stdout_line(f"### [{index}] @{author.get('username', '?')} ({author.get('name', '?')})")
        if author.get("description"):
            write_stdout_line(f"*{author['description'][:120]}*")
        write_stdout_line(f"Score: {tweet['_score']} | {created}")
        write_stdout_line(
            f"Likes: {metrics.get('like_count', 0)} | RTs: {metrics.get('retweet_count', 0)} | "
            f"Replies: {metrics.get('reply_count', 0)} | Views: {metrics.get('impression_count', 'N/A')}"
        )
        write_stdout_line()
        write_stdout_line(f"> {text}")
        write_stdout_line()
        if "media" in tweet:
            for media_item in tweet["media"]:
                write_stdout_line(
                    f"Media [{media_item.get('type', '?')}]: {media_item.get('url') or media_item.get('preview_image_url', '')}"
                )
        if url:
            write_stdout_line(f"[Link]({url})")
        write_stdout_line()

    all_likes = sum(tweet.get("public_metrics", {}).get("like_count", 0) for tweet in tweets)
    all_rts = sum(tweet.get("public_metrics", {}).get("retweet_count", 0) for tweet in tweets)
    all_views = sum(tweet.get("public_metrics", {}).get("impression_count", 0) for tweet in tweets)
    write_stdout_line(
        f"---\n**Totals:** {len(tweets)} posts | {all_likes:,} likes | {all_rts:,} RTs | {all_views:,} views"
    )


def emit_compact(tweets, topic, days):
    write_stdout_line(f"# X: {topic} (last {days}d, {len(tweets)} results)")
    write_stdout_line()
    for index, tweet in enumerate(tweets[:15], 1):
        author = tweet.get("author", {})
        text = (tweet.get("note_tweet", {}).get("text") or tweet.get("text", ""))[:200]
        metrics = tweet.get("public_metrics", {})
        write_stdout_line(
            f"{index}. @{author.get('username', '?')} [{tweet['_score']}] "
            f"L:{metrics.get('like_count', 0)} RT:{metrics.get('retweet_count', 0)} V:{metrics.get('impression_count', 'N/A')}"
        )
        write_stdout_line(f"   {text}")
        if tweet.get("tweet_url"):
            write_stdout_line(f"   {tweet['tweet_url']}")
        write_stdout_line()


def emit_json(tweets, topic, days):
    write_json_stdout(
        {
            "topic": topic,
            "days": days,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total": len(tweets),
            "tweets": tweets,
        }
    )


def write_usage():
    write_stdout_line(
        'Usage: python3 x_search.py "topic" [--days=7] [--limit=100] [--no-retweets] [--lang=en] [--emit=full|compact|json]'
    )


def main():
    args = sys.argv[1:]
    if not args or args[0] in {"--help", "-h"}:
        write_usage()
        return

    opts = parse_args()
    if not BEARER:
        logger.error("X_BEARER_TOKEN not found in .env.")
        raise SystemExit(1)
    if not opts["topic"]:
        raise UsageError('Usage: python3 x_search.py "topic" [--days=7] [--limit=100] [--no-retweets] [--lang=en] [--emit=full|compact|json]')

    logger.info(
        "Searching X for: %s (last %s days, limit %s)...",
        opts["topic"],
        opts["days"],
        opts["limit"],
    )

    tweets, users, media, ref_tweets = search(
        opts["topic"],
        opts["days"],
        opts["limit"],
        opts["no_retweets"],
        opts["lang"],
    )

    if not tweets:
        logger.info("No results found.")
        return

    enriched = enrich(tweets, users, media, ref_tweets)
    emitters = {"full": emit_full, "compact": emit_compact, "json": emit_json}
    emitter = emitters[opts["emit"]]
    emitter(enriched, opts["topic"], opts["days"])


if __name__ == "__main__":
    try:
        main()
    except UsageError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
