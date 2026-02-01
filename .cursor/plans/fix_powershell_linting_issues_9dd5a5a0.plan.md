---
name: Fix PowerShell Linting Issues
overview: "Fix 8 PSScriptAnalyzer warnings across 2 files: rename `$args` variables to avoid shadowing the automatic variable, and rename 3 functions to use approved PowerShell verbs."
todos:
  - id: fix-automation-lib
    content: Fix $Args param, $args variable, and 3 function names in automation-lib.ps1
    status: completed
  - id: fix-implement
    content: Fix $args variable in implement.ps1
    status: completed
  - id: update-callers
    content: Update function call sites in implement.ps1 and review.ps1
    status: completed
  - id: verify
    content: Verify 0 linting warnings remain
    status: pending
isProject: false
---

# Fix PowerShell Linting Issues

## Changes Required

### 1. [automation-lib.ps1](templates/automation-loop/automation-lib.ps1) - 6 fixes

**Rename `$Args` parameter and usages in `Invoke-Git` (lines 102, 105, 107):**

- `$Args` -> `$GitArgs`

**Rename `$args` variable in `Invoke-Agent` (lines 192, 194, 196, 206, 209, 214):**

- `$args` -> `$runnerArgs`

**Rename functions to use approved verbs:**

- `Ensure-Directory` -> `Initialize-Directory` (line 69)
- `Ensure-RepoClean` -> `Assert-RepoClean` (line 111)
- `Render-Prompt` -> `Format-Prompt` (line 158)

### 2. [implement.ps1](templates/automation-loop/implement.ps1) - 2 fixes

**Rename `$args` variable (lines 55, 57, 59):**

- `$args` -> `$ghArgs`

### 3. Update Callers

After renaming functions, update all call sites in:

- [implement.ps1](templates/automation-loop/implement.ps1) - calls `Ensure-Directory`, `Ensure-RepoClean`, `Render-Prompt`
- [review.ps1](templates/automation-loop/review.ps1) - calls `Ensure-Directory`, `Ensure-RepoClean`, `Render-Prompt`

## Verification

Run PSScriptAnalyzer or re-open files in Cursor to confirm 0 warnings.
