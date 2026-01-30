---
doc_type: proposal
ssot_owner: AGENTS.md
update_trigger: memory integration strategy or provider options change
---

# Memory Integration Roadmap: Learning-Enhanced Governance

## Executive Summary

This roadmap defines how to integrate persistent memory capabilities into the governance framework **without hardcoding a specific provider** (like Supermemory). The goal is to create a **learning feedback loop** where:

1. Agents accumulate learnings during sessions
2. Learnings persist across sessions via abstracted memory
3. Governance evolves based on validated learnings
4. Memory providers are swappable (Supermemory, local vector DB, git-native, etc.)

**Core Principle**: Memory enhances governance; it does not replace it. Governance remains the authoritative constitution. Memory is the persistent knowledge substrate.

---

## Problem Statement

| Gap | Impact |
|-----|--------|
| Learning is session-bound | Same mistakes repeat across sessions |
| Context injection is static | `agents-manifest.yaml` can't learn from experience |
| No semantic retrieval | Relevant past decisions aren't surfaced |
| Manual governance updates | Learnings → governance requires human effort |

---

## Architecture: Provider-Agnostic Memory Layer

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GOVERNANCE (SSOT)                           │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────────┐  │
│  │ AGENTS.md   │  │ agents-manifest  │  │ docs/agents/*.md      │  │
│  │ (authority) │  │ (injection rules)│  │ (supporting policy)   │  │
│  └─────────────┘  └──────────────────┘  └───────────────────────┘  │
│         ▲                  ▲                       ▲                │
│         │                  │                       │                │
│         └──────────────────┼───────────────────────┘                │
│                            │                                        │
│                   LEARNING FEEDBACK LOOP                            │
│                            │                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  MEMORY LAYER   │
                    │  (abstraction)  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Supermemory    │ │  Local Vector   │ │  Git-Native     │
│  (MCP provider) │ │  (ChromaDB/     │ │  (structured    │
│                 │ │   LanceDB)      │ │   YAML files)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Memory Provider Interface (MPI)

To avoid hardcoding any provider, define a standard interface:

```yaml
# memory-provider-interface.yaml (specification)
version: 1
interface: MemoryProvider
description: >-
  Abstract interface for memory operations. Any provider (Supermemory,
  ChromaDB, git-native, etc.) must implement these operations.

operations:
  store:
    description: Store a memory item
    input:
      content: string       # The content to store
      metadata:
        type: string        # learning | decision | discovery | invariant
        source: string      # session_id, file_path, or governance_ref
        timestamp: string   # ISO8601
        tags: string[]      # searchable tags
        confidence: float   # 0.0-1.0, for unverified learnings
    output:
      memory_id: string

  retrieve:
    description: Semantic search for relevant memories
    input:
      query: string         # Natural language query
      filters:
        type: string[]      # Filter by type
        tags: string[]      # Filter by tags
        min_confidence: float
      limit: integer        # Max results
    output:
      memories: Memory[]

  promote:
    description: Mark a learning as governance-ready
    input:
      memory_id: string
      target: string        # AGENTS.md | manifest | docs/agents/* | learning.md
      proposal: string      # Draft governance text
    output:
      promotion_id: string

  list_promotions:
    description: Get pending governance proposals from learnings
    input:
      status: string        # pending | approved | rejected | merged
    output:
      promotions: Promotion[]
```

---

## Provider Implementations

### Option 1: Supermemory (Cloud/MCP)

**Pros**: Fast, scalable, cross-LLM via MCP, no infra management
**Cons**: External dependency, potential privacy concerns

```yaml
# .governance/memory-config.yaml
provider: supermemory
config:
  mode: mcp                    # or 'api' for direct API
  collection: governance_learnings
  self_hosted: false           # true for console.supermemory.ai API key
```

### Option 2: Local Vector DB (ChromaDB/LanceDB)

**Pros**: No external dependency, full privacy, works offline
**Cons**: Requires local setup, no cross-machine sync

```yaml
provider: chromadb
config:
  path: .governance/memory/chroma.db
  embedding_model: all-MiniLM-L6-v2  # local model
```

### Option 3: Git-Native (Structured YAML)

**Pros**: Zero dependencies, version-controlled, auditable
**Cons**: No semantic search, manual retrieval

```yaml
provider: git-native
config:
  path: .governance/memory/learnings/
  format: yaml
  index_file: .governance/memory/index.yaml
```

### Option 4: Hybrid (Recommended)

**Pros**: Best of all worlds
**Cons**: More complex setup

```yaml
provider: hybrid
config:
  primary: supermemory-mcp     # For semantic retrieval
  fallback: git-native         # For offline/audit trail
  sync_strategy: bidirectional # Sync learnings between providers
```

---

## Learning Feedback Loop

### Phase 1: Capture (Session → Memory)

During agent sessions, learnings are captured and stored:

```
┌─────────────────────────────────────────────────────────────┐
│ SESSION                                                     │
│                                                             │
│  1. Agent encounters friction/failure                       │
│  2. Agent identifies learning (per governance-learnings     │
│     playbook template)                                      │
│  3. Learning captured via Memory Provider Interface         │
│                                                             │
│  store({                                                    │
│    content: "Path.glob() returns generator, not list...",   │
│    metadata: {                                              │
│      type: "learning",                                      │
│      source: "session_abc123",                              │
│      tags: ["python", "pathlib", "iteration"],              │
│      confidence: 0.8                                        │
│    }                                                        │
│  })                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Retrieve (Memory → Context Injection)

Before implementing, agents query memory for relevant learnings:

```yaml
# Extended agents-manifest.yaml
memory_injection:
  enabled: true
  provider: ${MEMORY_PROVIDER}  # Environment variable, not hardcoded
  inject_on_task_start:
    query_template: "learnings relevant to: {task_keywords}"
    max_results: 5
    min_confidence: 0.7
  inject_profiles:
    excel_automation:
      query: "pitfalls with Excel COM, openpyxl, xlwings"
    io_batch:
      query: "file I/O gotchas, chunking, large file handling"
```

### Phase 3: Validate (Memory → Promotion Queue)

Learnings with high confidence and repeated evidence get promoted:

```
┌─────────────────────────────────────────────────────────────┐
│ PROMOTION CRITERIA                                          │
│                                                             │
│  Auto-promote to governance proposal queue when:            │
│  - Same learning captured 2+ times across sessions          │
│  - Confidence >= 0.9                                        │
│  - Has witness/verification defined                         │
│  - Mapped to governance target (AGENTS.md, manifest, etc.)  │
│                                                             │
│  Human review required for:                                 │
│  - AGENTS.md hard gates                                     │
│  - Manifest profile changes                                 │
│  - New playbooks                                            │
└─────────────────────────────────────────────────────────────┘
```

### Phase 4: Merge (Promotion → Governance)

```
┌─────────────────────────────────────────────────────────────┐
│ GOVERNANCE UPDATE WORKFLOW                                  │
│                                                             │
│  1. list_promotions(status: "pending") → review queue       │
│  2. Human reviews proposal                                  │
│  3. If approved:                                            │
│     - Generate PR with governance delta                     │
│     - Update governance file(s)                             │
│     - Mark promotion as "merged"                            │
│  4. If rejected:                                            │
│     - Mark promotion as "rejected" with reason              │
│     - Learning remains in memory (may resurface)            │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 0: Foundation (This PR)

**Goal**: Establish architecture without external dependencies

**Deliverables**:
- [x] This roadmap document
- [ ] Memory Provider Interface specification (`memory-provider-interface.yaml`)
- [ ] Git-native provider implementation (zero dependencies)
- [ ] Extended `agents-manifest.yaml` with memory injection hooks
- [ ] Learning capture schema in `governance-learnings-template.md`

**No Supermemory dependency yet** — pure git-native to validate the loop.

### Phase 1: Local Enhancement

**Goal**: Add semantic retrieval without cloud dependency

**Deliverables**:
- [ ] ChromaDB/LanceDB provider implementation
- [ ] Local embedding model integration
- [ ] CLI tool: `scripts/memory-query.py` for manual retrieval
- [ ] Automated learning capture hook (post-session)

### Phase 2: MCP Integration (Optional)

**Goal**: Enable Supermemory/MCP for cross-LLM memory sharing

**Deliverables**:
- [ ] Supermemory-MCP provider implementation
- [ ] Hybrid provider (MCP + git-native fallback)
- [ ] Privacy controls (what gets synced externally)
- [ ] Cross-session learning retrieval

### Phase 3: Automated Governance Evolution

**Goal**: Close the loop with automated promotion

**Deliverables**:
- [ ] Promotion scoring algorithm
- [ ] PR generation from promotions
- [ ] Governance diff preview
- [ ] Human-in-the-loop approval workflow

---

## Comparison: Supermemory vs Alternatives

| Criteria | Supermemory | Local Vector | Git-Native | Hybrid |
|----------|-------------|--------------|------------|--------|
| Semantic search | Yes | Yes | No | Yes |
| Cross-LLM | Yes (MCP) | No | No | Yes |
| Privacy | Cloud | Full | Full | Configurable |
| Offline | No | Yes | Yes | Yes |
| Audit trail | Limited | Limited | Full | Full |
| Setup effort | Low | Medium | Zero | Medium |
| Dependency | External | Local lib | None | Mixed |

**Recommendation**: Start with **Git-Native** (Phase 0), add **Local Vector** (Phase 1), then **Hybrid with optional Supermemory** (Phase 2) for teams that want cross-LLM capabilities.

---

## Integration Points with Current Governance

### 1. `agents-manifest.yaml` Extension

```yaml
# New section at bottom of manifest
memory:
  enabled: true
  provider_config: .governance/memory-config.yaml

  # When to query memory
  inject_on:
    - task_start           # Before reasoning
    - profile_match        # When a profile matches
    - stuck_loop_reset     # When restarting

  # What to store
  capture:
    learnings: true
    decisions: true
    discoveries: false     # SSOT maps are enough
```

### 2. `docs/project/learning.md` as Git-Native Store

The existing `learning.md` becomes the human-readable git-native store:

```markdown
# Learning Notes

## Captured Learnings

### LEARN-001: Path.glob returns generator
- **Evidence**: Session xyz, file abc.py
- **Confidence**: 0.9
- **Witness**: Unit test `test_glob_list_conversion`
- **Status**: promoted → docs/agents/70-io-data-integrity.md

### LEARN-002: Excel COM requires STA thread
- **Evidence**: Session def, error log
- **Confidence**: 0.8
- **Witness**: Runtime check in excel_lifecycle.py
- **Status**: pending review
```

### 3. Context Injection Procedure Update

Add to `AGENTS.md` "Context Injection Procedure":

```markdown
6) If memory injection is enabled (`agents-manifest.yaml:memory.enabled`):
   - Query memory provider with task-relevant keywords
   - Include top N learnings in context
   - Log which learnings were injected
```

---

## Security & Privacy Considerations

| Concern | Mitigation |
|---------|------------|
| Sensitive data in memory | Filter before storage; no secrets/credentials |
| External provider trust | Use self-hosted Supermemory or local-only |
| Learning pollution | Confidence scoring; human review for promotions |
| Governance drift | Promotions require explicit approval |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Repeat failures | -50% after 30 days |
| Manual governance updates | -30% (auto-promoted) |
| Context relevance | 80% of injected learnings rated useful |
| Time to governance update | <24h for high-confidence learnings |

---

## Next Steps

1. **Approve this roadmap** — align on architecture
2. **Implement Phase 0** — git-native provider, no dependencies
3. **Test learning loop** — 2-week pilot with manual capture
4. **Evaluate Phase 1** — decide if semantic search is needed
5. **Evaluate Phase 2** — decide if Supermemory/MCP adds value

---

## References

- Supermemory: https://github.com/supermemoryai/supermemory
- Supermemory-MCP: https://github.com/supermemoryai/supermemory-mcp
- Model Context Protocol: https://modelcontextprotocol.io
- ChromaDB: https://www.trychroma.com
- LanceDB: https://lancedb.com

---

## Appendix: Why Not Just Use Supermemory Directly?

1. **Vendor lock-in** — If Supermemory changes pricing/API, you're stuck
2. **Privacy** — Some orgs can't use external memory services
3. **Offline** — Development often happens without internet
4. **Auditability** — Git-native provides full history
5. **Governance sovereignty** — Your rules shouldn't depend on external infra

The abstraction layer gives you **freedom to choose** while still benefiting from Supermemory's capabilities when appropriate.
