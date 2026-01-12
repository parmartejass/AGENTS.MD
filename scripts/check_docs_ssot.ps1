$ErrorActionPreference = "Stop"

$docsRoot = "docs"
$agentsDocsRoot = Join-Path $docsRoot "agents"

if (-not (Test-Path $docsRoot -PathType Container)) {
  Write-Host "No docs/ folder found. Skipping docs SSOT checks."
  exit 0
}

if (-not (Test-Path $agentsDocsRoot -PathType Container)) {
  throw "docs/agents/ missing. This repo expects governance docs there."
}

$files = Get-ChildItem -Path $agentsDocsRoot -Recurse -Filter "*.md" -File
$issues = 0

foreach ($file in $files) {
  if ($file.Name -eq "index.md") { continue }

  $head = Get-Content -Path $file.FullName -TotalCount 25

  if (-not ($head | Select-String -Pattern '^doc_type:' -Quiet)) {
    Write-Host "ERROR: Missing doc header (doc_type) in: $($file.FullName)"
    $issues++
  }
  if (-not ($head | Select-String -Pattern '^ssot_owner:' -Quiet)) {
    Write-Host "ERROR: Missing doc header (ssot_owner) in: $($file.FullName)"
    $issues++
  }
  if (-not ($head | Select-String -Pattern '^update_trigger:' -Quiet)) {
    Write-Host "ERROR: Missing doc header (update_trigger) in: $($file.FullName)"
    $issues++
  }
}

if ($issues -gt 0) {
  throw "Docs SSOT header check failed: $issues issue(s)."
}

# Soft guardrail: warn on "defaults tables" language (common drift source).
$warnMatches =
  Get-ChildItem -Path $docsRoot -Recurse -File |
  Where-Object { $_.FullName -notmatch '[\\/]generated[\\/]' } |
  Select-String -Pattern 'defaults?:\s*$|default value' -ErrorAction SilentlyContinue

if ($warnMatches) {
  Write-Warning "Docs mention defaults/default value. Ensure docs reference config keys by identifier, not copied literal values."
}

Write-Host "Docs SSOT checks passed."
