[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$IncludeCompatibility,
    [string]$RepoRoot
)

& (Join-Path (Split-Path -Parent $PSScriptRoot) "link_repo_assets.ps1") -Include settings -Force:$Force -IncludeCompatibility:$IncludeCompatibility -RepoRoot $RepoRoot
