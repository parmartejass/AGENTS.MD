from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from x_runtime import parse_retry_delay_seconds, request_json, summarize_payload


logger = logging.getLogger(__name__)

TWEET_FIELDS = "id,text,author_id,created_at,conversation_id,in_reply_to_user_id,referenced_tweets,attachments,geo,lang,public_metrics,possibly_sensitive,reply_settings,source,entities,context_annotations,note_tweet"
EXPANSIONS = "author_id,referenced_tweets.id,referenced_tweets.id.author_id,attachments.media_keys,attachments.poll_ids,in_reply_to_user_id,entities.mentions.username"
USER_FIELDS = "id,name,username,created_at,description,profile_image_url,public_metrics,verified,verified_type,url,location"
MEDIA_FIELDS = "media_key,type,url,preview_image_url,alt_text,duration_ms,height,width,public_metrics,variants"
POLL_FIELDS = "id,options,duration_minutes,end_datetime,voting_status"
MAX_RATE_LIMIT_RETRIES = 5


def fetch_current_user(token: str) -> tuple[str, str]:
    response = request_json(
        "GET",
        "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {token}"},
        context="GET https://api.twitter.com/2/users/me",
    )
    if response.status != 200:
        raise RuntimeError(f"Failed to get user info ({response.status}): {summarize_payload(response.data)}")

    return response.data["data"]["id"], response.data["data"]["username"]


def fetch_bookmarks(user_id: str, token: str, since: datetime):
    url = f"https://api.x.com/2/users/{user_id}/bookmarks"
    params = {
        "max_results": "100",
        "tweet.fields": TWEET_FIELDS,
        "expansions": EXPANSIONS,
        "user.fields": USER_FIELDS,
        "media.fields": MEDIA_FIELDS,
        "poll.fields": POLL_FIELDS,
    }

    all_tweets, users, media, tweets_inc, polls = [], {}, {}, {}, {}
    pagination_token = None
    page = 0
    rate_limit_retries = 0

    logger.info("Fetching bookmarks since %s...", since.strftime("%Y-%m-%d"))

    while True:
        page += 1
        request_params = dict(params)
        if pagination_token:
            request_params["pagination_token"] = pagination_token

        response = request_json(
            "GET",
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=request_params,
            context=f"GET {url}",
        )

        if response.status == 429:
            rate_limit_retries += 1
            if rate_limit_retries > MAX_RATE_LIMIT_RETRIES:
                raise RuntimeError(f"Rate limit persisted after {MAX_RATE_LIMIT_RETRIES} retries.")
            delay = parse_retry_delay_seconds(response.headers, default_seconds=60)
            logger.warning(
                "Rate limited while fetching bookmarks; waiting %s seconds before retry %s/%s.",
                delay,
                rate_limit_retries,
                MAX_RATE_LIMIT_RETRIES,
            )
            time.sleep(delay)
            page -= 1
            continue

        rate_limit_retries = 0
        if response.status != 200:
            raise RuntimeError(f"Bookmark fetch failed ({response.status}): {summarize_payload(response.data)}")

        if "data" not in response.data:
            break

        includes = response.data.get("includes", {})
        for user in includes.get("users", []):
            users[user["id"]] = user
        for media_item in includes.get("media", []):
            media[media_item["media_key"]] = media_item
        for tweet in includes.get("tweets", []):
            tweets_inc[tweet["id"]] = tweet
        for poll in includes.get("polls", []):
            polls[poll["id"]] = poll

        stop = False
        for tweet in response.data["data"]:
            created = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
            if created >= since:
                all_tweets.append(tweet)
            else:
                stop = True

        logger.info("  Page %s: %s tweets (%s in range)", page, len(response.data["data"]), len(all_tweets))

        if stop:
            break
        pagination_token = response.data.get("meta", {}).get("next_token")
        if not pagination_token:
            break

    return all_tweets, users, media, tweets_inc, polls


def enrich(tweets, users, media, ref_tweets, polls):
    enriched = []
    for tweet in tweets:
        item = dict(tweet)
        author_id = item.get("author_id")
        if author_id and author_id in users:
            item["author"] = users[author_id]
        if "attachments" in item and "media_keys" in item["attachments"]:
            item["media"] = [media[key] for key in item["attachments"]["media_keys"] if key in media]
        if "attachments" in item and "poll_ids" in item["attachments"]:
            item["polls"] = [polls[poll_id] for poll_id in item["attachments"]["poll_ids"] if poll_id in polls]
        if "referenced_tweets" in item:
            for ref in item["referenced_tweets"]:
                ref_id = ref.get("id")
                if ref_id and ref_id in ref_tweets:
                    ref_data = dict(ref_tweets[ref_id])
                    ref_author_id = ref_data.get("author_id")
                    if ref_author_id and ref_author_id in users:
                        ref_data["author"] = users[ref_author_id]
                    ref["tweet_data"] = ref_data
        username = users.get(author_id, {}).get("username", "")
        if username:
            item["tweet_url"] = f"https://x.com/{username}/status/{item['id']}"
        enriched.append(item)
    return enriched


def save_bookmarks(output_dir: Path, enriched, since: datetime, *, days_back: int) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"bookmarks_{timestamp}.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "since": since.isoformat(),
                "total_bookmarks": len(enriched),
                "bookmarks": enriched,
            },
            handle,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    logger.info("Saved %s bookmarks -> %s", len(enriched), json_path)

    summary_path = output_dir / f"bookmarks_summary_{timestamp}.txt"
    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write(f"X Bookmarks - Last {days_back} Days\n")
        handle.write(f"Fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Total: {len(enriched)} bookmarks\n")
        handle.write("=" * 80 + "\n\n")
        for index, tweet in enumerate(enriched, 1):
            author = tweet.get("author", {})
            text = tweet.get("note_tweet", {}).get("text") or tweet.get("text", "")
            metrics = tweet.get("public_metrics", {})
            handle.write(f"[{index}] @{author.get('username', '?')} ({author.get('name', '?')})\n")
            handle.write(f"    Date: {tweet.get('created_at', '')[:19].replace('T', ' ')}\n")
            handle.write(f"    URL:  {tweet.get('tweet_url', '')}\n")
            handle.write(
                "    Likes: "
                f"{metrics.get('like_count', 0)} | RTs: {metrics.get('retweet_count', 0)} | "
                f"Replies: {metrics.get('reply_count', 0)} | Views: {metrics.get('impression_count', 'N/A')}\n"
            )
            handle.write(f"    Text: {text}\n")
            if "media" in tweet:
                for media_item in tweet["media"]:
                    handle.write(
                        f"    Media [{media_item.get('type', '?')}]: "
                        f"{media_item.get('url') or media_item.get('preview_image_url', '')}\n"
                    )
            handle.write("\n" + "-" * 80 + "\n\n")
    logger.info("Saved summary -> %s", summary_path)
