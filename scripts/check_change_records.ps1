param(
  [string]$RepoRoot,
  [string]$GovernanceRoot,
  [switch]$RequireRecords
)

$ErrorActionPreference = "Stop"

$repoRootProvided = $PSBoundParameters.ContainsKey('RepoRoot')
$governanceRootName = Split-Path -Leaf (Split-Path -Parent $PSScriptRoot)
if (-not $repoRootProvided -and $governanceRootName -eq ".governance") {
  throw "RepoRoot is required when running from a vendored governance submodule. Use -RepoRoot <target repo root> (e.g., -RepoRoot .)."
}

. (Join-Path $PSScriptRoot "_governance_paths.ps1")
$context = Get-GovernanceContext -RepoRoot $RepoRoot -GovernanceRoot $GovernanceRoot -ScriptRoot $PSScriptRoot

# Validates structured change-record artifacts when present.
# Required mode is enabled by -RequireRecords or docs/project/change-records/.required.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_change_records.ps1

$repoRootPath = $context.RepoRoot
$governanceRootPath = $context.GovernanceRoot

$recordsRoot = Join-Path $repoRootPath "docs/project/change-records"
$schemaPath = Join-Path $governanceRootPath "docs/agents/schemas/change-record.schema.json"
$requiredMarkerPath = Join-Path $recordsRoot ".required"
$recordsRequired = $RequireRecords -or (Test-Path -Path $requiredMarkerPath -PathType Leaf)

if (-not (Test-Path -Path $schemaPath -PathType Leaf)) {
  throw "Missing change-record schema: $schemaPath"
}

if (-not (Test-Path -Path $recordsRoot -PathType Container)) {
  if ($recordsRequired) {
    throw "Missing change-record directory: $recordsRoot"
  }

  Write-Host "SKIPPED: No change-record directory found at docs/project/change-records."
  exit 0
}

$recordFiles = @(Get-ChildItem -Path $recordsRoot -File -Filter "*.json" | Sort-Object FullName)
if ($recordFiles.Count -eq 0) {
  if ($recordsRequired) {
    throw "No change-record files found under: $recordsRoot"
  }

  Write-Host "SKIPPED: No change-record files (*.json) found under docs/project/change-records."
  exit 0
}

function Add-Issue([System.Collections.Generic.List[string]]$list, [string]$message) {
  $list.Add($message)
}

function ConvertFrom-JsonCompat([string]$jsonText) {
  $convertCmd = Get-Command ConvertFrom-Json
  if ($convertCmd.Parameters.ContainsKey("Depth")) {
    return $jsonText | ConvertFrom-Json -Depth 100
  }
  return $jsonText | ConvertFrom-Json
}

function Test-HasProperty([object]$obj, [string]$name) {
  if (-not $obj) { return $false }
  return $null -ne $obj.PSObject.Properties[$name]
}

function Get-PropertyValue([object]$obj, [string]$name) {
  if (Test-HasProperty $obj $name) {
    return $obj.PSObject.Properties[$name].Value
  }
  return $null
}

function Test-NonEmptyValue([object]$value) {
  if ($null -eq $value) { return $false }
  if ($value -is [string]) {
    return -not [string]::IsNullOrWhiteSpace($value)
  }
  if ($value -is [System.Collections.IEnumerable] -and -not ($value -is [string])) {
    foreach ($item in $value) {
      return $true
    }
    return $false
  }
  return $true
}

function Convert-ToArray([object]$value) {
  if ($null -eq $value) { return @() }
  if ($value -is [string]) { return @($value) }
  if ($value -is [pscustomobject]) { return @($value) }
  if ($value -is [System.Collections.IDictionary]) { return @($value) }
  if ($value -is [System.Collections.IEnumerable]) { return @($value) }
  return @($value)
}

try {
  $schema = ConvertFrom-JsonCompat (Get-Content -Raw -Path $schemaPath)
} catch {
  throw "Failed to parse schema JSON: $schemaPath. $($_.Exception.Message)"
}

if (-not $schema) {
  throw "Schema did not parse to an object: $schemaPath"
}

$allowedChangeTypes = @()
if ($schema.PSObject.Properties['properties'] -and $schema.properties.PSObject.Properties['change_type'] -and $schema.properties.change_type.PSObject.Properties['enum']) {
  $allowedChangeTypes = @($schema.properties.change_type.enum)
}

if ($allowedChangeTypes.Count -eq 0) {
  throw "Schema missing properties.change_type.enum in: $schemaPath"
}

$baseRequired = @()
if ($schema.PSObject.Properties['required']) {
  $baseRequired = @($schema.required)
}

if ($baseRequired.Count -eq 0) {
  throw "Schema missing required field list in: $schemaPath"
}

$bugfixRequired = @(
  "symptom_location",
  "authority_fix_point",
  "root_cause_statement",
  "class_of_errors_prevented",
  "mre",
  "tests"
)

$mreRequired = @(
  "fixture_path",
  "pre_fix_failure_signal",
  "post_fix_pass_signal"
)

