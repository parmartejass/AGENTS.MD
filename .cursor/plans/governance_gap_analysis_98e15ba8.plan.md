---
name: Governance Gap Analysis
overview: Comprehensive analysis of missing best practices and fundamentals in the AGENTS.MD governance framework, based on 2025-2026 AI agent governance advancements and industry standards.
todos:
  - id: safety-prompt-injection
    content: Create docs/agents/45-prompt-injection-defense.md with threat model and defense patterns
    status: pending
  - id: safety-sandboxing
    content: Add Sandboxing/Isolation section to AGENTS.md Non-Negotiables
    status: pending
  - id: safety-hitl-escalation
    content: Create docs/agents/55-human-escalation-tiers.md with risk classification and approval requirements
    status: pending
  - id: safety-rollback
    content: Extend Workflow State Machine in AGENTS.md with CHECKPOINT phase and rollback procedures
    status: pending
  - id: orchestration-multi-agent
    content: Create docs/agents/56-multi-agent-orchestration.md with coordination patterns
    status: pending
  - id: orchestration-conflict
    content: Add conflict resolution process to Subagent Council section
    status: pending
  - id: observability-telemetry
    content: Extend docs/agents/30-logging-errors.md with OpenTelemetry-compatible tracing
    status: pending
  - id: observability-token-budget
    content: Create docs/agents/42-token-budget-management.md
    status: pending
  - id: quality-evaluation
    content: Create docs/agents/95-agent-evaluation.md with metrics framework
    status: pending
  - id: integration-mcp
    content: Create docs/agents/skills/15-mcp-integration.md
    status: pending
  - id: integration-tool-interface
    content: Add Tool Interface Standards to AGENTS.md Non-Negotiables
    status: pending
  - id: polish-examples
    content: Add code examples to 35-authority-bounded-modules.md, 40-config-constants.md, 60-gui-threading.md
    status: pending
  - id: polish-testing
    content: Expand docs/agents/80-testing-real-files.md with fixture patterns and CI guidance
    status: pending
  - id: polish-release
    content: Expand docs/agents/90-release-checklist.md with versioning and deployment
    status: pending
isProject: false
---

# AGENTS.MD Gap Analysis: Missing Best Practices (Feb 2026)

Based on analysis of the current governance framework and research into the latest 2025-2026 advancements in AI agent governance, this plan identifies missing fundamentals organized by priority.

---

## Current Framework Strengths

The AGENTS.MD framework already covers these areas well:

- **SSOT Principles**: Strong single source of truth governance
- **First-Principles Protocol**: Model-Proof-Change methodology
- **Authority-First Debugging**: Root cause uplift, bias-resistant debugging
- **Verification Floors**: Deterministic verification requirements
- **Domain-Specific Safety**: Excel COM lifecycle, GUI threading
- **Subagent Council**: Multi-perspective review before changes
- **Change Contracts**: Structured invariant/witness documentation

---

## Category 1: Agentic Safety and Security (HIGH PRIORITY)

### 1.1 Prompt Injection Defense

**Gap**: No guidance on protecting agents from indirect prompt injection attacks embedded in tool outputs or retrieved content.

**2025-2026 State**: Frameworks like MELON, RTBAS, and PromptArmor now provide principled defenses:

- Masked re-execution to detect malicious redirects
- Information Flow Control for tool-based agents
- Pre-processing filters to remove injected prompts

**Recommendation**: Add a new doc `docs/agents/45-prompt-injection-defense.md` covering:

- Threat model: indirect injection via tool outputs, retrieved docs, user inputs
- Defense patterns: input sanitization, output validation, re-execution verification
- Tool output trust boundaries
- Escalation when suspicious content detected

### 1.2 Sandboxing and Isolation Boundaries

**Gap**: No guidance on execution sandboxing for tool operations (file writes, shell commands, network calls).

**2025-2026 State**: Claude Code, Docker Sandboxes, GKE Agent Sandbox, and Koyeb provide production sandboxing:

- Filesystem isolation to specific directories
- Network allow-lists
- Container/microVM isolation for untrusted code

**Recommendation**: Add sandboxing section to [AGENTS.md](AGENTS.md) Non-Negotiables:

- Define isolation boundaries per tool type
- Allowlist approach for filesystem/network access
- Sandbox verification as part of verification floors

### 1.3 Human-in-the-Loop Escalation Tiers

**Gap**: Subagent council provides review but no formal escalation tiers for high-risk operations before execution.

**2025-2026 State**: LangGraph, OpenAI Agents SDK, and Semantic Kernel use interrupt-based HITL with risk classification:

- Tiered approval requirements based on risk level
- Approval channels (sync/async)
- State preservation during interrupts

**Recommendation**: Add `docs/agents/55-human-escalation-tiers.md`:

