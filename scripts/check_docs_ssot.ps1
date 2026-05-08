param(
  [string]$RepoRoot,
  [string]$GovernanceRoot
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
. (Join-Path $PSScriptRoot "_entrypoint_contracts.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

$docsRoot = Join-Path $context.RepoRoot "docs"
$policyPath = Join-Path $context.GovernanceRoot "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md"
$registryPath = Join-Path $context.GovernanceRoot "scripts/entrypoint_contracts.json"

if (-not (Test-Path $docsRoot -PathType Container)) {
  throw "Missing required docs/ folder: $docsRoot"
}

if (-not (Test-Path $policyPath -PathType Leaf)) {
  throw "docs/agents/25-docs-ssot-policy/docs-ssot-policy.md missing in governance root. Doc header enum SSOT is required."
}

if (-not (Test-Path $registryPath -PathType Leaf)) {
  throw "scripts/entrypoint_contracts.json missing in governance root."
}

$policyLines = Get-Content -Path $policyPath
$docTypeEnumLine = $null
$inCodeBlock = $false
foreach ($line in $policyLines) {
  $trimmed = $line.Trim()
  if ($trimmed.StartsWith('```')) {
    $inCodeBlock = -not $inCodeBlock
    continue
  }
  if ($inCodeBlock -and $trimmed -match '^doc_type:\s*.+\|.+') {
    $docTypeEnumLine = $trimmed
    break
  }
}
if (-not $docTypeEnumLine) {
  throw "Doc header enum template not found in docs/agents/25-docs-ssot-policy/docs-ssot-policy.md (expected 'doc_type: ...|...' inside a fenced code block)."
}

$allowedDocTypes =
  ($docTypeEnumLine -replace '^doc_type:\s*', '').Split('|') |
  ForEach-Object { $_.Trim() } |
  Where-Object { $_ -ne "" }

$contractContext = Get-DocsEntrypointContractContext -RegistryPath $registryPath
$minimumLeafCount = $contractContext.MinimumLeafCount
$identityFiles = @($contractContext.IdentityFiles)

$docsRootFull = (Resolve-Path $docsRoot).Path
$files = Get-ChildItem -Path $docsRoot -Recurse -Filter "*.md" -File
$issues = 0

function Get-RelativeDocsPath([string]$fullPath) {
  return $fullPath.Substring($docsRootFull.Length).TrimStart('\', '/') -replace '\\', '/'
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

function Get-DirectVisibleChildren([string]$dirPath, [string]$routerName) {
  $children = New-Object System.Collections.Generic.List[System.IO.FileSystemInfo]
  foreach ($item in (Get-ChildItem -Path $dirPath -Force | Sort-Object Name)) {
    if ($item.Name -eq $routerName) { continue }
    if ($item.Name.StartsWith(".")) { continue }
    $children.Add($item)
  }
  return $children
}

function Normalize-LinkTarget([string]$target) {
  $target = [System.Uri]::UnescapeDataString($target.Trim())
  if ($target -eq "") { return $null }
  if ($target -match '^[A-Za-z][A-Za-z0-9+\.-]*:' -or $target.StartsWith("//")) { return $null }
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
  foreach ($part in ($target -split '/')) {
    if ($part -eq "" -or $part -eq ".") { continue }
    if ($part -eq "..") { return $null }
    $parts.Add($part)
  }
  if ($parts.Count -eq 0) { return $null }
  return ($parts -join "/")
}

function Get-RouteTargets([string]$routerText, [string]$routerPath) {
  $targets = New-Object System.Collections.Generic.List[string]
  $lines = @(
    $routerText -split "`r?`n" |
    Where-Object { $_.Trim() -ne "" }
  )

  if ($lines.Count -eq 0) {
    Write-Host "ERROR: Router file is empty: $routerPath"
    $script:issues++
    return $targets
  }
  if (-not $lines[0].Trim().StartsWith("# ")) {
    Write-Host "ERROR: Router file must begin with a markdown heading: $routerPath"
    $script:issues++
    return $targets
  }

  for ($i = 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i].Trim()
    if (-not $line.StartsWith("- ")) {
      Write-Host "ERROR: Router file must remain routing-only (title plus route bullets only): $routerPath"
      $script:issues++
      continue
    }
    if ($line -notmatch 'Required when:') {
      Write-Host "ERROR: Router bullet is missing 'Required when:': $routerPath"
      $script:issues++
    }
    $match = [regex]::Match($line, '\[[^\]]+\]\(([^)]+)\)')
    if (-not $match.Success) {
      Write-Host "ERROR: Router bullet is missing a markdown link target: $routerPath"
      $script:issues++
      continue
    }
    $normalized = Normalize-LinkTarget $match.Groups[1].Value
    if (-not $normalized) {
      Write-Host "ERROR: Router bullet uses an invalid or out-of-bounds link target '$($match.Groups[1].Value)': $routerPath"
      $script:issues++
      continue
    }
    $targets.Add($normalized)
  }

  return $targets
}

function Test-RouteTargetsChild(
  [System.Collections.Generic.List[string]]$targets,
  [System.IO.FileSystemInfo]$child
) {
  foreach ($target in $targets) {
    if ($child.PSIsContainer) {
      $childRouter = Resolve-DocsRouterFilename $child.Name
      if ($target -ceq $child.Name -or $target -ceq ($child.Name + "/" + $childRouter)) {
        return $true
      }
    } else {
      if ($target -ceq $child.Name) {
        return $true
      }
    }
  }
  return $false
}

function Test-HeaderExemptMarkdown([string]$relativePath) {
  if ($relativePath -match '/SKILL\.md$') { return $true }
  return $false
}

foreach ($dir in (@((Get-Item $docsRoot)) + (Get-ChildItem -Path $docsRoot -Recurse -Directory | Sort-Object FullName))) {
  $routerName = Resolve-DocsRouterFilename $dir.Name
  $routerPath = Join-Path $dir.FullName $routerName
  if (-not (Test-Path $routerPath -PathType Leaf)) {
    Write-Host "ERROR: Missing folder router: $routerPath"
    $issues++
    continue
  }

  $children = Get-DirectVisibleChildren $dir.FullName $routerName
  $routerText = Get-Content -Raw -Path $routerPath
  $routeTargets = Get-RouteTargets $routerText $routerPath
  $publicMarkdownChildren = @(
    $children |
    Where-Object {
      -not $_.PSIsContainer -and
      $_.Extension -eq ".md" -and
      ($identityFiles -notcontains $_.Name)
    }
  )
  $artifactFirst = $publicMarkdownChildren.Count -eq 0
  if (-not $artifactFirst) {
    if ($publicMarkdownChildren.Count -lt $minimumLeafCount) {
      Write-Host "ERROR: Docs folder must expose at least $minimumLeafCount public leaf docs: $($dir.FullName)"
      $issues++
    }
    $expectedLeaf = Resolve-PrimaryLeafFilename $dir.Name
    if (-not (Test-EntrypointCaseSensitiveContains -Values $publicMarkdownChildren.Name -Expected $expectedLeaf)) {
      Write-Host "ERROR: Missing canonical public leaf '$expectedLeaf': $($dir.FullName)"
      $issues++
    }
  }

  foreach ($child in $children) {
    if (-not (Test-RouteTargetsChild $routeTargets $child)) {
      Write-Host "ERROR: Router is missing a route to direct child '$($child.Name)': $routerPath"
      $issues++
    }
  }
}

foreach ($file in $files) {
  $relativePath = Get-RelativeDocsPath $file.FullName
  $routerName = Resolve-DocsRouterFilename $file.Directory.Name
  if ($file.Name -eq $routerName) { continue }
  if (Test-HeaderExemptMarkdown $relativePath) { continue }

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
