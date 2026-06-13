[CmdletBinding()]
param(
    [switch]$Force,
    [string]$PythonExe,
    [string]$RepoRoot
)

& (Join-Path (Split-Path -Parent $PSScriptRoot) "link_repo_assets.ps1") -Include settings -Force:$Force -PythonExe $PythonExe -RepoRoot $RepoRoot
