param(
  [string]$WorkingRoot,
  [switch]$IncludePrCheck,
  [switch]$KeepWorkDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
  param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string[]]$Args
  )

  & git -C $RepoRoot @Args
  if ($LASTEXITCODE -ne 0) {
    throw "git failed: git -C $RepoRoot $($Args -join ' ')"
  }
}

function Assert-Contains {
  param(
    [Parameter(Mandatory = $true)][string]$Content,
    [Parameter(Mandatory = $true)][string]$Needle,
    [Parameter(Mandatory = $true)][string]$Label
  )

  if ($Content -notlike "*$Needle*") {
    throw "FAIL: $Label (missing '$Needle')"
  }

  Write-Output "PASS: $Label"
}

$automationRoot = $PSScriptRoot
$workRoot = $WorkingRoot
if ([string]::IsNullOrWhiteSpace($workRoot)) {
  $workRoot = Join-Path $env:TEMP ("automation-loop-verify-" + [guid]::NewGuid().ToString("N"))
}

$resolvedWorkRoot = Resolve-Path -Path $workRoot -ErrorAction SilentlyContinue
if ($resolvedWorkRoot) {
  $workRoot = $resolvedWorkRoot.Path
}

if (-not (Test-Path $workRoot)) {
  New-Item -ItemType Directory -Path $workRoot | Out-Null
}

$originBare = Join-Path $workRoot "origin.git"
$repoRoot = Join-Path $workRoot "repo"
$automationCopy = Join-Path $repoRoot "automation"
$logDir = $null

if (-not $WorkingRoot) {
  $cleanupWorkRoot = $true
} else {
  $cleanupWorkRoot = $false
}

if ($KeepWorkDir) {
  $cleanupWorkRoot = $false
}

