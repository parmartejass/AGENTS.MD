param(
  [string]$RepoRoot,
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
. (Join-Path $PSScriptRoot "_entrypoint_contracts.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

$repoRoot = $context.RepoRoot
$registryPath = Join-Path $context.GovernanceRoot "scripts/entrypoint_contracts.json"
$contractContext = Get-DocsEntrypointContractContext -RegistryPath $registryPath

$governancePrefix = ""
if (-not [string]::IsNullOrWhiteSpace($context.GovernanceRelPath)) {
  $governancePrefix = $context.GovernanceRelPath.TrimEnd("/") + "/"
}

$issues = New-Object System.Collections.Generic.List[string]

function Add-Issue([System.Collections.Generic.List[string]]$list, [string]$message) {
  $list.Add($message)
}

function Resolve-DocsAuthority([string]$folderName) {
  return Resolve-EntrypointDocsAuthority -FolderName $folderName -ContractContext $script:contractContext
}

function Resolve-DocsRouterFilename([string]$folderName) {
  return Resolve-EntrypointDocsRouterFilename -FolderName $folderName -ContractContext $script:contractContext
}

function Resolve-PrimaryLeafFilename([string]$folderName) {
  return Resolve-EntrypointPrimaryLeafFilename -FolderName $folderName -ContractContext $script:contractContext
}

function Get-RouteTargets(
  [string]$routerText,
  [string]$routerPath,
  [System.Collections.Generic.List[string]]$Issues
) {
  $targets = New-Object System.Collections.Generic.List[string]
  $lines = @(
    $routerText -split "`r?`n" |
    Where-Object { $_.Trim() -ne "" }
  )

  if ($lines.Count -eq 0) {
    Add-Issue $Issues "$routerPath is empty."
    return $targets
  }
  if (-not $lines[0].Trim().StartsWith("# ")) {
    Add-Issue $Issues "$routerPath must begin with a markdown heading."
    return $targets
  }

  for ($i = 1; $i -lt $lines.Count; $i++) {
    $trimmed = $lines[$i].Trim()
    if (-not $trimmed.StartsWith("- ")) {
      Add-Issue $Issues "$routerPath must remain routing-only (title plus route bullets only)."
      continue
    }
    if ($trimmed -notmatch 'Required when:') {
      Add-Issue $Issues "$routerPath has a route bullet missing 'Required when:'."
    }
    $match = [regex]::Match($trimmed, '\[[^\]]+\]\(([^)]+)\)')
    if (-not $match.Success) {
      Add-Issue $Issues "$routerPath has a route bullet missing a markdown link target."
      continue
    }
    $target = [System.Uri]::UnescapeDataString($match.Groups[1].Value.Trim())
    $target = ($target -split '\?')[0]
    $target = ($target -split '#')[0]
    $target = $target -replace '\\', '/'
    while ($target.StartsWith("./")) {
      $target = $target.Substring(2)
    }
    if ($target.StartsWith("/")) {
      $target = $target.Substring(1)
    }
    $parts = New-Object System.Collections.Generic.List[string]
    $invalid = $false
    foreach ($part in ($target -split '/')) {
      if ($part -eq "" -or $part -eq ".") { continue }
      if ($part -eq "..") {
        $invalid = $true
        break
      }
      $parts.Add($part)
    }
    if ($invalid -or $parts.Count -eq 0) {
      Add-Issue $Issues "$routerPath has an invalid or out-of-bounds route target '$($match.Groups[1].Value)'."
      continue
    }
    $targets.Add($parts -join "/")
  }
  return $targets
}

$requiredFiles = @(
  "README.md",
  "docs/project/project_index.md",
  "docs/project/goal/goal_index.md",
  "docs/project/goal/goal.md",
  "docs/project/rules/rules_index.md",
  "docs/project/rules/rules.md",
  "docs/project/architecture/architecture_index.md",
  "docs/project/architecture/architecture.md",
  "docs/project/learning/learning_index.md",
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
    "docs/project/project_index.md",
    "AGENTS.md",
    "${governancePrefix}scripts/check_docs_ssot.ps1",
    "${governancePrefix}scripts/check_docs_router_contract/check_docs_router_contract_main.py",
    "${governancePrefix}scripts/check_agents_manifest.ps1",
    "${governancePrefix}scripts/check_project_docs.ps1",
    "${governancePrefix}scripts/check_repo_hygiene.ps1",
    "${governancePrefix}scripts/check_change_records.ps1",
    "${governancePrefix}scripts/check_folder_architecture/check_folder_architecture_main.py",
    "${governancePrefix}scripts/check_python_safety/check_python_safety_main.py"
  )

  foreach ($ref in $requiredReadmeRefs) {
    if ($readmeText -notlike "*$ref*") {
      Add-Issue $issues "README.md must reference: $ref"
    }
  }
}

$projectRouterPath = Join-Path $repoRoot "docs/project/project_index.md"
if (Test-Path $projectRouterPath -PathType Leaf) {
  $targets = Get-RouteTargets -routerText (Get-Content -Raw -Path $projectRouterPath) -routerPath "docs/project/project_index.md" -Issues $issues
  foreach ($child in @("goal", "rules", "architecture", "learning")) {
    $expected = "$child/$(Resolve-DocsRouterFilename $child)"
    if (-not (Test-EntrypointCaseSensitiveContains -Values $targets -Expected $expected)) {
      Add-Issue $issues "docs/project/project_index.md must reference $expected"
    }
  }
}

foreach ($child in @("goal", "rules", "architecture", "learning")) {
  $routerRel = "docs/project/$child/$(Resolve-DocsRouterFilename $child)"
  $routerPath = Join-Path $repoRoot $routerRel
  if (-not (Test-Path $routerPath -PathType Leaf)) {
    Add-Issue $issues "Missing required file: $routerRel"
    continue
  }
  $targets = Get-RouteTargets -routerText (Get-Content -Raw -Path $routerPath) -routerPath $routerRel -Issues $issues
  $expectedLeaf = Resolve-PrimaryLeafFilename $child
  if (-not (Test-EntrypointCaseSensitiveContains -Values $targets -Expected $expectedLeaf)) {
    Add-Issue $issues "$routerRel must reference $expectedLeaf"
  }
}

if ($issues.Count -gt 0) {
  foreach ($issue in $issues) {
    Write-Host "ERROR: $issue"
  }
  throw "Project docs check failed: $($issues.Count) issue(s)."
}

Write-Host "Project docs checks passed."