- Risk classification framework (reversibility, data sensitivity, cost)
- Approval requirements by tier
- Interrupt/resume patterns for agent workflows
- Audit logging for all approvals/rejections

### 1.4 Rollback and Undo Mechanisms

**Gap**: Rewrite risk policy mentions staged rollout but no formal rollback procedures or checkpointing.

**2025-2026 State**: IBM's STRATUS uses "Transactional No-Regression" (TNR); SAFEFLOW uses write-ahead logging:

- Checkpointing before risky operations
- Write-ahead logging for reversibility
- Automated rollback to known-good states

**Recommendation**: Extend workflow state machine section in [AGENTS.md](AGENTS.md):

- Add CHECKPOINT phase before COMMIT_READY
- Rollback procedures for each failure phase
- Checkpoint retention and cleanup policy

---

## Category 2: Multi-Agent Orchestration (MEDIUM-HIGH PRIORITY)

### 2.1 Multi-Agent Coordination Patterns

**Gap**: Subagent council is review-only; no patterns for parallel/sequential agent execution or task delegation.

**2025-2026 State**: AWS Multi-Agent Orchestrator, Semantic Kernel, OpenAI Swarm provide:

- Intent classification for routing
- Parallel vs sequential execution patterns
- Context management across agents

**Recommendation**: Add `docs/agents/56-multi-agent-orchestration.md`:

- Coordination patterns: sequential, parallel, hierarchical
- Intent-based routing
- Context aggregation and handoff
- Failure isolation between agents

### 2.2 Agent Handoff Protocols

**Gap**: No guidance on how context should be passed between agents or what handoff semantics apply.

**Recommendation**: Include in orchestration doc:

- Handoff context schema (task, constraints, partial results, relevant files)
- Minimal context principle (avoid passing full conversation history)
- Explicit ownership transfer semantics

### 2.3 Conflict Resolution

**Gap**: No formal process when subagent council members disagree on findings.

**Recommendation**: Add conflict resolution section to Subagent Council:

- Escalation to human when council findings conflict
- Weighted voting for non-critical disagreements
- Required consensus for high-risk changes

---

## Category 3: Observability and Monitoring (MEDIUM PRIORITY)

### 3.1 Agent Telemetry and Tracing

**Gap**: Standard log schema exists but lacks OpenTelemetry semantic conventions and agent-specific tracing.

**2025-2026 State**: OpenTelemetry GenAI Semantic Conventions, Azure AI Foundry tracing, AgentOps:

- Standardized trace formats for agent operations
- Tool usage, retries, latencies, costs per operation
- Session replay capabilities

**Recommendation**: Extend `docs/agents/30-logging-errors.md`:

- OpenTelemetry-compatible trace schema
- Per-tool operation logging (input hash, output hash, duration, cost estimate)
- Session/run correlation IDs
- Optional integration points for AgentOps/similar

### 3.2 Token Budget and Cost Management

**Gap**: No guidance on token budgets, cost controls, or context window management.

**2025-2026 State**: Google BATS framework, OpenAI usage tracking:

- Per-request token tracking
- Budget caps and throttling
- Context compression strategies

**Recommendation**: Add `docs/agents/42-token-budget-management.md`:

- Token budget estimation per task type
- Context compression strategies (summarization, truncation, RAG)
- Cost monitoring and alerting thresholds
- Guardrails for runaway token consumption

### 3.3 Context Window Management

**Gap**: No guidance on handling context accumulation in long-running multi-step tasks.

**2025-2026 State**: "Lost in the middle" problem well-documented; best practices emerging:

- Explicit token budgets per step
- Strategic truncation of old context
- Summarization of tool outputs
- Automatic context clearing

**Recommendation**: Include in token budget doc:

- Context accumulation patterns and risks
- When to summarize vs truncate
- Priority ordering for context retention
- Detecting silent context overflow

---

## Category 4: Evaluation and Quality (MEDIUM PRIORITY)

### 4.1 Agent Evaluation Metrics

**Gap**: No benchmarks or quality metrics for measuring agent performance.

**2025-2026 State**: SWE-Bench Pro, LoCoBench-Agent, ProjectEval:

- Task completion rate
- Comprehension vs efficiency trade-offs
- Error recovery patterns
- Multi-turn interaction quality

**Recommendation**: Add `docs/agents/95-agent-evaluation.md`:

- Standard metrics: task success rate, verification pass rate, council finding rate
- Efficiency metrics: tool calls per task, context usage, time to completion
- Quality signals: code review acceptance rate, regression rate
- Evaluation cadence (per session, per project)

### 4.2 Reproducibility and Provenance

**Gap**: Determinism mentioned but no formal provenance tracking.

**2025-2026 State**: PROV-AGENT, MLflow LoggedModel:

- W3C PROV-based provenance for agent workflows
- Version tracking for prompts, configs, traces
- Linking traces to specific application versions

