$ErrorActionPreference = "Stop"

# Lightweight repo hygiene checks for common generated artifacts that should not be tracked.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1

$repoRoot = Split-Path -Parent $PSScriptRoot

function Add-Issue([System.Collections.Generic.List[string]]$issues, [string]$message) {
  $issues.Add($message)
}

$issues = New-Object System.Collections.Generic.List[string]

try {
  $tracked = git -C $repoRoot ls-files
} catch {
  throw "git is required for hygiene checks."
}

foreach ($path in $tracked) {
  if ($path -match '(^|/)__pycache__(/|$)') {
    Add-Issue $issues "Tracked Python cache dir/file: $path"
    continue
  }

  if ($path.EndsWith(".pyc") -or $path.EndsWith(".pyo")) {
    Add-Issue $issues "Tracked Python bytecode: $path"
    continue
  }

  if ($path -match '(^|/)\.DS_Store$' -or $path -match '(^|/)Thumbs\.db$') {
    Add-Issue $issues "Tracked OS noise file: $path"
    continue
  }

  if ($path -like "templates/python-dual-entry/tests/output/*" -and $path -ne "templates/python-dual-entry/tests/output/.gitkeep") {
    Add-Issue $issues "Tracked template output file (should be generated/ignored): $path"
    continue
  }
}

if ($issues.Count -gt 0) {
  foreach ($issue in $issues) {
    Write-Host "ERROR: $issue"
  }
  throw "Repo hygiene check failed: $($issues.Count) issue(s)."
}

Write-Host "Repo hygiene checks passed."
