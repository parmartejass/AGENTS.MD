param(
  [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")

$defaultGovernanceRoot = Split-Path -Parent $PSScriptRoot
$defaultRepoRoot = Split-Path -Parent $defaultGovernanceRoot

$effectiveRepoRoot = $defaultRepoRoot
if ($RepoRoot -and $RepoRoot.Trim()) {
  $effectiveRepoRoot = $RepoRoot
}

$context = Get-GovernanceContext `
  -RepoRoot $effectiveRepoRoot `
  -GovernanceRoot $defaultGovernanceRoot `
  -ScriptRoot $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($context.GovernanceRelPath)) {
  throw "Cannot determine governance submodule path from repo root."
}

if ($context.GovernanceRelPath -match '^\.\.') {
  throw "Governance root must be inside the repo root."
}

$gitModulesPath = Join-Path $context.RepoRoot ".gitmodules"
if (-not (Test-Path $gitModulesPath -PathType Leaf)) {
  throw "No .gitmodules found at repo root: $gitModulesPath"
}

git -C $context.RepoRoot submodule update --init --remote $context.GovernanceRelPath

Write-Host "Governance submodule updated at: $($context.GovernanceRelPath)"
Write-Host "If there are changes, commit the pointer:"
Write-Host "  git -C $($context.RepoRoot) add $($context.GovernanceRelPath)"