**Recommendation**: Extend Change Contract template:

- Add provenance section: model version, prompt hash, config snapshot
- Link run_id to full trace for post-hoc analysis
- Guidance on seed/temperature settings for reproducibility

---

## Category 5: Integration Standards (MEDIUM PRIORITY)

### 5.1 Model Context Protocol (MCP) Integration

**Gap**: No guidance on MCP integration despite MCP becoming an industry standard.

**2025-2026 State**: MCP Best Practices Guide covers:

- Single responsibility per server
- Contracts-first design
- Stateless by default
- Gateway patterns for enterprise

**Recommendation**: Add `docs/agents/skills/15-mcp-integration.md`:

- When to use MCP vs direct tool integration
- Server design principles aligned with authority boundaries
- Security requirements for MCP servers
- Testing MCP integrations

### 5.2 Tool Interface Standards

**Gap**: No formal tool interface contracts or least-privilege patterns.

**2025-2026 State**: AgenTRIM focuses on tool risk mitigation:

- Offline verification of tool interfaces
- Runtime enforcement of least-privilege
- Tool capability allowlisting

**Recommendation**: Add tool interface section to [AGENTS.md](AGENTS.md):

- Tool capability declaration requirements
- Least-privilege principle for tool access
- Tool output validation requirements
- Side-effect disclosure

---

## Category 6: Implementation Completeness (LOWER PRIORITY)

These gaps were identified by the explore agents analyzing existing docs:

### 6.1 Code Examples

**Gap**: Most policy docs lack concrete implementation examples.

**Recommendation**: Add example code blocks to:

- [docs/agents/35-authority-bounded-modules.md](docs/agents/35-authority-bounded-modules.md): contract definition example
- [docs/agents/40-config-constants.md](docs/agents/40-config-constants.md): config schema validation example
- [docs/agents/60-gui-threading.md](docs/agents/60-gui-threading.md): queue/drain pattern example

### 6.2 Testing Guidance Depth

**Gap**: [docs/agents/80-testing-real-files.md](docs/agents/80-testing-real-files.md) lacks test structure and fixture patterns.

**Recommendation**: Expand with:

- Test directory structure conventions
- Fixture creation and maintenance patterns
- Golden file testing patterns
- CI integration guidance

### 6.3 Platform Diversity

**Gap**: GUI threading focuses on Tkinter only.

**Recommendation**: Add framework notes to [docs/agents/60-gui-threading.md](docs/agents/60-gui-threading.md):

- PyQt/PySide queue patterns
- wxPython equivalent patterns
- Or mark as "Tkinter-specific; extend for other frameworks as needed"

### 6.4 Release Process

**Gap**: [docs/agents/90-release-checklist.md](docs/agents/90-release-checklist.md) lacks versioning and deployment.

**Recommendation**: Add sections for:

- Semantic versioning guidance
- Changelog generation
- Deployment verification steps
- Rollback procedures post-release

---

## Summary Priority Matrix


| Priority | Area                      | New Docs/Sections                             |
| -------- | ------------------------- | --------------------------------------------- |
| HIGH     | Prompt Injection Defense  | `docs/agents/45-prompt-injection-defense.md`  |
| HIGH     | Sandboxing                | Add to Non-Negotiables                        |
| HIGH     | HITL Escalation           | `docs/agents/55-human-escalation-tiers.md`    |
| HIGH     | Rollback/Undo             | Extend workflow state machine                 |
| MED-HIGH | Multi-Agent Orchestration | `docs/agents/56-multi-agent-orchestration.md` |
| MED-HIGH | Conflict Resolution       | Extend Subagent Council                       |
| MED      | Agent Telemetry           | Extend `30-logging-errors.md`                 |
| MED      | Token Budget Management   | `docs/agents/42-token-budget-management.md`   |
| MED      | Agent Evaluation          | `docs/agents/95-agent-evaluation.md`          |
| MED      | MCP Integration           | `docs/agents/skills/15-mcp-integration.md`    |
| MED      | Tool Interface Standards  | Add to Non-Negotiables                        |
| LOW      | Code Examples             | Update existing docs                          |
| LOW      | Testing Depth             | Expand `80-testing-real-files.md`             |
| LOW      | Release Process           | Expand `90-release-checklist.md`              |


---

## Implementation Approach

1. **Phase 1 (Safety-Critical)**: Items 1.1-1.4 - These address security and reversibility gaps that could cause real harm
2. **Phase 2 (Orchestration)**: Items 2.1-2.3 - Enable more sophisticated multi-agent patterns
3. **Phase 3 (Observability)**: Items 3.1-3.3 - Improve monitoring and cost control
4. **Phase 4 (Quality)**: Items 4.1-4.2 - Add evaluation and reproducibility
5. **Phase 5 (Polish)**: Items 5.1-5.2, 6.1-6.4 - Integration standards and doc completeness

