---
doc_type: runbook
ssot_owner: AGENTS.md
update_trigger: execution-loop rules change OR new recurring AI failure patterns emerge
---

# 15 - Stuck in Loop: Generate a Fresh Restart Prompt

This is supporting guidance. The normative rules live in `AGENTS.md` (Prime Directive + Mandatory Execution Loop).

## Use this runbook when
- repeated failures suggest a stuck loop (same error/bug reintroduced)
- long threads risk context drift (requirements missing/changed)
- output "looks right" but verification contradicts it (phantom compliance)

## Stuck-loop reset protocol (must be deterministic)
1) Re-run the `AGENTS.md` Mandatory Execution Loop steps 1-5 explicitly:
   - restate goal + acceptance criteria
   - discover files and SSOT owners
   - decompose into atomic subtasks
   - run subagent council and reconcile findings
   - run ambiguity gate (ask clarifying questions only if material ambiguity remains)
2) Reproduce/verify the failure with deterministic tools; capture the exact command + output.
   Use README.md "Checks" (SSOT) when available.
3) Populate the Restart Prompt Template below and present it as a copy-pasteable restart prompt.
4) Restart in a fresh chat/model using that prompt, then re-attempt implementation minimally and re-run verification.

### Restart Prompt Template (fill, then present as copy/paste)
Filling rules (to prevent hallucinated context):
- Goal/acceptance criteria come from the current conversation.
- Repo facts must be verified (paths/symbols/config keys/commands). If not verified, write `Unknown`.
- Prefer linking to SSOT owners by path (do not duplicate constants/rules in the prompt).
- Keep constraints to the ones that apply (Excel COM, GUI threading, security, etc.).
- Include learned context so the restart does not repeat dead ends (attempt history + verified failure evidence).
- If restarting without repo file access, include/paste `AGENTS.md` (authoritative) and any relevant file excerpts.

Output format (copy/paste block):
```
Here's your restart prompt (copy/paste into a new chat/model):

Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.

Goal:
Acceptance criteria:
-

Why restarting (current failure evidence):
-

Defect vocabulary (for bug/error work):
  (use `AGENTS.md` "First-Principles Protocol (Hard Gate)" -> "Defect vocabulary")
- Symptom/manifestation:
- Root-cause hypothesis:
- Blast radius:

Previous attempts and why they failed:
- Attempt 1:
- Attempt 2:

Key insights learned:
-

Do NOT retry (known bad approaches/assumptions):
-

Repo discovery notes (verified files/symbols/SSOT owners):
-

Applicable constraints (from `AGENTS.md`):
-

Verification commands (exact):
-

Bugfix evidence to carry forward (if applicable):
- MRE witness (fail before / pass after):
- Regression test:
- Disconfirming test:
- Failure-path check:

Open questions / Unknowns:
-
```

Example (format only; paths/symbols are illustrative):
```
Here's your restart prompt (copy/paste into a new chat/model):

Hard gates:
- Read and follow `AGENTS.md` (SSOT). If you cannot access it, request it before doing any work.

Goal: Add Excel validation for duplicate invoice IDs
Acceptance criteria:
- Check column B for duplicates before processing
- Log SKIPPED + reason when found
- Raise ValidationError with duplicate IDs listed

Why restarting (current failure evidence):
- pytest tests/test_invoice_validation.py -> FAIL (duplicates not detected); see assertion output in test log

Previous attempts and why they failed:
- Attempt 1: validated after processing -> too late; test expects pre-check + skip
- Attempt 2: checked the wrong column -> verification still fails on duplicates

Key insights learned:
- The duplicate check must run before any downstream processing and must emit SKIPPED + reason

Do NOT retry (known bad approaches/assumptions):
- Do not move the duplicate check after processing
- Do not infer the invoice-id column; use the SSOT header mapping

Repo discovery notes (verified files/symbols/SSOT owners):
- SSOT: src/constants.py (SHEET_NAMES, HEADER_COLUMNS)
- Validation: src/validators/invoice.py

Applicable constraints (from `AGENTS.md`):
- Use module-level logging (no print)
- Excel COM must not run on UI thread

Verification commands (exact):
- pytest tests/test_invoice_validation.py

Open questions / Unknowns:
- None
```

## Review checklist (prevent silent errors)
- Verify behavior with the tightest available commands (tests/lint/run); prefer repo scripts over ad-hoc checks.
- Confirm failures are explicit (logged + raised), not silently skipped (`AGENTS.md` "Logging + Explicit Failure").
- Scan for security regressions relevant to the change (input validation, injection surfaces, secret handling).
- Scan for resource leaks relevant to the change (files, subprocesses, Excel COM, UI threads).
- Scan for performance regressions when perf is relevant (timing or complexity reasoning).

## Model/tool switching (optional)
If your platform supports it, switching models can break repetition loops; otherwise,
restarting with a fresh prompt is usually enough.
