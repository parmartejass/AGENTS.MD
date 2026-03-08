---
doc_type: reference
ssot_owner: docs/agents/skills/10-platform-adapters.md
update_trigger: collection window changes OR sourced Codex CLI examples are added/removed
---

# LLMJunky Codex CLI Config Snippets (Last 30 Days)

## Source and scope
- Source: X API user timeline for `@LLMJunky`.
- Collection window: `2026-02-03T20:17:53Z` through `2026-03-05T20:17:53Z` UTC.
- Inclusion: only posts by `@LLMJunky` that contained explicit Codex CLI config text in the post body.
- Preservation rule: snippets below keep the source line order and wording from the X API response. Invalid, partial, or speculative fragments are left as-is rather than normalized.

## Exact source-preserved config fragments

### Fast mode
Sources:
- `2026-03-05`: `https://x.com/LLMJunky/status/2029627240074338720`

```toml
fast_mode = true
```

### Artifact feature
Sources:
- `2026-03-04`: `https://x.com/LLMJunky/status/2029077324797550659`

```toml
[features]
artifact = true
```

### Realtime conversation
Sources:
- `2026-03-03`: `https://x.com/LLMJunky/status/2028865543835406781`

```toml
realtime_conversation = true
```

### Ask Question Tool
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027436828534452309`
- `2026-02-27`: `https://x.com/LLMJunky/status/2027443439462207992`

```toml
[features]
default_mode_request_user_input = true
```

Also shared as a root-level one-line fragment:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027252813668000110`

```toml
default_mode_request_user_input = true
```

### Feature bundle
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027424373884277236`

```toml
[features]
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
realtime_conversation = true
prevent_idle_sleep = true
```

### Feature bundle variant
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027423975651889256`

```toml
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
realtime_conversation = true
prevent_idle_sleep = true
default_mode_request_user_input = true
responses_websockets_v2 = true
```

Smaller subset variants were also shared here:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027424751619100959`

```toml
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
realtime_conversation = true
prevent_idle_sleep = true
default_mode_request_user_input = true
```

- `2026-02-27`: `https://x.com/LLMJunky/status/2027423922027712615`

```toml
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
realtime_conversation = true
```

- `2026-02-27`: `https://x.com/LLMJunky/status/2027422648020750646`

```toml
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
prevent_idle_sleep = true
default_mode_request_user_input = true
```

### Minimal memory flags
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027417136709181537`

```toml
memories = true
sqlite = true
```

### Voice transcription
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027251692975088046`

```toml
[features]
voice_transcription = true
```

### Custom agent role
Sources:
- `2026-02-20`: `https://x.com/LLMJunky/status/2024915227721302373`

```toml
  [agents.sparky]
  description = "Spark worker"
  config_file = "/absolute/path/to/sparky.toml"
```

### Agent thread limit
Sources:
- `2026-02-18`: `https://x.com/LLMJunky/status/2024215094268203139`

```toml
[agents]
max_threads = 12
```

### Legacy memory flags
Sources:
- `2026-02-12`: `https://x.com/LLMJunky/status/2021847992555245977`

```toml
memory_tool = true
sqlite = true
```

## Partial, mixed, or speculative source fragments

### Fast mode with companion commands
Sources:
- `2026-03-05`: `https://x.com/LLMJunky/status/2029630921406636311`

```text
fast_mode = true
/fast

codex --enable fast_mode
```

### Agent depth (annotated value, not valid TOML as posted)
Sources:
- `2026-03-03`: `https://x.com/LLMJunky/status/2028687153543192993`

```text
[agents]
max_depth = 2 (or more if you're brave)
```

### Memories tuning (truncated in source post)
Sources:
- `2026-02-28`: `https://x.com/LLMJunky/status/2027811776692097529`

```text
[memories]
max_raw_memories_for_global = 1024
max_rollout_age_days = 30
max_rollouts_per_startup = 8
min_rollout_idle_hours = 12
phase_1_model = "gpt-5.1-codex-mini"
phase_2_model =
```

