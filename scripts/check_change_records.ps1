param(
  [string]$RepoRoot,
  [string]$GovernanceRoot,
  [string]$PythonExe,
  [switch]$RequireRecords
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
. (Join-Path $PSScriptRoot "_python_check_runner.ps1")

$timeoutMilliseconds = 120000
$validatorPath = Join-Path $PSScriptRoot "check_governance_core\check_governance_core_main.py"
if (-not (Test-Path -LiteralPath $validatorPath -PathType Leaf)) {
  throw "FAILED_VALIDATION: Missing Python change-record validator: $validatorPath"
}

$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot -RequireRepoRootForVendored
$pythonPath = Resolve-CheckPythonExecutable -RequestedPython $PythonExe
$successMarker = "change-records-" + [guid]::NewGuid().ToString("N")
$expectedSuccessMarker = "VALIDATOR_SUCCESS_MARKER: $successMarker"
$arguments = @(
  $validatorPath,
  "--only-change-records",
  "--success-marker",
  $successMarker,
  "--repo-root",
  $context.RepoRoot,
  "--governance-root",
  $context.GovernanceRoot
)
if ($RequireRecords) {
  $arguments += "--require-records"
}

Invoke-PythonCheck `
  -PythonPath $pythonPath `
  -Arguments $arguments `
  -WorkingDirectory $PSScriptRoot `
  -TimeoutMilliseconds $timeoutMilliseconds `
  -DisplayName "Python change-record validator" `
  -ExpectedSuccessMarker $expectedSuccessMarker