try {
  Invoke-Git -RepoRoot $workRoot -Args @("init", "--bare", $originBare)
  Invoke-Git -RepoRoot $workRoot -Args @("init", $repoRoot)
  Invoke-Git -RepoRoot $repoRoot -Args @("checkout", "-b", "main")
  Invoke-Git -RepoRoot $repoRoot -Args @("config", "user.email", "automation@example.com")
  Invoke-Git -RepoRoot $repoRoot -Args @("config", "user.name", "Automation Loop")

  New-Item -ItemType Directory -Path (Join-Path $repoRoot "docs\project") -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $repoRoot "reports") -Force | Out-Null
  Set-Content -Path (Join-Path $repoRoot "docs\project\learning.md") -Value "# Learning`n"
  Set-Content -Path (Join-Path $repoRoot "README.md") -Value "temp`n"

  Invoke-Git -RepoRoot $repoRoot -Args @("add", ".")
  Invoke-Git -RepoRoot $repoRoot -Args @("commit", "-m", "init")
  Invoke-Git -RepoRoot $repoRoot -Args @("remote", "add", "origin", $originBare)
  Invoke-Git -RepoRoot $repoRoot -Args @("push", "-u", "origin", "main")

  Copy-Item -Path $automationRoot -Destination $automationCopy -Recurse -Force
  Invoke-Git -RepoRoot $repoRoot -Args @("add", "automation")
  Invoke-Git -RepoRoot $repoRoot -Args @("commit", "-m", "add automation template")
  Invoke-Git -RepoRoot $repoRoot -Args @("push", "origin", "main")

  $configPath = Join-Path $automationCopy "automation.config.json"
  $config = Get-Content -Raw $configPath | ConvertFrom-Json
  $config.runner.command = "powershell"
  $config.runner.args = @("-NoProfile", "-Command", "`$input | Out-Null; exit 0")
  $config.runner.prompt_mode = "stdin"

  $reportsRoot = Join-Path $workRoot "reports"
  $logsRoot = Join-Path $workRoot "logs"
  New-Item -ItemType Directory -Path $reportsRoot -Force | Out-Null
  New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
  $logDir = $logsRoot
  $config.paths.logs_dir = $logsRoot
  $config.paths.priority_report = (Join-Path $reportsRoot "priorities.md")
  $config.paths.governance_proposals = (Join-Path $reportsRoot "governance-proposals-{date}.md")
  $config.paths.review_report = (Join-Path $reportsRoot "compound-review-{date}.md")

  function Save-Config {
    param([Parameter(Mandatory = $true)]$Value)
    $Value | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
  }

  function Commit-Config {
    param([Parameter(Mandatory = $true)][string]$Message)
    Invoke-Git -RepoRoot $repoRoot -Args @("add", "automation/automation.config.json")
    Invoke-Git -RepoRoot $repoRoot -Args @("commit", "-m", $Message)
    Invoke-Git -RepoRoot $repoRoot -Args @("push", "origin", "main")
  }

  Save-Config -Value $config
  Commit-Config -Message "config: baseline"

  $config.review.auto_commit = $false
  $config.review.auto_push = $true
  Save-Config -Value $config
  Commit-Config -Message "config: review auto_commit off"
  & (Join-Path $automationCopy "review.ps1") -RepoRoot $repoRoot | Out-Null

  $reviewLog = Get-ChildItem -Path $logDir -Filter "compound-review-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $reviewLog) {
    throw "FAIL: review log not found"
  }
  $reviewContent = Get-Content -Raw $reviewLog.FullName
  Assert-Contains -Content $reviewContent -Needle "SKIPPED: auto_commit disabled" -Label "auto_commit=false skips commit"
  Assert-Contains -Content $reviewContent -Needle "SKIPPED: no new commit to push" -Label "auto_push skips without commit"

  $config.review.auto_commit = $true
  $config.review.auto_push = $false
  Save-Config -Value $config
  Commit-Config -Message "config: review auto_commit on"
  & (Join-Path $automationCopy "review.ps1") -RepoRoot $repoRoot | Out-Null

  $reviewContent = Get-Content -Raw $reviewLog.FullName
  Assert-Contains -Content $reviewContent -Needle "SKIPPED: no staged changes to commit" -Label "no changes skip commit"

  $yesterday = (Get-Date).AddDays(-1).ToString("yyyyMMdd")
  Set-Content -Path (Join-Path $reportsRoot "governance-proposals-$yesterday.md") -Value "# Proposals`n"
  $config.implement.branch_prefix = "compound-" + [guid]::NewGuid().ToString("N").Substring(0, 6)
  $config.implement.create_pr = $false
  Save-Config -Value $config
  Commit-Config -Message "config: implement baseline"
  & (Join-Path $automationCopy "implement.ps1") -RepoRoot $repoRoot | Out-Null

  $implementLog = Get-ChildItem -Path $logDir -Filter "compound-implement-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $implementLog) {
    throw "FAIL: implement log not found"
  }
  $implementContent = Get-Content -Raw $implementLog.FullName
  Assert-Contains -Content $implementContent -Needle "Using latest governance proposals:" -Label "governance proposals fallback"

  if ($IncludePrCheck) {
    $stubDir = Join-Path $workRoot "bin"
    New-Item -ItemType Directory -Path $stubDir -Force | Out-Null
    $ghLog = Join-Path $workRoot "gh-args.txt"
    $ghCmd = Join-Path $stubDir "gh.cmd"
    Set-Content -Path $ghCmd -Value "@echo off`n echo %* >> `"$ghLog`"`n exit /b 0`n" -Encoding ASCII
    $env:PATH = "$stubDir;$env:PATH"

    $config.implement.branch_prefix = "compound-" + [guid]::NewGuid().ToString("N").Substring(0, 6)
    $config.implement.create_pr = $true
    $config.implement.pr_draft = $false
    Save-Config -Value $config
    Commit-Config -Message "config: implement pr check"
    & (Join-Path $automationCopy "implement.ps1") -RepoRoot $repoRoot | Out-Null

    if (-not (Test-Path $ghLog)) {
      throw "FAIL: gh args log not found"
    }
    $ghArgs = Get-Content -Raw $ghLog
    Assert-Contains -Content $ghArgs -Needle "--body" -Label "gh pr create includes --body"
  }

  Write-Output "All checks passed."
} finally {
  if ($cleanupWorkRoot) {
    if (Test-Path $workRoot) {
      Remove-Item -Recurse -Force $workRoot
    }
  } else {
    Write-Output "Work directory kept at: $workRoot"
  }
}
