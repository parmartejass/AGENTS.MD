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

$policyPath = Join-Path $agentsDocsRoot "25-docs-ssot-policy.md"
if (-not (Test-Path $policyPath -PathType Leaf)) {
  throw "docs/agents/25-docs-ssot-policy.md missing. Doc header enum SSOT is required."
}

$policyLines = Get-Content -Path $policyPath
$docTypeEnumLine = $policyLines | Where-Object { $_ -match '^doc_type:\s*.+\|.+' } | Select-Object -First 1
if (-not $docTypeEnumLine) {
  throw "Doc header enum not found in docs/agents/25-docs-ssot-policy.md (expected 'doc_type: ...|...')."
}

$allowedDocTypes =
  ($docTypeEnumLine -replace '^doc_type:\s*', '').Split('|') |
  ForEach-Object { $_.Trim() } |
  Where-Object { $_ -ne "" }

$docsRootFull = (Resolve-Path $docsRoot).Path

$files = Get-ChildItem -Path $docsRoot -Recurse -Filter "*.md" -File
$issues = 0

foreach ($file in $files) {
  $relativePath = $file.FullName.Substring($docsRootFull.Length).TrimStart('\', '/')
  $relativePath = $relativePath -replace '\\', '/'
  if ($relativePath -eq "index.md" -or $relativePath -match '^[^/]+/index\.md$') { continue }

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

# Soft guardrail: warn on "defaults tables" language (common drift source).
$warnMatches =
  Get-ChildItem -Path $docsRoot -Recurse -File |
  Where-Object { $_.FullName -notmatch '[\\/]generated[\\/]' } |
  Select-String -Pattern 'defaults?:\s*$|default value' -ErrorAction SilentlyContinue

if ($warnMatches) {
  Write-Warning "Docs mention defaults/default value. Ensure docs reference config keys by identifier, not copied literal values."
}

Write-Host "Docs SSOT checks passed."
