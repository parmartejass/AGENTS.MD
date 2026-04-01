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

function Get-MigratedRouterLeaves([string]$governanceRoot) {
  $mapPath = Join-Path $governanceRoot "scripts/migrated_router_leaves.json"
  if (-not (Test-Path $mapPath -PathType Leaf)) {
    throw "Missing migrated router-leaf map: $mapPath"
  }

  $payload = Get-Content -Raw -Path $mapPath | ConvertFrom-Json
  if (-not $payload.migrated_router_leaves) {
    throw "Expected key 'migrated_router_leaves' in $mapPath"
  }

  $map = @{}
  foreach ($prop in $payload.migrated_router_leaves.PSObject.Properties) {
    $key = [string]$prop.Name
    $value = [string]$prop.Value
    if ([string]::IsNullOrWhiteSpace($key) -or [string]::IsNullOrWhiteSpace($value)) {
      throw "Invalid migrated router map entry in $mapPath"
    }
    $map[$key.Trim('/')] = $value
  }

  return $map
}

function Get-MarkdownLinkTargets([string]$text) {
  $targets = New-Object System.Collections.Generic.List[string]
  $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
  foreach ($match in $matches) {
    $target = $match.Groups[1].Value.Trim()
    if ($target -eq "") { continue }
    if ($target -match '^[A-Za-z][A-Za-z0-9+\.-]*:' -or $target.StartsWith("//")) {
      continue
    }
    $target = ($target -split '\?')[0]
    $target = ($target -split '#')[0]
    $target = $target -replace '\\', '/'
    while ($target.StartsWith("./")) {
      $target = $target.Substring(2)
    }
    if ($target.StartsWith("/")) {
      $target = $target.Substring(1)
    }
    $segments = New-Object System.Collections.Generic.List[string]
    $invalid = $false
    foreach ($segment in ($target -split '/')) {
      if ($segment -eq "" -or $segment -eq ".") { continue }
      if ($segment -eq "..") {
        $invalid = $true
        break
      }
      $segments.Add($segment)
    }
    if ($invalid -or $segments.Count -eq 0) { continue }
    $targets.Add(($segments -join "/"))
  }
  return $targets
}

$requiredFiles = @(
  "README.md",
  "docs/project/index.md",
  "docs/project/goal/index.md",
  "docs/project/goal/goal.md",
  "docs/project/rules/index.md",
  "docs/project/rules/rules.md",
  "docs/project/architecture/index.md",
  "docs/project/architecture/architecture.md",
  "docs/project/learning/index.md",
  "docs/project/learning/learning.md"
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
    "${governancePrefix}docs/agents/platforms/00-platform-runtime-standards/platform-runtime-standards.md",
    "${governancePrefix}docs/agents/platforms/index.md",
    "${governancePrefix}docs/agents/platforms/runtime-projections.json",
    "${governancePrefix}docs/agents/integrations/index.md",
    "${governancePrefix}scripts/setup_repo_platform_assets.ps1",
    "${governancePrefix}scripts/check_docs_ssot.ps1",
    "${governancePrefix}scripts/check_docs_router_contract/main.py",
    "${governancePrefix}scripts/check_agents_manifest.ps1",
    "${governancePrefix}scripts/check_project_docs.ps1",
    "${governancePrefix}scripts/check_repo_hygiene.ps1",
    "${governancePrefix}scripts/check_change_records.ps1",
    "${governancePrefix}scripts/check_folder_architecture/main.py",
    "${governancePrefix}scripts/check_python_safety/main.py"
  )

  foreach ($ref in $requiredReadmeRefs) {
    if ($readmeText -notlike "*$ref*") {
      Add-Issue $issues "README.md must reference: $ref"
    }
  }
}

if ((Join-Path $repoRoot "docs/project/index.md") | Test-Path) {
  $indexText = Get-Content -Raw -Path (Join-Path $repoRoot "docs/project/index.md")
  foreach ($ref in @("docs/project/goal/index.md", "docs/project/rules/index.md", "docs/project/architecture/index.md", "docs/project/learning/index.md")) {
    if ($indexText -notlike "*$ref*") {
      Add-Issue $issues "docs/project/index.md must reference $ref"
    }
  }
}

$routerMap = Get-MigratedRouterLeaves -governanceRoot $context.GovernanceRoot
$projectRouterEntries = @(
  $routerMap.GetEnumerator() |
  Where-Object { $_.Key -like "project/*" } |
  Sort-Object Key
)

foreach ($entry in $projectRouterEntries) {
  $routerRel = "docs/$($entry.Key)/index.md"
  $expectedLeafRef = [string]$entry.Value
  $routerPath = Join-Path $repoRoot $routerRel
  if (-not (Test-Path $routerPath -PathType Leaf)) {
    continue
  }
  $routerText = Get-Content -Raw -Path $routerPath
  $linkTargets = Get-MarkdownLinkTargets $routerText
  if (-not ($linkTargets -contains $expectedLeafRef)) {
    Add-Issue $issues "$routerRel must reference $expectedLeafRef"
  }
}

if ($issues.Count -gt 0) {
  foreach ($issue in $issues) {
    Write-Host "ERROR: $issue"
  }
  throw "Project docs check failed: $($issues.Count) issue(s)."
}

Write-Host "Project docs checks passed."
