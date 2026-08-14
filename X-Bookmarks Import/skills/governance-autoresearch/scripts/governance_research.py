"""
Governance Autoresearch — X-powered improvement loop for governance files.

For each file:
  1. Extract key concepts
  2. Search X for latest discourse (7-day window)
  3. Output research context for the agent to propose improvements

Usage:
  python3 governance_research.py <file_path>
  python3 governance_research.py --list          # list all governance files
  python3 governance_research.py --all           # research all files sequentially

Reads X_BEARER_TOKEN from .env (walks up to find it).
"""

from __future__ import annotations

import logging
import os
import re
import stat
import sys
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath


X_BOOKMARKS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = X_BOOKMARKS_ROOT.parent
for import_root in (X_BOOKMARKS_ROOT, REPO_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from x_runtime import (  # noqa: E402
    UsageError,
    configure_logging,
    load_env,
    parse_retry_delay_seconds,
    request_json,
    summarize_payload,
    write_json_stdout,
    write_stdout_line,
)
from scripts.check_governance_core.check_governance_core_main import resolve_documents  # noqa: E402


configure_logging()
logger = logging.getLogger(__name__)

load_env(Path(__file__).resolve().parent)
BEARER = os.environ.get("X_BEARER_TOKEN", "")
MAX_TOPICS_PER_FILE = 3

@lru_cache(maxsize=1)
def governance_files() -> tuple[str, ...]:
    resolved = resolve_documents({"repo_root": str(REPO_ROOT), "governance_root": str(REPO_ROOT)})
    if resolved["status"] != "PASSED":
        raise RuntimeError(f"Governance document resolution failed: {resolved['errors']}")
    return tuple(str(value) for value in resolved["documents"])


@lru_cache(maxsize=1)
def governance_file_set() -> frozenset[str]:
    return frozenset(governance_files())


def _maximum_full_loop_searches() -> int:
    return len(governance_files()) * MAX_TOPICS_PER_FILE


def resolve_governance_path(filepath: str | os.PathLike[str]) -> tuple[str, Path]:
    value = os.fspath(filepath)
    relative = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or ":" in value
        or relative.is_absolute()
        or relative.as_posix() != value
        or any(part in {"", ".", ".."} or part != part.rstrip(" .") for part in relative.parts)
    ):
        raise UsageError(f"Governance path must be a canonical repository-relative path: {value!r}")
    if value not in governance_file_set():
        raise UsageError(f"Governance path is not in the canonical document corpus: {value}")
    repo_root = REPO_ROOT.resolve()
    current = repo_root
    try:
        for part in relative.parts:
            current /= part
            metadata = current.stat(follow_symlinks=False)
            attributes = getattr(metadata, "st_file_attributes", 0)
            reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            if current.is_symlink() or attributes & reparse_flag or (current.is_file() and metadata.st_nlink > 1):
                raise UsageError(f"Governance path must not traverse an alias: {value}")
        resolved = current.resolve(strict=True)
        resolved.relative_to(repo_root)
    except (OSError, ValueError) as exc:
        raise UsageError(f"Governance path is unavailable or escapes the repository: {value}") from exc
    if not resolved.is_file():
        raise UsageError(f"Governance path is not a file: {value}")
    return value, resolved


def api_get(url: str, params: dict[str, str] | None = None):
    response = request_json(
        "GET",
        url,
        headers={"Authorization": f"Bearer {BEARER}"},
        params=params,
        context=f"GET {url}",
    )
    return response.status, response.data, response.headers


def _extract_topics(normalized_path: str, content: str) -> list[str]:
    filename = Path(normalized_path).name
    headings = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    topics = []
    for heading in headings[:5]:
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", heading).strip()
        if len(clean) > 5:
            topics.append(clean)

    if not topics:
        topics = [filename.replace(".md", "").replace("-", " ")]
    return topics[:MAX_TOPICS_PER_FILE]


def extract_topics(filepath):
    """Get search topics for a governance file."""
    normalized_path, full_path = resolve_governance_path(filepath)
    return _extract_topics(normalized_path, full_path.read_text(encoding="utf-8"))


