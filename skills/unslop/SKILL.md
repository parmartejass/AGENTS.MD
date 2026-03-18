---
name: unslop
description: Use this skill when you need to run the unslop repo, analyze a domain for repetitive AI defaults, generate a reusable skill file, and verify that the output is specific and materially different from the baseline.
---

# unslop

Use this repo to generate a domain-specific profile that removes repetitive AI defaults.

## Workflow

1. Clone `https://github.com/mshumer/unslop` if the repo is not already present.
2. Enter the repo root and use a Python virtual environment.
3. Decide whether the job is `text` or `visual`.
   Text: writing, emails, essays, tutorials, copy, code explanations.
   Visual: websites, landing pages, HTML pages, UI mockups.
4. Install Playwright only for visual runs:
   `pip install playwright && playwright install chromium`
5. Run the tool:
   `python3 unslop.py --domain "<domain>"`
   `python3 unslop.py --domain "<domain>" --type visual --count 20 --concurrency 3`

## Output Review

Check `unslop-output/analysis.md` and `unslop-output/skill.md`.

- `analysis.md` must be concrete, counted, and specific.
- `skill.md` should mostly say what to avoid, not prescribe one new stock style.
- For visual runs, compare `unslop-output/before-after/before.html` and `unslop-output/before-after/after.html`.
- The `after` result should feel meaningfully less generic than `before`.

If the analysis is thin or obviously missed repeated patterns, rerun or rewrite the analysis from inside `unslop-output` after reviewing the screenshots and sample files directly.

## Deliverable

Return:

- The generated `skill.md`
- The main repeated patterns the analysis found
- Any caveats about sample quality, missing screenshots, or weak comparison output
