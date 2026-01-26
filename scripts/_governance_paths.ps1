$ErrorActionPreference = "Stop"

function Resolve-PathOrFull {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  $resolved = Resolve-Path -Path $Path -ErrorAction SilentlyContinue
  if ($resolved) {
    return $resolved.Path
  }

  return [System.IO.Path]::GetFullPath($Path)
}

function Get-RelativePath {
  param(
    [Parameter(Mandatory = $true)]
    [string]$From,
    [Parameter(Mandatory = $true)]
    [string]$To
  )

  $fromPath = Resolve-PathOrFull -Path $From
  $toPath = Resolve-PathOrFull -Path $To

  $fromIsDir = (Test-Path -Path $fromPath -PathType Container) -or ($From -match '[\\/]$')
  $toIsDir = (Test-Path -Path $toPath -PathType Container) -or ($To -match '[\\/]$')

  $fromPath = $fromPath.TrimEnd('\', '/')
  if ($fromIsDir) {
    $fromPath += '\'
  }

  $toPath = $toPath.TrimEnd('\', '/')
  if ($toIsDir) {
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

  $governanceRootPath = if ($GovernanceRoot) {
    Resolve-PathOrFull -Path $GovernanceRoot
  } else {
    Resolve-PathOrFull -Path (Split-Path -Parent $ScriptRoot)
  }

  $repoRootPath = if ($RepoRoot) {
    Resolve-PathOrFull -Path $RepoRoot
  } else {
    $governanceRootPath
  }

  $relative = Get-RelativePath -From $repoRootPath -To $governanceRootPath
  if ($relative -eq "." -or [string]::IsNullOrWhiteSpace($relative)) {
    $relative = ""
  } else {
    $relative = $relative -replace '\\', '/'
  }

  return [pscustomobject]@{
    RepoRoot = $repoRootPath
    GovernanceRoot = $governanceRootPath
    GovernanceRelPath = $relative
  }
}