### Incomplete websocket flag fragment
Sources:
- `2026-02-27`: `https://x.com/LLMJunky/status/2027424050801234225`

```text
unified_exec = true
shell_snapshot = true
undo = true
memories = true
sqlite = true
steer = true
multi_agent = true
voice_transcription = true
realtime_conversation = true
prevent_idle_sleep = true
default_mode_request_user_input = true
responses_websockets_v2 =
```

### Speculative user-input feature flag
Sources:
- `2026-02-25`: `https://x.com/LLMJunky/status/2026700901633737032`

```text
[features] 
user_input_tool = true  
```

### Agent thread/depth alpha snippet (URL appended in source)
Sources:
- `2026-02-20`: `https://x.com/LLMJunky/status/2024647458186240225`

```text
[agents]
max_threads = 12
max_depth = 2 https://t.co/PvCySWSily
```

## Use Cases By Setting
- `artifact`: enable artifact-style outputs such as generated spreadsheet or presentation artifacts.
- `config_file`: point a named agent role at a separate TOML file that holds that role's model and reasoning config.
- `default_mode_request_user_input`: allow the Ask Question / interview-style tool outside plan mode when the model truly needs clarification.
- `description`: attach a human-readable purpose to a custom agent role.
- `fast_mode`: switch to a faster, lower-deliberation workflow for quick iteration, debugging, or smaller coding tasks.
- `max_depth`: control how many layers deep subagents or teams can recurse.
- `max_raw_memories_for_global`: cap how many raw memories are considered when building or backfilling global memory.
- `max_rollout_age_days`: stop memory backfill from considering rollout history older than the configured age.
- `max_rollouts_per_startup`: limit how many old rollouts are processed each time Codex starts.
- `max_threads`: raise or lower the amount of concurrent agent work when using teams or multi-agent flows.
- `memories`: turn on memory storage/recall features.
- `memory_tool`: apparent legacy switch for the earlier memory tool implementation.
- `min_rollout_idle_hours`: avoid processing very recent rollouts until they have been idle long enough.
- `multi_agent`: enable multi-agent orchestration and team-style workflows.
- `phase_1_model`: choose the model used for the first memory-processing phase.
- `phase_2_model`: apparent placeholder for the second memory-processing phase model; the shared source fragment was incomplete.
- `prevent_idle_sleep`: keep the machine awake during long-running Codex sessions or agent work.
- `realtime_conversation`: enable live conversational interaction instead of purely turn-based prompting.
- `responses_websockets_v2`: apparent switch for a newer websocket-based response transport; source fragment was incomplete in one post.
- `shell_snapshot`: preserve shell/session state between actions so follow-up steps can build on prior terminal context.
- `sqlite`: use local SQLite-backed storage, typically alongside memory features.
- `steer`: enable steering controls or steering-related orchestration behavior for the session.
- `unified_exec`: use the unified execution path for terminal or tool execution.
- `undo`: allow reverting or undoing recent actions during an interactive workflow.
- `user_input_tool`: apparent earlier or speculative name for the Ask Question capability before the later `default_mode_request_user_input` flag.
- `voice_transcription`: enable voice input or dictation.

## Explicitly skipped non-TOML mentions
- `SKIPPED_NON_TEXT_MEDIA`: `2026-03-04` `https://x.com/LLMJunky/status/2029063622895243414`
- `SKIPPED_NON_TEXT_MEDIA`: `2026-03-04` `https://x.com/LLMJunky/status/2029063620957503716`
- `SKIPPED_NON_TOML_PATH_ONLY`: `2026-02-22` `https://x.com/LLMJunky/status/2025637547401961938`
- `SKIPPED_NON_TOML_PATH_ONLY`: `2026-02-12` `https://x.com/LLMJunky/status/2022081189687992338`
