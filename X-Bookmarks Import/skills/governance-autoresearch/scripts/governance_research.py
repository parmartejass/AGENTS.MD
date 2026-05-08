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
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


X_BOOKMARKS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = X_BOOKMARKS_ROOT.parent
if str(X_BOOKMARKS_ROOT) not in sys.path:
    sys.path.insert(0, str(X_BOOKMARKS_ROOT))

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


configure_logging()
logger = logging.getLogger(__name__)

load_env(Path(__file__).resolve().parent)
BEARER = os.environ.get("X_BEARER_TOKEN", "")
MAX_RATE_LIMIT_RETRIES = 1

GOVERNANCE_FILES = [
    "AGENTS.md",
    "docs/agents/00-principles/principles.md",
    "docs/agents/05-context-retrieval/context-retrieval.md",
    "docs/agents/10-repo-discovery/repo-discovery.md",
    "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md",
    "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md",
    "docs/agents/30-logging-errors/logging-errors.md",
    "docs/agents/35-authority-bounded-modules/authority-bounded-modules.md",
    "docs/agents/40-config-constants/config-constants.md",
    "docs/agents/70-io-data-integrity/io-data-integrity.md",
    "docs/agents/80-testing-real-files/testing-real-files.md",
    "docs/agents/90-release-checklist/release-checklist.md",
    "docs/agents/workflow-registry/workflow-registry.md",
    "docs/agents/skills/00-skill-standards/skill-standards.md",
    "docs/agents/skills/10-platform-adapters/platform-adapters.md",
    "docs/agents/settings/00-settings-standards/settings-standards.md",
    "docs/agents/playbooks/rca-methods-template/rca-methods-template.md",
    "docs/agents/playbooks/bugfix-template/bugfix-template.md",
    "docs/agents/playbooks/design-principles-checklist/design-principles-checklist.md",
    "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md",
    "docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md",
]

FILE_TOPIC_MAP = {
    "AGENTS.md": ["AGENTS.md governance", "AI agent constitution rules"],
    "docs/agents/00-principles/principles.md": ["AI agent first principles", "coding agent design principles"],
    "docs/agents/05-context-retrieval/context-retrieval.md": ["AI agent context injection", "LLM context management coding"],
    "docs/agents/10-repo-discovery/repo-discovery.md": ["AI agent repo discovery", "codebase exploration agent"],
    "docs/agents/20-sources-of-truth-map/sources-of-truth-map.md": ["single source of truth code", "SSOT software architecture"],
    "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md": ["documentation as code", "docs single source of truth"],
    "docs/agents/30-logging-errors/logging-errors.md": ["AI agent error handling", "coding agent logging observability"],
    "docs/agents/35-authority-bounded-modules/authority-bounded-modules.md": ["module boundaries authority", "bounded context software"],
    "docs/agents/40-config-constants/config-constants.md": ["configuration management constants", "config as code"],
    "docs/agents/70-io-data-integrity/io-data-integrity.md": ["data integrity file processing", "IO safety coding agent"],
    "docs/agents/80-testing-real-files/testing-real-files.md": ["AI agent testing strategy", "coding agent test automation"],
    "docs/agents/90-release-checklist/release-checklist.md": ["release checklist automation", "CI CD agent workflow"],
    "docs/agents/workflow-registry/workflow-registry.md": ["workflow state machine", "agent workflow orchestration"],
    "docs/agents/skills/00-skill-standards/skill-standards.md": ["Claude Code skills", "AI agent skills standard"],
    "docs/agents/skills/10-platform-adapters/platform-adapters.md": ["multi-platform agent", "agent platform adapter"],
    "docs/agents/settings/00-settings-standards/settings-standards.md": ["agent settings configuration", "coding agent permissions"],
    "docs/agents/playbooks/rca-methods-template/rca-methods-template.md": ["root cause analysis AI", "RCA debugging agent"],
    "docs/agents/playbooks/bugfix-template/bugfix-template.md": ["AI bugfix workflow", "agent debugging template"],
    "docs/agents/playbooks/design-principles-checklist/design-principles-checklist.md": ["software design principles AI", "SOLID DRY agent coding"],
    "docs/agents/playbooks/governance-learnings-template/governance-learnings-template.md": ["governance framework learnings", "AI governance improvement"],
    "docs/agents/playbooks/ai-coding-prompt-template/ai-coding-prompt-template.md": ["AI coding prompt engineering", "agent prompt template"],
}


def api_get(url: str, params: dict[str, str] | None = None):
    response = request_json(
        "GET",
        url,
        headers={"Authorization": f"Bearer {BEARER}"},
        params=params,
        context=f"GET {url}",
    )
    return response.status, response.data, response.headers


def extract_topics(filepath):
    """Get search topics for a governance file."""
    normalized_path = Path(filepath).as_posix()
    if normalized_path in FILE_TOPIC_MAP:
        return FILE_TOPIC_MAP[normalized_path]

    filename = Path(normalized_path).name
    if filename in FILE_TOPIC_MAP:
        return FILE_TOPIC_MAP[filename]

    full_path = REPO_ROOT / filepath
    if not full_path.exists():
        return [filename.replace(".md", "").replace("-", " ")]

    content = full_path.read_text(encoding="utf-8")
    headings = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    topics = []
    for heading in headings[:5]:
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", heading).strip()
        if len(clean) > 5:
            topics.append(clean)

    if not topics:
        topics = [filename.replace(".md", "").replace("-", " ")]
    return topics[:3]


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
    full_path = REPO_ROOT / filepath
    if not full_path.exists():
        raise UsageError(f"{filepath} not found")

    topics = extract_topics(filepath)
    content = full_path.read_text(encoding="utf-8")
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
        "file": filepath,
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
        for governance_file in GOVERNANCE_FILES:
            exists = "OK" if (REPO_ROOT / governance_file).exists() else "MISSING"
            topics = extract_topics(governance_file)
            write_stdout_line(f"  [{exists}] {governance_file}")
            write_stdout_line(f"         Topics: {', '.join(topics)}")
        return

    if not BEARER:
        logger.error("X_BEARER_TOKEN not found.")
        raise SystemExit(1)

    if args[0] == "--all":
        all_research = [research_file(governance_file) for governance_file in GOVERNANCE_FILES]
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
