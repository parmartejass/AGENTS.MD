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
  throw "FAILED_VALIDATION: Missing Python docs SSOT validator: $validatorPath"
}

$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot -RequireRepoRootForVendored
$pythonPath = Resolve-CheckPythonExecutable -RequestedPython $PythonExe
$successMarker = "docs-ssot-" + [guid]::NewGuid().ToString("N")
$expectedSuccessMarker = "VALIDATOR_SUCCESS_MARKER: $successMarker"
$arguments = @(
  $validatorPath,
  "--only-docs-ssot",
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
  -DisplayName "Python docs SSOT validator" `
  -ExpectedSuccessMarker $expectedSuccessMarker
