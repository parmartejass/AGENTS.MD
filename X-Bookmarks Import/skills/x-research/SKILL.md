---
name: x-research
description: "Search and analyze recent X (Twitter) posts on any topic. Fetches public posts from the last 7 days, ranks by engagement, identifies trending themes, and surfaces most-shared links. Use when the user asks to research, explore, or find what people are saying about a topic on X/Twitter. Triggers on phrases like 'what is trending', 'search X for', 'what are people saying about', 'research on X', 'Twitter search', 'X discourse'."
---

# X Research Skill

## Overview

Search and analyze recent X (Twitter) posts on any topic. Returns engagement-scored results with full tweet data, trending themes, and most-shared links. Uses the X API v2 recent search endpoint (7-day window) with the app-only bearer token from `.env`.

## Prerequisites

- `X_BEARER_TOKEN` set in `.env` (app-only bearer token)
- Python 3.10+
- No external dependencies (stdlib only)

## Usage

Run the research script with the topic as the first argument:

```bash
python3 "X-Bookmarks Import/skills/x-research/scripts/x_search.py" "TOPIC" [OPTIONS]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--days=N` | 7 | Lookback window (max 7, API limit) |
| `--limit=N` | 100 | Max tweets to fetch (paginated at 100/page) |
| `--no-retweets` | off | Exclude retweets |
| `--lang=XX` | any | Filter by language code (en, es, ja, etc.) |
| `--emit=MODE` | full | Output format: `full`, `compact`, or `json` |

### Examples

```bash
# Full research on Claude Code
python3 "X-Bookmarks Import/skills/x-research/scripts/x_search.py" "Claude Code" --no-retweets --lang=en

# Quick scan of AI agents discourse
python3 "X-Bookmarks Import/skills/x-research/scripts/x_search.py" "AI agents" --emit=compact --limit=50

# JSON output for programmatic use
python3 "X-Bookmarks Import/skills/x-research/scripts/x_search.py" "AGENTS.md governance" --emit=json

# Specific user's recent posts
python3 "X-Bookmarks Import/skills/x-research/scripts/x_search.py" "from:anthropaborner" --days=7
```

## Output Formats

### `full` (default)
- Trending themes (from X context annotations)
- Most-shared external links
- Top 25 posts ranked by engagement score
- Per-post: author, bio, metrics, full text, media, tweet URL
- Aggregate stats

### `compact`
- Top 15 posts, one-line per tweet
- Score, metrics, truncated text, URL

### `json`
- Machine-readable full dataset
- All tweets with enriched author/media data

## Scoring

Posts are ranked by composite engagement score (likes, RTs, replies, quotes, bookmarks) weighted by velocity and recency. See [REFERENCE.md](REFERENCE.md) for the full formula.

## Limitations

- **7-day window**: X API recent search covers the last 7 days only. Full-archive search requires Pro plan ($5K/mo).
- **Rate limits**: 180 requests per 15 minutes (Basic plan). Script handles pagination within this.
- **Monthly quota**: 10,000 tweets/month on Basic plan. Monitor usage.
- **No protected tweets**: Only public posts are searchable.

## Query Operators

The topic string supports X search operators (`from:`, `to:`, `has:media`, `has:links`, `url:`, `-is:retweet`, `"exact phrase"`, boolean `OR`). See [REFERENCE.md](REFERENCE.md) for the full operator table.

## Error Handling

- **Rate limited (429)**: Wait for the duration in the `x-rate-limit-reset` header, then retry. The script handles pagination within rate limits, but multi-topic sessions may exceed 180 requests/15 minutes.
- **Invalid token (401/403)**: Verify `X_BEARER_TOKEN` in `.env` is a valid app-only bearer token from the X Developer Portal.
- **Quota exhausted**: Check monthly usage at the X Developer Portal. Basic plan allows 10,000 tweets/month. Use `--limit` with lower values to conserve quota.
- **Empty results**: Broaden the query — remove restrictive operators, shorten exact phrases, or try alternate terminology.

## Integration with Other Skills

The `--emit=json` output can be piped to other tools or saved for analysis:

```bash
python3 .../x_search.py "topic" --emit=json > /tmp/x_research.json
```

The x-api-data-access skill provides the auth/endpoint reference if you need to extend this.
