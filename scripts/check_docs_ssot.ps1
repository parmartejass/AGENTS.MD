param(
  [string]$RepoRoot,
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

$docsRoot = Join-Path $context.RepoRoot "docs"
$policyPath = Join-Path $context.GovernanceRoot "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"

if (-not (Test-Path $docsRoot -PathType Container)) {
  Write-Host "No docs/ folder found. Skipping docs SSOT checks."
  exit 0
}

if (-not (Test-Path $policyPath -PathType Leaf)) {
  throw "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md missing in governance root. Doc header enum SSOT is required."
}

$policyLines = Get-Content -Path $policyPath
$docTypeEnumLine = $policyLines | Where-Object { $_ -match '^doc_type:\s*.+\|.+' } | Select-Object -First 1
if (-not $docTypeEnumLine) {
  throw "Doc header enum not found in docs/agents/25-docs-ssot-policy/docs-ssot-policy.md (expected 'doc_type: ...|...')."
}

$allowedDocTypes =
  ($docTypeEnumLine -replace '^doc_type:\s*', '').Split('|') |
  ForEach-Object { $_.Trim() } |
  Where-Object { $_ -ne "" }

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
    if ([string]::IsNullOrWhiteSpace($key)) {
      throw "Invalid migrated router key in $mapPath"
    }
    if ([string]::IsNullOrWhiteSpace($value)) {
      throw "Invalid migrated router leaf value for key '$key' in $mapPath"
    }
    if ($value.Contains("/") -or $value.EndsWith("/")) {
      throw "Invalid migrated router leaf '$value' for '$key' in $mapPath"
    }
    $map[$key.Trim('/')] = $value
  }

  return $map
}

$docsRootFull = (Resolve-Path $docsRoot).Path
$files = Get-ChildItem -Path $docsRoot -Recurse -Filter "*.md" -File
$issues = 0
$migratedRouterLeaves = Get-MigratedRouterLeaves -governanceRoot $context.GovernanceRoot

