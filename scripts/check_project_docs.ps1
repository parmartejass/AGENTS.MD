param(
  [string]$RepoRoot,
  [string]$GovernanceRoot,
  [string]$PythonExe
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
. (Join-Path $PSScriptRoot "_python_check_runner.ps1")

$timeoutMilliseconds = 120000
$validatorPath = Join-Path $PSScriptRoot "check_governance_core\check_governance_core_main.py"
if (-not (Test-Path -LiteralPath $validatorPath -PathType Leaf)) {
  throw "FAILED_VALIDATION: Missing Python project docs validator: $validatorPath"
}

$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot -RequireRepoRootForVendored
$pythonPath = Resolve-CheckPythonExecutable -RequestedPython $PythonExe
$successMarker = "project-docs-" + [guid]::NewGuid().ToString("N")
$expectedSuccessMarker = "VALIDATOR_SUCCESS_MARKER: $successMarker"
$arguments = @(
  $validatorPath,
  "--only-project-docs",
  "--success-marker",
  $successMarker,
  "--repo-root",
  $context.RepoRoot,
  "--governance-root",
  $context.GovernanceRoot
)

Invoke-PythonCheck `
  -PythonPath $pythonPath `
  -Arguments $arguments `
  -WorkingDirectory $PSScriptRoot `
  -TimeoutMilliseconds $timeoutMilliseconds `
  -DisplayName "Python project docs validator" `
  -ExpectedSuccessMarker $expectedSuccessMarker
