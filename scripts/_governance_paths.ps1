$ErrorActionPreference = "Stop"

function Get-RelativePath {
  param(
    [Parameter(Mandatory = $true)]
    [string]$From,
    [Parameter(Mandatory = $true)]
    [string]$To
  )

  $fromResolved = Resolve-Path -Path $From
  $toResolved = Resolve-Path -Path $To

  $fromPath = $fromResolved.Path.TrimEnd('\')
  if (Test-Path -Path $fromResolved.Path -PathType Container) {
    $fromPath += '\'
  }

  $toPath = $toResolved.Path.TrimEnd('\')
  if (Test-Path -Path $toResolved.Path -PathType Container) {
    $toPath += '\'
  }

  $fromUri = New-Object System.Uri($fromPath)
  $toUri = New-Object System.Uri($toPath)

  $relative = $fromUri.MakeRelativeUri($toUri).ToString()
  if ([string]::IsNullOrWhiteSpace($relative)) {
    return "."
  }

  return $relative
}

function Get-GovernanceContext {
  param(
    [string]$RepoRoot,
    [string]$GovernanceRoot,
    [string]$ScriptRoot
  )

  if ([string]::IsNullOrWhiteSpace($ScriptRoot)) {
    $ScriptRoot = $PSScriptRoot
  }

  $resolvedGovernanceRoot = if ($GovernanceRoot) {
    Resolve-Path -Path $GovernanceRoot
  } else {
    Resolve-Path -Path (Split-Path -Parent $ScriptRoot)
  }

  $resolvedRepoRoot = if ($RepoRoot) {
    Resolve-Path -Path $RepoRoot
  } else {
    $resolvedGovernanceRoot
  }

  $relative = Get-RelativePath -From $resolvedRepoRoot.Path -To $resolvedGovernanceRoot.Path
  if ($relative -eq "." -or [string]::IsNullOrWhiteSpace($relative)) {
    $relative = ""
  } else {
    $relative = $relative -replace '\\', '/'
  }

  return [pscustomobject]@{
    RepoRoot = $resolvedRepoRoot.Path
    GovernanceRoot = $resolvedGovernanceRoot.Path
    GovernanceRelPath = $relative
  }
}
