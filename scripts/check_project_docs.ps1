param(
  [string]$RepoRoot,
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

# Validates that minimal project docs exist and are reachable from README.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_project_docs.ps1

$repoRoot = $context.RepoRoot

$governancePrefix = ""
if (-not [string]::IsNullOrWhiteSpace($context.GovernanceRelPath)) {
  $governancePrefix = $context.GovernanceRelPath.TrimEnd("/") + "/"
}

$issues = New-Object System.Collections.Generic.List[string]

function Add-Issue([System.Collections.Generic.List[string]]$list, [string]$message) {
  $list.Add($message)
}

$requiredFiles = @(
  "README.md",
  "docs/project/index.md",
  "docs/project/goal.md",
  "docs/project/rules.md",
  "docs/project/architecture.md",
  "docs/project/learning.md"
)

foreach ($rel in $requiredFiles) {
  $full = Join-Path $repoRoot $rel
  if (-not (Test-Path $full -PathType Leaf)) {
    Add-Issue $issues "Missing required file: $rel"
  }
}

if ((Join-Path $repoRoot "README.md") | Test-Path) {
  $readmeText = Get-Content -Raw -Path (Join-Path $repoRoot "README.md")
  $requiredReadmeRefs = @(
    "docs/project/index.md",
    "AGENTS.md",
    "${governancePrefix}scripts/check_docs_ssot.ps1",
    "${governancePrefix}scripts/check_agents_manifest.ps1",
    "${governancePrefix}scripts/check_project_docs.ps1",
    "${governancePrefix}scripts/check_repo_hygiene.ps1",
    "${governancePrefix}scripts/check_change_records.ps1",
    "${governancePrefix}scripts/check_python_safety.py"
  )

  foreach ($ref in $requiredReadmeRefs) {
    if ($readmeText -notlike "*$ref*") {
      Add-Issue $issues "README.md must reference: $ref"
    }
  }
}

if ((Join-Path $repoRoot "docs/project/index.md") | Test-Path) {
  $indexText = Get-Content -Raw -Path (Join-Path $repoRoot "docs/project/index.md")
  foreach ($ref in @("docs/project/goal.md", "docs/project/rules.md", "docs/project/architecture.md", "docs/project/learning.md")) {
    if ($indexText -notlike "*$ref*") {
      Add-Issue $issues "docs/project/index.md must reference $ref"
    }
  }
}

if ($issues.Count -gt 0) {
  foreach ($issue in $issues) {
    Write-Host "ERROR: $issue"
  }
  throw "Project docs check failed: $($issues.Count) issue(s)."
}

Write-Host "Project docs checks passed."
