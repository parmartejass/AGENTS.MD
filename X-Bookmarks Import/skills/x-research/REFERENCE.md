# X Research Reference

## Scoring Algorithm

Posts are ranked by a composite engagement score:

```
engagement = likes + (RTs * 2) + (replies * 1.5) + (quotes * 3) + (bookmarks * 2)
velocity   = engagement / views * 1000
recency    = 1.5 decaying to 0.5 over 7 days
score      = (engagement * 0.6 + velocity * 100 * 0.4) * recency
```

This surfaces high-signal posts (viral + high engagement-to-view ratio) with recency bias.

## Query Operators

The topic string supports X search operators:

| Operator | Example | Purpose |
|----------|---------|---------|
| `from:user` | `from:AnthropicAI` | Posts by specific account |
| `to:user` | `to:ClaudeCode` | Replies to specific account |
| `has:media` | `AI agents has:media` | Posts with images/video |
| `has:links` | `Claude Code has:links` | Posts with URLs |
| `url:"domain"` | `url:"github.com"` | Posts linking to specific domain |
| `-is:retweet` | auto via `--no-retweets` | Exclude retweets |
| `is:reply` / `-is:reply` | | Include/exclude replies |
| `"exact phrase"` | `"Claude Code skills"` | Exact match |
| `(A OR B)` | `(Claude OR Codex) skills` | Boolean OR |
