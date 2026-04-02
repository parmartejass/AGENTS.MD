---
name: governance-autoresearch
description: Autoresearch loop for governance files. Researches latest X discourse on each governance topic, proposes ONE atomic improvement per file, validates it, keeps or discards. Use when the user asks to improve, update, or evolve the governance framework using latest community insights.
---

# Governance Autoresearch Skill

## Overview

Adapts Karpathy's autoresearch pattern to governance file improvement:
- **Research** each file's topics on X (last 7 days)
- **Cross-reference** with bookmarks data (if available in `X-Bookmarks Import/`)
- **Propose** ONE atomic change per file
- **Validate** structure and SSOT consistency
- **Keep** if it improves the file, **discard** if not
- **Commit** each kept change with `experiment:` prefix

## Prerequisites

- `X_BEARER_TOKEN` in `.env`
- Python 3.10+
- Bookmarks import data (optional, in `X-Bookmarks Import/`)

## Workflow — Execute These Steps Per File

### Step 0: Get Research Context

Run the research script for the target file:

```bash
python3 "X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py" "<file_path>"
```

This outputs JSON with:
- Top X posts about the file's topics (engagement-ranked)
- External links being shared
- File summary for context

### Step 1: Read the File

Read the full governance file. Note:
- Current structure and sections
- YAML frontmatter (doc_type, ssot_owner)
- Key policies, rules, or patterns defined

### Step 2: Cross-Reference Bookmarks (if available)

Check `X-Bookmarks Import/data/articles-batch-1.md`, `data/articles-batch-2.md`, `data/github-repos.md`, `data/other-sources.md` for content relevant to this file's domain. Key sources:

| Bookmark Content | Relevant To |
|-----------------|-------------|
| Claude Code Skills (Anthropic) | skill-standards, platform-adapters |
| .claude/ folder anatomy | settings, context-retrieval |
| Autoresearch / self-improving | automation loops, nightly-compound |
| Paperclip (AI company) | workflow orchestration, subagents |
| EurekaClaw (memory system) | context-retrieval, SSOT |
| evals-skills (hamelsmu) | testing, playbooks |
| project-skill-audit | skill-standards, repo-discovery |
| chrome-cdp-skill | skill-standards, platform-adapters |
| Self-learning agents (Cursor) | principles, AGENTS.md |
| SOTA memory system | context-retrieval, sources-of-truth |

### Step 3: Propose ONE Atomic Change

Based on research findings, propose exactly ONE change. Types of valid changes:

1. **Add a new section** — a concept the community is converging on that the file doesn't cover
2. **Strengthen an existing rule** — add specificity based on real-world patterns
3. **Add a reference/link** — point to a new tool, pattern, or standard
4. **Update terminology** — align with current ecosystem language
5. **Add a gotcha/anti-pattern** — something the community has learned the hard way

### Anti-patterns (DO NOT do these):

- Do NOT rewrite entire files
- Do NOT change SSOT owners or frontmatter without explicit approval
- Do NOT add speculative features — only things with community evidence
- Do NOT duplicate content already in another governance file
- Do NOT remove existing rules without evidence they're harmful
- Do NOT add content unrelated to the file's stated scope

### Step 4: Validate

Before applying, check:

1. **Structure preserved** — YAML frontmatter intact, heading hierarchy maintained
2. **SSOT consistency** — no contradictions with AGENTS.md or other governance files
3. **No duplication** — content doesn't exist elsewhere in the governance pack
4. **Evidence-backed** — change is supported by X research or bookmarks data
5. **Minimal diff** — smallest change that captures the insight

Run validation if available:
```bash
python3 scripts/check_governance_core/main.py
```

### Step 5: Apply or Discard

- If validation passes: apply the change using Edit tool
- If validation fails: discard and record why
- Record the outcome either way

### Step 6: Report

For each file, output:

```
FILE: <path>
STATUS: KEPT | DISCARDED
CHANGE: <one-line description>
EVIDENCE: <X post URL or bookmark reference>
REASON: <why this improves the governance framework>
```

## Running the Full Loop

To process all governance files sequentially:

1. Get the file list:
```bash
python3 "X-Bookmarks Import/skills/governance-autoresearch/scripts/governance_research.py" --list
```

2. For each file, execute Steps 0-6 above.

3. After all files, run full validation:
```bash
python3 scripts/check_governance_core/main.py
```

## Scoring (How to Judge Quality)

A change is worth keeping if it meets ALL of:
- [ ] Adds genuinely new information not derivable from existing docs
- [ ] Supported by 2+ X posts or 1 high-engagement post (>100 likes)
- [ ] Fits the file's existing scope and doc_type
- [ ] Does not weaken existing rules
- [ ] Passes structural validation

## Rate Limit Awareness

- X API recent search: 180 requests / 15 minutes
- Each file uses 2-3 search queries
- Full loop (~27 files) uses ~80 queries — well within limits
- If rate-limited, wait and resume from the last file
