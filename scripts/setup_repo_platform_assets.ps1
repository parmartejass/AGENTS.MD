[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$IncludeCompatibility,
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $PSScriptRoot
$linker = Join-Path $scriptRoot "docs\agents\link_repo_assets.ps1"

if (-not (Test-Path -LiteralPath $linker -PathType Leaf)) {
    throw "Missing linker script: $linker"
}

& $linker `
    -Include @("skills", "subagents", "mcp", "acp", "settings") `
    -Force:$Force `
    -IncludeCompatibility:$IncludeCompatibility `
    -RepoRoot $RepoRoot
