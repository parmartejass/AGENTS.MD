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

  $timestamp = Get-Date -Format "yyyyMMdd"
  $logPath = Join-Path $logDir "compound-review-$timestamp.log"
  Set-LogPath -Path $logPath

  Write-Log "Starting review run"
  Write-Log "Repo root: $repoRoot"

  Assert-RepoClean -RepoRoot $repoRoot
  Invoke-Git -RepoRoot $repoRoot -GitArgs @("checkout", $config.git.main_branch)
  Invoke-Git -RepoRoot $repoRoot -GitArgs @("pull", $config.git.remote, $config.git.main_branch)

  $learningDoc = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $config.paths.learning_doc
  $priorityReport = Resolve-RepoPath -RepoRoot $repoRoot -PathValue $config.paths.priority_report
  $governanceProposals = Resolve-RepoPath -RepoRoot $repoRoot -PathValue (Expand-DateToken -PathTemplate $config.paths.governance_proposals -DateToken $timestamp)
  $reviewReport = Resolve-RepoPath -RepoRoot $repoRoot -PathValue (Expand-DateToken -PathTemplate $config.paths.review_report -DateToken $timestamp)

  Initialize-Directory -Path (Split-Path -Parent $governanceProposals)
  Initialize-Directory -Path (Split-Path -Parent $reviewReport)

  $promptTemplate = Resolve-AutomationPath -AutomationRoot $AutomationRoot -PathValue $config.review.prompt_template
  $prompt = Format-Prompt -TemplatePath $promptTemplate -Tokens @{
    REPO_ROOT = $repoRoot
    LEARNING_DOC = $learningDoc
    PRIORITY_REPORT = $priorityReport
    GOVERNANCE_PROPOSALS = $governanceProposals
    REVIEW_REPORT = $reviewReport
    AUTOMATION_ROOT = $AutomationRoot
  }

  Invoke-Agent -Config $config -PromptText $prompt
  Assert-GovernanceClean -RepoRoot $repoRoot -Config $config

  $didCommit = $false

  if ($config.review.auto_commit) {
    $pathsToAdd = @()
    if (Test-Path $learningDoc) { $pathsToAdd += $learningDoc }
    if (Test-Path $governanceProposals) { $pathsToAdd += $governanceProposals }
    if (Test-Path $reviewReport) { $pathsToAdd += $reviewReport }

    if ($pathsToAdd.Count -gt 0) {
      $gitAddArgs = @("add") + $pathsToAdd
      Invoke-Git -RepoRoot $repoRoot -GitArgs $gitAddArgs

      & git -C $repoRoot diff --cached --quiet
      if ($LASTEXITCODE -eq 0) {
        Write-Log "SKIPPED: no staged changes to commit"
      } elseif ($LASTEXITCODE -eq 1) {
        $commitMessage = "Nightly review learnings ($timestamp)"
        Invoke-Git -RepoRoot $repoRoot -GitArgs @("commit", "-m", $commitMessage)
        $didCommit = $true
      } else {
        throw "git diff --cached --quiet failed with exit code $LASTEXITCODE"
      }
    } else {
      Write-Log "SKIPPED: no review artifacts found to commit"
    }
  } else {
    Write-Log "SKIPPED: auto_commit disabled"
  }

  if ($config.review.auto_push) {
    if ($didCommit) {
      Invoke-Git -RepoRoot $repoRoot -GitArgs @("push", $config.git.remote, $config.git.main_branch)
    } else {
      Write-Log "SKIPPED: no new commit to push"
    }
  }

  Write-Log "Review run complete"
} finally {
  Pop-Location
}
