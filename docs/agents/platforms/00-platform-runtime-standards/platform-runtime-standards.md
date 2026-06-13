---
doc_type: policy
ssot_owner: docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md
update_trigger: verified platform runtime paths, support levels, setup flow, or projection modes change
---

# Platform Runtime Standards (SSOT)

## Purpose
- This doc owns the cross-platform runtime projection model for repo-owned agent assets.
- Policy lives here; concrete path/runtime facts live in `docs/agents/platforms/runtime-projections.json`.
- Dated external evidence lives under `docs/agents/platforms/<platform>/`.

## Model
- Canonical non-secret assets stay under `docs/agents/`.
- Runtime folders/files under repo dotpaths or user-home dotpaths are projections only.
- A projection may be a direct link or a manual/snippet-only surface when the platform mixes repo config with user-local state.

## Path resolution
- Relative `source_root` and `source_preference` values in `docs/agents/platforms/runtime-projections.json` resolve from the governance root.
- Relative `source_path` values in `docs/agents/platforms/runtime-projections.json` resolve from the governance root.
- Relative `target_root` and `target_path` values resolve from the project root after `{HOME}` expansion when present.
- This split is mandatory so the same governance pack works both as the top-level repo and when vendored under `.governance/`.

## Support Levels
- `official`: verified against current official platform docs and safe to manage through the repo setup flow.
- `manual`: verified surface exists, but repo automation must not replace it wholesale because the file mixes user-local state or secrets.
- `unsupported`: no verified runtime contract exists for automated projection, so setup must emit `SKIPPED + reason`.
- `reserved`: no verified runtime contract is adopted yet.

## Projection Modes
- Concrete mode tokens live in `docs/agents/platforms/runtime-projections.json` and are consumed by `docs/agents/link_repo_assets.ps1`.
- Linked directory modes: `child_directory_links`
- Linked file modes: `mcp_file_link`, `settings_file_link`
- Explicit no-op mode: `skip` (emit `SKIPPED + reason` instead of replacing a runtime file)

## Invariants
- One concrete runtime-mapping authority: `docs/agents/platforms/runtime-projections.json`.
- Mixed user config files are never replaced wholesale by repo automation.
- Unsupported or unverified mappings must emit `SKIPPED + reason`.
- Platform-doc snapshots are recorded evidence only; they justify mappings but do not replace the manifest or linker logic.

## Multi-Agent Orchestration Runtimes
- External orchestration runtimes (e.g., Paperclip) may consume the same repo-owned agent assets (skills, instructions, settings, MCP configs) and project them across multiple backend runtimes (Claude Code, Codex, OpenClaw, etc.).
- Orchestration runtimes are not projection targets; they are consumers of the canonical `docs/agents/` assets via their own import mechanism.
- This repo does not auto-project into orchestration runtimes; their integration is manual and documented outside the projection manifest.

## Bootstrap Contract
- One setup entrypoint owns runtime projection repair: `scripts/setup_repo_platform_assets.ps1`.
- Fresh clone on a new machine is supported by rerunning the setup entrypoint; passive cross-device symlink portability is not assumed.
- Repo-local targets should prefer relative links where possible. User-home targets may require rerun-on-move behavior.

## Editing Rule
- Edit canonical repo-owned assets under their declared source roots in `docs/agents/**`.
- Do not edit runtime projection paths as authorities.
- If a platform contract changes, update this doc, `docs/agents/platforms/runtime-projections.json`, the relevant dated platform note, and `docs/agents/link_repo_assets.ps1` together.
