Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AutomationConfig {
  param([Parameter(Mandatory = $true)][string]$AutomationRoot)

  $configPath = Join-Path $AutomationRoot "automation.config.json"
  if (-not (Test-Path $configPath)) {
    throw "Missing automation.config.json at: $configPath"
  }

  $raw = Get-Content -Raw $configPath
  return $raw | ConvertFrom-Json
}

function Get-RepoRoot {
  param(
    [string]$Override,
    [Parameter(Mandatory = $true)][string]$AutomationRoot
  )

  if ($Override) {
    return (Resolve-Path $Override).Path
  }

  $result = & git -C $AutomationRoot rev-parse --show-toplevel 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $result) {
    throw "Unable to determine repo root. Provide -RepoRoot."
  }

  return $result.Trim()
}

function Resolve-RepoPath {
  param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$PathValue
  )

  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return $PathValue
  }

  return (Join-Path $RepoRoot $PathValue)
}

function Resolve-AutomationPath {
  param(
    [Parameter(Mandatory = $true)][string]$AutomationRoot,
    [Parameter(Mandatory = $true)][string]$PathValue
  )

  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return $PathValue
  }

  return (Join-Path $AutomationRoot $PathValue)
}

function Expand-DateToken {
  param(
    [Parameter(Mandatory = $true)][string]$PathTemplate,
    [Parameter(Mandatory = $true)][string]$DateToken
  )

  return ($PathTemplate -replace "\{date\}", $DateToken)
}

function Initialize-Directory {
  param([Parameter(Mandatory = $true)][string]$Path)

  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Force $Path | Out-Null
  }
}

$script:LogPath = $null

function Set-LogPath {
  param([Parameter(Mandatory = $true)][string]$Path)

  $script:LogPath = $Path
}

function Write-Log {
  param(
    [Parameter(Mandatory = $true)][string]$Message,
    [string]$Level = "INFO"
  )

  $timestamp = (Get-Date).ToString("s")
  $line = "$timestamp [$Level] $Message"
  Write-Output $line
  if ($script:LogPath) {
    Add-Content -Path $script:LogPath -Value $line
  }
}

function Invoke-Git {
  param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string[]]$GitArgs
  )

  & git -C $RepoRoot @GitArgs
  if ($LASTEXITCODE -ne 0) {
    throw "git command failed: git -C $RepoRoot $($GitArgs -join ' ')"
  }
}

function Assert-RepoClean {
  param([Parameter(Mandatory = $true)][string]$RepoRoot)

  $dirty = & git -C $RepoRoot status --porcelain
  if ($LASTEXITCODE -ne 0) {
    throw "git status failed"
  }

  if ($dirty) {
    throw "Working tree is not clean. Resolve and rerun."
  }
}

function Assert-GovernanceClean {
  param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)]$Config
  )

  if (-not $Config.guard) {
    return
  }

  if (-not $Config.guard.fail_on_governance_changes) {
    return
  }

  $govPath = $Config.guard.governance_path
  if (-not $govPath) {
    return
  }

  $fullGovPath = Resolve-RepoPath -RepoRoot $RepoRoot -PathValue $govPath
  if (-not (Test-Path $fullGovPath)) {
    return
  }

  $dirty = & git -C $RepoRoot status --porcelain -- $govPath
  if ($LASTEXITCODE -ne 0) {
    throw "git status failed for governance path"
  }

  if ($dirty) {
    throw "Governance path has changes. Do not edit .governance from the parent repo."
  }
}

function Format-Prompt {
  param(
    [Parameter(Mandatory = $true)][string]$TemplatePath,
    [Parameter(Mandatory = $true)][hashtable]$Tokens
  )

  if (-not (Test-Path $TemplatePath)) {
    throw "Prompt template not found: $TemplatePath"
  }

  $text = Get-Content -Raw $TemplatePath
  foreach ($key in $Tokens.Keys) {
    $needle = [regex]::Escape("{{${key}}}")
    $text = $text -replace $needle, [string]$Tokens[$key]
  }

  return $text
}

function Invoke-Agent {
  param(
    [Parameter(Mandatory = $true)]$Config,
    [Parameter(Mandatory = $true)][string]$PromptText
  )

  if (-not $Config.runner) {
    throw "Missing runner config"
  }

  $command = $Config.runner.command
  if ([string]::IsNullOrWhiteSpace($command)) {
    throw "runner.command is required"
  }

  $runnerArgs = @()
  if ($Config.runner.args) {
    $runnerArgs = @($Config.runner.args)
  }

  $mode = $Config.runner.prompt_mode
  if (-not $mode) {
    throw "runner.prompt_mode is required"
  }

  Write-Log "Invoking agent runner: $command (mode=$mode)"

  switch ($mode) {
    "stdin" {
      $PromptText | & $command @runnerArgs
    }
    "arg" {
      & $command @runnerArgs $PromptText
    }
    "file" {
      $tempFile = New-TemporaryFile
      Set-Content -Path $tempFile -Value $PromptText
      & $command @runnerArgs $tempFile
      Remove-Item $tempFile -Force
    }
    default {
      throw "Unsupported runner.prompt_mode: $mode"
    }
  }

  if ($LASTEXITCODE -ne 0) {
    throw "Agent runner failed with exit code $LASTEXITCODE"
  }
}