$testsRequired = @(
  "regression",
  "disconfirming",
  "failure_path"
)

$witnessRequired = @(
  "invariant_id",
  "signal",
  "record_location",
  "pass_criteria"
)

$issues = New-Object System.Collections.Generic.List[string]
$validRecords = 0

foreach ($recordFile in $recordFiles) {
  $record = $null

  try {
    $record = ConvertFrom-JsonCompat (Get-Content -Raw -Path $recordFile.FullName)
  } catch {
    Add-Issue $issues "Failed to parse JSON in $($recordFile.FullName): $($_.Exception.Message)"
    continue
  }

  if (-not $record) {
    Add-Issue $issues "Parsed record is empty in $($recordFile.FullName)."
    continue
  }

  $recordHasErrors = $false

  foreach ($field in $baseRequired) {
    $value = Get-PropertyValue $record $field
    if (-not (Test-HasProperty $record $field) -or -not (Test-NonEmptyValue $value)) {
      Add-Issue $issues "Missing or empty required field '$field' in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }

  $invariants = Convert-ToArray (Get-PropertyValue $record "invariants")
  $invariantCount = 0
  foreach ($invariant in $invariants) {
    $invariantCount++
    if (-not (Test-NonEmptyValue $invariant)) {
      Add-Issue $issues "invariants[$invariantCount] is empty in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }
  if ($invariantCount -eq 0) {
    Add-Issue $issues "invariants must contain at least one entry in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  $ssotOwnerPaths = Convert-ToArray (Get-PropertyValue $record "ssot_owner_paths")
  $ownerPathCount = 0
  foreach ($ownerPath in $ssotOwnerPaths) {
    $ownerPathCount++
    if (-not (Test-NonEmptyValue $ownerPath)) {
      Add-Issue $issues "ssot_owner_paths[$ownerPathCount] is empty in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }
  if ($ownerPathCount -eq 0) {
    Add-Issue $issues "ssot_owner_paths must contain at least one entry in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  $changeType = Get-PropertyValue $record "change_type"
  if (-not (Test-NonEmptyValue $changeType)) {
    Add-Issue $issues "Missing or empty change_type in $($recordFile.FullName)."
    $recordHasErrors = $true
  } elseif ($allowedChangeTypes -notcontains $changeType) {
    Add-Issue $issues "Unknown change_type '$changeType' in $($recordFile.FullName). Allowed values: $($allowedChangeTypes -join ', ')."
    $recordHasErrors = $true
  }

  $verificationCommands = Convert-ToArray (Get-PropertyValue $record "verification_commands")
  $verificationCount = 0
  foreach ($command in $verificationCommands) {
    $verificationCount++
    if (-not (Test-NonEmptyValue $command)) {
      Add-Issue $issues "verification_commands contains an empty entry in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }
  if ($verificationCount -eq 0) {
    Add-Issue $issues "verification_commands must contain at least one command in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  $witnesses = Convert-ToArray (Get-PropertyValue $record "witnesses")
  $witnessCount = 0
  foreach ($witness in $witnesses) {
    $witnessCount++
    foreach ($field in $witnessRequired) {
      $value = Get-PropertyValue $witness $field
      if (-not (Test-HasProperty $witness $field) -or -not (Test-NonEmptyValue $value)) {
        Add-Issue $issues "witnesses[$witnessCount] missing or empty '$field' in $($recordFile.FullName)."
        $recordHasErrors = $true
      }
    }
  }
  if ($witnessCount -eq 0) {
    Add-Issue $issues "witnesses must contain at least one entry in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  if ($changeType -in @("bugfix", "regression")) {
    foreach ($field in $bugfixRequired) {
      $value = Get-PropertyValue $record $field
      if (-not (Test-HasProperty $record $field) -or -not (Test-NonEmptyValue $value)) {
        Add-Issue $issues "Bugfix/regression record missing or empty '$field' in $($recordFile.FullName)."
        $recordHasErrors = $true
      }
    }

    $mre = Get-PropertyValue $record "mre"
    if ($mre) {
      foreach ($field in $mreRequired) {
        $value = Get-PropertyValue $mre $field
        if (-not (Test-HasProperty $mre $field) -or -not (Test-NonEmptyValue $value)) {
          Add-Issue $issues "mre missing or empty '$field' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }
    }

    $tests = Get-PropertyValue $record "tests"
    if ($tests) {
      foreach ($field in $testsRequired) {
        $value = Get-PropertyValue $tests $field
        if (-not (Test-HasProperty $tests $field) -or -not (Test-NonEmptyValue $value)) {
          Add-Issue $issues "tests missing or empty '$field' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }
    }
  }

  if (-not $recordHasErrors) {
    $validRecords++
  }
}

if ($issues.Count -gt 0) {
  foreach ($issue in $issues) {
    Write-Host "ERROR: $issue"
  }
  throw "Change record check failed: $($issues.Count) issue(s)."
}

Write-Host "Change record checks passed. Valid records: $validRecords"
