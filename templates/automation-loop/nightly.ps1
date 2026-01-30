param(
  [string]$RepoRoot,
  [int]$WaitMinutes = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AutomationRoot = $PSScriptRoot

& (Join-Path $AutomationRoot "review.ps1") -RepoRoot $RepoRoot

if ($WaitMinutes -gt 0) {
  Start-Sleep -Seconds ($WaitMinutes * 60)
}

& (Join-Path $AutomationRoot "implement.ps1") -RepoRoot $RepoRoot
