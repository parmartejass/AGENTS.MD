# Review Adapter Contract (Provider-Agnostic)

The control-plane logic is provider-neutral. Provider integrations MUST normalize into this contract.

## Required Operations
1. `get_latest_review_run(head_sha) -> review_run | null`
2. `list_findings(head_sha) -> finding[]`
3. `request_rerun(head_sha, existing_comments, marker, trigger_text) -> rerun_decision`
4. `list_threads(head_sha) -> thread[]`
5. `resolve_thread(thread_id) -> bool`

## Normalized `review_run` Shape
```json
{
  "name": "Code Review Agent",
  "head_sha": "abc123",
  "status": "completed",
  "conclusion": "success",
  "summary": "No actionable findings.",
  "completed_at": "2026-02-16T12:00:00Z"
}
```

## Normalized `finding` Shape
```json
{
  "id": "finding-001",
  "severity": "high",
  "confidence": "high",
  "summary": "SQL injection risk",
  "actionable": true
}
```

## Normalized `thread` Shape
```json
{
  "id": "thread-1",
  "isResolved": false,
  "comments": [
    { "author_login": "review-agent[bot]" }
  ]
}
```

## Invariants
1. Current-head SHA strictness:
   - Any review state is valid only when `review_run.head_sha == current_head_sha`.
2. Stale evidence rejection:
   - Provider summaries/findings tied to older SHAs MUST be ignored.
3. Deterministic rerun dedupe:
   - `request_rerun` must dedupe by marker + `sha:<headSha>`.
4. Thread safety:
   - Auto-resolve only unresolved bot-only threads after clean rerun.
5. Explicit failure:
   - Adapter errors should be explicit and machine-readable.
