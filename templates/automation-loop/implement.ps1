param(
  [string]$RepoRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AutomationRoot = $PSScriptRoot
. (Join-Path $AutomationRoot "automation-lib.ps1")

$config = Read-AutomationConfig -AutomationRoot $AutomationRoot
$repoRoot = Get-RepoRoot -Override $RepoRoot -AutomationRoot $AutomationRoot

Push-Location $repoRoot
try {
  $logDir = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $config.paths.logs_dir
  Initialize-Directory -Path $logDir

  $timestamp = Get-Date -Format "yyyyMMdd-HHmm"
  $logPath = Join-Path $logDir "compound-implement-$timestamp.log"
  Set-LogPath -Path $logPath

  Write-Log "Starting implement run"
  Write-Log "Repo root: $repoRoot"

  Assert-RepoClean -RepoRoot $repoRoot
  Invoke-Git -RepoRoot $repoRoot -GitArgs @("checkout", $config.git.main_branch)
  Invoke-Git -RepoRoot $repoRoot -GitArgs @("pull", $config.git.remote, $config.git.main_branch)

  $branchName = "$($config.implement.branch_prefix)-$timestamp"
  Invoke-Git -RepoRoot $repoRoot -GitArgs @("checkout", "-b", $branchName)
  Write-Log "Created branch: $branchName"

  $learningDoc = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $config.paths.learning_doc
  $priorityReport = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $config.paths.priority_report

  $governanceTemplate = $config.paths.governance_proposals
  $governanceDate = Get-Date -Format "yyyyMMdd"
  $governanceExpanded = Expand-DateToken -PathTemplate $governanceTemplate -DateToken $governanceDate
  $governanceProposals = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $governanceExpanded

  if (-not (Test-Path $governanceProposals) -and ($governanceTemplate -like "*{date}*")) {
    $wildcardTemplate = $governanceTemplate -replace "\{date\}", "*"
    $wildcardPath = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $wildcardTemplate
    $wildcardDir = Split-Path -Parent $wildcardPath
    $wildcardPattern = Split-Path -Leaf $wildcardPath

    if (Test-Path $wildcardDir) {
      $candidate = Get-ChildItem -Path $wildcardDir -Filter $wildcardPattern -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
      if ($candidate) {
        $governanceProposals = $candidate.FullName
        Write-Log "Using latest governance proposals: $governanceProposals"
      } else {
        Write-Log "SKIPPED: governance proposals not found for $governanceDate" "WARN"
      }
    } else {
      Write-Log "SKIPPED: governance proposals directory not found: $wildcardDir" "WARN"
    }
  }

  $promptTemplate = Resolve-AutomationPath -AutomationRoot $AutomationRoot -PathValue $config.implement.prompt_template
  $prompt = Format-Prompt -TemplatePath $promptTemplate -Tokens @{
    REPO_ROOT = $repoRoot
    LEARNING_DOC = $learningDoc
    PRIORITY_REPORT = $priorityReport
    GOVERNANCE_PROPOSALS = $governanceProposals
    REVIEW_REPORT = ""
    AUTOMATION_ROOT = $AutomationRoot
  }

  Invoke-Agent -Config $config -PromptText $prompt
  Assert-GovernanceClean -RepoRoot $repoRoot -Config $config

  if ($config.implement.create_pr) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
      Write-Log "gh CLI not found; skipping PR creation" "WARN"
    } else {
      $title = "Compound: $branchName"
      $ghArgs = @("pr", "create", "--title", $title, "--base", $config.git.main_branch, "--body", "")
      if ($config.implement.pr_draft) {
        $ghArgs += "--draft"
      }
      & $gh @ghArgs
      if ($LASTEXITCODE -ne 0) {
        throw "gh pr create failed"
      }
    }
  }

  Write-Log "Implement run complete"
} finally {
  Pop-Location
}
