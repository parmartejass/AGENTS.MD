param(
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
$context = Get-GovernanceContext -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

# Validates agents-manifest.yaml for:
# - quoted paths in `default_inject` and `profiles.*.inject`
# - duplicates within each inject list (duplicates across lists are allowed)
# - referenced paths exist
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_agents_manifest.ps1

$governanceRoot = $context.GovernanceRoot
$manifestPath = Join-Path $governanceRoot "agents-manifest.yaml"

if (-not (Test-Path $manifestPath -PathType Leaf)) {
  throw "Missing agents-manifest.yaml at governance root: $manifestPath"
}

$lines = Get-Content -Path $manifestPath

$inPathList = $false
$pathListIndent = 0
$pathListKey = $null

$inProfiles = $false
$profilesIndent = 0
$profileKeyIndent = $null
$currentProfile = $null

$pathsByList = @{}
$issues = 0

function Get-IndentLength([string]$line) {
  if ($line -match '^(\s*)') { return $matches[1].Length }
  return 0
}

function Add-PathItem([string]$listKey, [string]$value, [int]$lineNumber) {
  if (-not $pathsByList.ContainsKey($listKey)) {
    $pathsByList[$listKey] = New-Object System.Collections.Generic.List[string]
  }

  if ([string]::IsNullOrWhiteSpace($value)) {
    Write-Host "ERROR: Empty path value in $listKey at line $lineNumber"
    $script:issues++
    return
  }

  $pathsByList[$listKey].Add($value)
}

for ($i = 0; $i -lt $lines.Count; $i++) {
  $lineNumber = $i + 1
  $line = $lines[$i]
  $trimmed = $line.Trim()

  if ($trimmed -eq "" -or $trimmed.StartsWith("#")) { continue }

  $indent = Get-IndentLength $line

  if ($inProfiles) {
    if (($indent -le $profilesIndent) -and ($trimmed -match '^[A-Za-z0-9_]+:\s*')) {
      $inProfiles = $false
      $profilesIndent = 0
      $profileKeyIndent = $null
      $currentProfile = $null
    } elseif ($trimmed -match '^([A-Za-z0-9_]+):\s*$') {
      if ($null -eq $profileKeyIndent) {
        if ($indent -gt $profilesIndent) {
          $profileKeyIndent = $indent
          $currentProfile = $matches[1]
        }
      } elseif ($indent -eq $profileKeyIndent) {
        $currentProfile = $matches[1]
      }
    }
  }

  if (-not $inProfiles) {
    if ($line -match '^(\s*)profiles:\s*$') {
      $inProfiles = $true
      $profilesIndent = $matches[1].Length
      $profileKeyIndent = $null
      $currentProfile = $null
    }
  }

  if ($inPathList) {
    $isListItem = $trimmed.StartsWith("- ")
    $isNewKeyAtOrAbove = (-not $isListItem) -and ($indent -le $pathListIndent) -and ($trimmed -match '^[A-Za-z0-9_]+:\s*')
    if ($isNewKeyAtOrAbove) {
      $inPathList = $false
      $pathListIndent = 0
      $pathListKey = $null
    }
  }

  if (-not $inPathList) {
    if ($line -match '^(\s*)default_inject:\s*$') {
      $inPathList = $true
      $pathListIndent = $matches[1].Length
      $pathListKey = "default_inject"
      continue
    }
    if ($line -match '^(\s*)fallback_inject:\s*$') {
      $inPathList = $true
      $pathListIndent = $matches[1].Length
      $pathListKey = "fallback_inject"
      continue
    }
    if ($line -match '^(\s*)inject:\s*$') {
      $inPathList = $true
      $pathListIndent = $matches[1].Length
      if ($inProfiles -and (-not [string]::IsNullOrWhiteSpace($currentProfile))) {
        $pathListKey = "profiles.$currentProfile.inject"
      } else {
        $pathListKey = "inject"
      }
      continue
    }
  }

  if ($inPathList) {
    if ($trimmed -notmatch '^- ') { continue }

    if ($trimmed -match '^-\s+"([^"]+)"\s*$') {
      Add-PathItem $pathListKey $matches[1] $lineNumber
      continue
    }

    if ($trimmed -match "^-\s+'([^']+)'\s*$") {
      Add-PathItem $pathListKey $matches[1] $lineNumber
      continue
    }

    Write-Host "ERROR: Unquoted path in ${pathListKey} at line ${lineNumber}: $trimmed"
    $issues++
    continue
  }
}

$allPaths = New-Object System.Collections.Generic.List[string]
foreach ($key in $pathsByList.Keys) {
  foreach ($p in $pathsByList[$key]) {
    $allPaths.Add($p)
  }
}

if (-not $pathsByList.ContainsKey("default_inject")) {
  Write-Host "ERROR: Missing or empty default_inject list in agents-manifest.yaml"
  $issues++
} elseif (-not $pathsByList["default_inject"].Contains("AGENTS.md")) {
  Write-Host "ERROR: default_inject must include AGENTS.md"
  $issues++
}

foreach ($listKey in $pathsByList.Keys) {
  $seen = @{}
  foreach ($p in $pathsByList[$listKey]) {
    if ($seen.ContainsKey($p)) {
      Write-Host "ERROR: Duplicate path in ${listKey}: $p"
      $issues++
    } else {
      $seen[$p] = $true
    }
  }
}

foreach ($p in ($allPaths | Select-Object -Unique)) {
  $full = Join-Path $governanceRoot $p
  if (-not (Test-Path $full)) {
    Write-Host "ERROR: Manifest references missing path: $p"
    $issues++
  }
}

if ($issues -gt 0) {
  throw "Agents manifest check failed: $issues issue(s)."
}

Write-Host "Agents manifest checks passed."
