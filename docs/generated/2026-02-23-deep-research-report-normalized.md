---
doc_type: generated
ssot_owner: docs/project/learning.md
update_trigger:
  - deep-research-report.md source content changes
  - governance decisions in docs/project/learning.md change
---

# Normalized Deep Research Report (2026-02-23)

## Source and trust status
- Source input: `deep-research-report.md` at repository root.
- Trust level: `[CONTEXT: UNTRUSTED]` until validated against repository SSOT and checks.
- Normalization goal: retain only governance-improvement deltas that map to existing authorities.

## Repo-validated deltas
1. Expand governance context injection for complete reviews.
- Authority owner: `agents-manifest.yaml` (`profiles.governance_improvement.inject`).
- Why: governance reviews require README checks and project learning context.

2. Enforce change-record evidence in cross-platform core checks.
- Authority owner: `scripts/check_governance_core.py`.
- Why: core governance check previously omitted change-record validation.

3. Prevent prompt-pack drift in governance learnings playbook.
- Authority owner: `docs/agents/playbooks/governance-learnings-template.md`.
- Why: hard-gate duplication can diverge silently without parity checks.

4. Treat unresolved citation placeholders as invalid in governed docs.
- Authority owner: `scripts/check_governance_core.py` docs checks.
- Why: placeholders are non-auditable recorded truth.

## Deliberately not adopted as new authority
- Generic framework narratives (PDCA/OODA/Scrum/FMEA overviews) were not copied into policy docs.
- New parallel templates were not introduced where equivalent SSOT already exists in `AGENTS.md` and existing playbooks.
- No new governance SSOT owner was created.

## Verification witnesses
- `python3 scripts/check_governance_core.py`
- `python3 scripts/check_governance_core.py --require-records`
- `python3 scripts/check_governance_core.py --fail-on-safety-warnings`

