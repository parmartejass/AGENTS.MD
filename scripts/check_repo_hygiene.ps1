param(
  [string]$RepoRoot,
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

$repoRootProvided = $PSBoundParameters.ContainsKey('RepoRoot')
$governanceRootName = Split-Path -Leaf (Split-Path -Parent $PSScriptRoot)
if (-not $repoRootProvided -and $governanceRootName -eq ".governance") {
  throw "RepoRoot is required when running from a vendored governance submodule. Use -RepoRoot <target repo root> (e.g., -RepoRoot .)."
}

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

# Lightweight repo hygiene checks for common generated artifacts that should not be tracked.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_repo_hygiene.ps1

$repoRoot = $context.RepoRoot
$gitDir = Join-Path $repoRoot ".git"
if (-not (Test-Path -Path $gitDir)) {
  throw "Repo root does not appear to be a git repository: $repoRoot"
}

function Add-Issue([System.Collections.Generic.List[string]]$issues, [string]$message) {
  $issues.Add($message)
}

function Test-TrackedSecretLikePath([string]$Path) {
  $normalized = $Path.Replace('\', '/')
  $lower = $normalized.ToLowerInvariant()

  if ($lower -match '(^|/)\.env($|\.local$|\.dev$|\.prod$|\.test$)') {
    return $true
  }

  if ($lower -match '(^|/)\.x_token\.json$') {
    return $true
  }

  if ($normalized -like "X-Bookmarks Import/data/*") {
    return $true
  }

  if ($lower -match '(^|/)[^/]*(token|secret|credential|credentials)[^/]*\.(json|txt|env|ini|toml|yaml|yml)$') {
    return $true
  }

  return $false
}

$issues = New-Object System.Collections.Generic.List[string]

try {
  $tracked = git -C $repoRoot ls-files
  if ($LASTEXITCODE -ne 0) {
    throw "git ls-files failed for repo root: $repoRoot"
  }
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

  if (Test-TrackedSecretLikePath -Path $path) {
    Add-Issue $issues "Tracked secret-like or workspace-local file: $path"
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