def search_x(query, limit=30):
    """Search X for recent tweets on a topic."""
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "query": f"{query} -is:retweet lang:en",
        "max_results": str(max(10, min(limit, 100))),
        "start_time": since,
        "sort_order": "relevancy",
        "tweet.fields": "id,text,author_id,created_at,public_metrics,entities,note_tweet",
        "expansions": "author_id",
        "user.fields": "username,name,public_metrics,verified,description",
    }

    status, data, headers = api_get("https://api.x.com/2/tweets/search/recent", params)
    if status == 429:
        delay = parse_retry_delay_seconds(headers, default_seconds=60)
        logger.warning("Search rate limited; waiting %s seconds before retry.", delay)
        time.sleep(delay)
        status, data, headers = api_get("https://api.x.com/2/tweets/search/recent", params)

    if status in {401, 403}:
        raise RuntimeError(f"Search authentication failed ({status}): {summarize_payload(data)}")
    if status == 429:
        raise RuntimeError("Search rate limit persisted after bounded retry.")
    if status != 200:
        raise RuntimeError(f"Search failed ({status}): {query} :: {summarize_payload(data)}")

    if "data" not in data:
        logger.info("Search for %r returned no data.", query)
        return []

    users = {}
    for user in data.get("includes", {}).get("users", []):
        users[user["id"]] = user

    results = []
    for tweet in data["data"]:
        metrics = tweet.get("public_metrics", {})
        engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0) * 2 + metrics.get("bookmark_count", 0) * 2
        author = users.get(tweet.get("author_id"), {})
        text = tweet.get("note_tweet", {}).get("text") or tweet.get("text", "")
        results.append(
            {
                "text": text,
                "author": f"@{author.get('username', '?')}",
                "author_bio": author.get("description", "")[:100],
                "engagement": engagement,
                "likes": metrics.get("like_count", 0),
                "views": metrics.get("impression_count", 0),
                "url": f"https://x.com/{author.get('username', '_')}/status/{tweet['id']}",
                "created_at": tweet.get("created_at", ""),
                "links": [
                    url_info.get("expanded_url", "")
                    for url_info in tweet.get("entities", {}).get("urls", [])
                    if "x.com" not in url_info.get("expanded_url", "") and "twitter.com" not in url_info.get("expanded_url", "")
                ],
            }
        )

    results.sort(key=lambda item: item["engagement"], reverse=True)
    return results


def research_file(filepath):
    """Research a governance file and output context for improvement."""
    normalized_path, full_path = resolve_governance_path(filepath)
    content = full_path.read_text(encoding="utf-8")
    topics = _extract_topics(normalized_path, content)
    line_count = len(content.splitlines())

    logger.info("\n%s", "=" * 70)
    logger.info("RESEARCHING: %s", filepath)
    logger.info("  Lines: %s | Topics: %s", line_count, topics)

    all_results = []
    for topic in topics:
        logger.info('  Searching X: "%s"...', topic)
        results = search_x(topic, limit=20)
        all_results.extend(results)
        logger.info("    Found %s results", len(results))

    seen = set()
    unique = []
    for result in all_results:
        if result["url"] not in seen:
            seen.add(result["url"])
            unique.append(result)

    unique.sort(key=lambda item: item["engagement"], reverse=True)
    top = unique[:15]

    ext_links = []
    for result in unique:
        ext_links.extend(result.get("links", []))
    ext_links = list(dict.fromkeys(ext_links))[:10]

    return {
        "file": normalized_path,
        "line_count": line_count,
        "topics_searched": topics,
        "total_results": len(unique),
        "top_posts": top,
        "external_links": ext_links,
        "file_summary": content[:500],
    }


def write_usage() -> None:
    write_stdout_line("Usage:")
    write_stdout_line("  python3 governance_research.py <file_path>  # research one file")
    write_stdout_line("  python3 governance_research.py --list       # list all governance files")
    write_stdout_line("  python3 governance_research.py --all        # research all files")


def main():
    args = sys.argv[1:]

    if not args or args[0] in {"--help", "-h"}:
        write_usage()
        return

    if args[0] == "--list":
        for governance_file in governance_files():
            exists = "OK" if (REPO_ROOT / governance_file).exists() else "MISSING"
            topics = extract_topics(governance_file)
            write_stdout_line(f"  [{exists}] {governance_file}")
            write_stdout_line(f"         Topics: {', '.join(topics)}")
        write_stdout_line(
            "Summary: "
            f"documents={len(governance_files())}, "
            f"max_topics_per_file={MAX_TOPICS_PER_FILE}, "
            f"maximum_full_loop_searches={_maximum_full_loop_searches()}"
        )
        return

    if not BEARER:
        logger.error("X_BEARER_TOKEN not found.")
        raise SystemExit(1)

    if args[0] == "--all":
        all_research = [research_file(governance_file) for governance_file in governance_files()]
        write_json_stdout(all_research)
        return

    result = research_file(args[0])
    write_json_stdout(result)


if __name__ == "__main__":
    try:
        main()
    except UsageError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