function Get-RelativeDocsPath([string]$fullPath) {
  return $fullPath.Substring($docsRootFull.Length).TrimStart('\', '/') -replace '\\', '/'
}

function Get-DirectVisibleChildren([string]$dirPath) {
  $children = New-Object System.Collections.Generic.List[System.IO.FileSystemInfo]
  foreach ($item in (Get-ChildItem -Path $dirPath -Force | Sort-Object Name)) {
    if ($item.Name -eq "index.md") { continue }
    if ($item.Name.StartsWith(".")) { continue }
    $children.Add($item)
  }
  return $children
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

function Test-IndexReferencesChild(
  [System.Collections.Generic.List[string]]$linkTargets,
  [System.IO.FileSystemInfo]$child
) {
  foreach ($target in $linkTargets) {
    if ($child.PSIsContainer) {
      if ($target -eq $child.Name -or $target -eq ($child.Name + "/index.md")) {
        return $true
      }
    } else {
      if ($target -eq $child.Name) {
        return $true
      }
    }
  }
  return $false
}

function Test-IsDocsRouterExempt([string]$dirPath) {
  $relativePath = Get-RelativeDocsPath $dirPath
  if ($relativePath -match '^agents/subagents/shared($|/)') {
    return $true
  }
  if ($relativePath -match '^agents/skills/([^/]+)$') {
    return (Test-Path (Join-Path $dirPath "SKILL.md") -PathType Leaf)
  }
  return $false
}

function Test-IsRoutingOnlyIndex([string]$indexText) {
  $lines = @(
    $indexText -split "`r?`n" |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -ne "" }
  )

  if ($lines.Count -eq 0) { return $false }
  if (-not $lines[0].StartsWith("# ")) { return $false }

  for ($i = 1; $i -lt $lines.Count; $i++) {
    if (-not $lines[$i].StartsWith("- ")) {
      return $false
    }
  }

  return $true
}

foreach ($dir in (@((Get-Item $docsRoot)) + (Get-ChildItem -Path $docsRoot -Recurse -Directory | Sort-Object FullName))) {
  $indexPath = Join-Path $dir.FullName "index.md"
  if (-not (Test-Path $indexPath -PathType Leaf)) {
    Write-Host "ERROR: Missing folder index: $indexPath"
    $issues++
    continue
  }

  $children = Get-DirectVisibleChildren $dir.FullName
  $indexText = Get-Content -Raw -Path $indexPath
  $relativeDir = Get-RelativeDocsPath $dir.FullName
  $isRouterExempt = Test-IsDocsRouterExempt $dir.FullName
  $directMarkdownChildren = @($children | Where-Object { -not $_.PSIsContainer -and $_.Extension -eq ".md" })

  if (-not $isRouterExempt -and -not (Test-IsRoutingOnlyIndex $indexText)) {
    Write-Host "ERROR: Docs folder index must remain routing-only (title plus bullet links only): $indexPath"
    $issues++
  }

  if (-not $isRouterExempt -and $directMarkdownChildren.Count -gt 1) {
    Write-Host "ERROR: Docs narrative folders must contain at most one canonical non-index markdown doc: $($dir.FullName)"
    $issues++
  }

  $expectedLeaf = $null
  if ($migratedRouterLeaves.ContainsKey($relativeDir)) {
    $expectedLeaf = $migratedRouterLeaves[$relativeDir]
    if ($directMarkdownChildren.Count -ne 1 -or $directMarkdownChildren[0].Name -ne $expectedLeaf) {
      Write-Host "ERROR: Migrated narrative folder must contain canonical leaf '$expectedLeaf': $($dir.FullName)"
      $issues++
    }
  }

  if ($children.Count -eq 0) { continue }

  $linkTargets = Get-MarkdownLinkTargets $indexText
  $requiredWhenCount = ([regex]::Matches($indexText, 'Required when:')).Count
  if ($requiredWhenCount -lt $children.Count) {
    Write-Host "ERROR: Folder index must include a 'Required when:' route for each direct child: $indexPath"
    $issues++
  }

  foreach ($child in $children) {
    if (-not (Test-IndexReferencesChild $linkTargets $child)) {
      Write-Host "ERROR: Folder index is missing a markdown link to direct child '$($child.Name)': $indexPath"
      $issues++
    }
  }

}

foreach ($file in $files) {
  $relativePath = Get-RelativeDocsPath $file.FullName
  if ($relativePath -match '^agents/skills/([^/]+)/') {
    $skillBundleRoot = Join-Path $docsRoot ("agents/skills/" + $Matches[1])
    if (Test-Path (Join-Path $skillBundleRoot "SKILL.md") -PathType Leaf) { continue }
  }
  if ($relativePath -match '^agents/subagents/[^/]+/') { continue }
  if ($relativePath -eq "index.md" -or $relativePath -match '(^|/)index\.md$') { continue }

  $head = Get-Content -Path $file.FullName -TotalCount 25

  $docTypeMatch = $head | Select-String -Pattern '^doc_type:' | Select-Object -First 1
  if (-not $docTypeMatch) {
    Write-Host "ERROR: Missing doc header (doc_type) in: $($file.FullName)"
    $issues++
  } else {
    $docTypeValue = ($docTypeMatch.Line -replace '^doc_type:\s*', '').Trim()
    if ($allowedDocTypes -notcontains $docTypeValue) {
      Write-Host "ERROR: Invalid doc_type '$docTypeValue' in: $($file.FullName)"
      $issues++
    }
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

$warnMatches =
  Get-ChildItem -Path $docsRoot -Recurse -File |
  Where-Object { $_.FullName -notmatch '[\\/]generated[\\/]' } |
  Select-String -Pattern 'defaults?:\s*$|default value' -ErrorAction SilentlyContinue

if ($warnMatches) {
  Write-Warning "Docs mention defaults/default value. Ensure docs reference config keys by identifier, not copied literal values."
}

Write-Host "Docs SSOT checks passed."
