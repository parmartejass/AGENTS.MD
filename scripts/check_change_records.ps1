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

function Get-LegacyJsonValueKind([object]$value) {
  if ($null -eq $value) { return "Null" }
  if ($value -is [string]) { return "String" }
  if ($value -is [bool]) { if ($value) { return "True" } else { return "False" } }
  if ($value -is [System.Collections.IDictionary] -or $value -is [pscustomobject]) { return "Object" }
  if ($value -is [System.Collections.IEnumerable]) { return "Array" }
  if ($value -is [System.ValueType]) { return "Number" }
  return "Object"
}

function Get-LegacyJsonPathValueKind([string]$jsonText, [string[]]$path) {
  try {
    $current = ConvertFrom-JsonCompat $jsonText
  } catch {
    return $null
  }

  foreach ($segment in $path) {
    if ($null -eq $current) { return $null }

    if ($current -is [System.Collections.IDictionary]) {
      if (-not ($current.Keys -contains $segment)) { return $null }
      $current = $current[$segment]
      continue
    }

    if ($current -is [pscustomobject]) {
      $prop = $current.PSObject.Properties[$segment]
      if ($null -eq $prop) { return $null }
      $current = $prop.Value
      continue
    }

    return $null
  }

  return Get-LegacyJsonValueKind $current
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

function Test-NonEmptyArrayElement([object]$value) {
  if ($null -eq $value) { return $false }
  if ($value -is [string]) {
    return -not [string]::IsNullOrWhiteSpace($value)
  }
  if ($value -is [System.Collections.IDictionary]) {
    return $value.Count -gt 0
  }
  if ($value -is [pscustomobject]) {
    return $value.PSObject.Properties.Count -gt 0
  }
  return Test-NonEmptyValue $value
}

function Get-JsonPathValueKind([string]$jsonText, [string[]]$path) {
  $jsonDocType = "System.Text.Json.JsonDocument" -as [type]
  if ($null -eq $jsonDocType) {
    return Get-LegacyJsonPathValueKind $jsonText $path
  }

  try {
    $doc = [System.Text.Json.JsonDocument]::Parse($jsonText)
  } catch {
    return Get-LegacyJsonPathValueKind $jsonText $path
  }

  try {
    $current = $doc.RootElement
    foreach ($segment in $path) {
      if ($current.ValueKind -ne [System.Text.Json.JsonValueKind]::Object) {
        return $null
      }
      $next = [System.Text.Json.JsonElement]::new()
      if (-not $current.TryGetProperty($segment, [ref]$next)) {
        return $null
      }
      $current = $next
    }
    return $current.ValueKind.ToString()
  } finally {
    $doc.Dispose()
  }
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

$councilFullRequired = @(
  "council_run_id",
  "phase",
  "intent_coverage",
  "reviewers",
  "findings",
  "conflicts",
  "reconciliation_decision",
  "residual_risks",
  "go_no_go",
  "verification_links"
)

$councilAbbreviatedRequired = @(
  "intent_coverage",
  "findings",
  "residual_risks",
  "go_no_go"
)
$councilFullOnlyFields = @($councilFullRequired | Where-Object { $councilAbbreviatedRequired -notcontains $_ })

$councilPhasesAllowed = @("pre_change", "post_change")
$councilGoNoGoAllowed = @("go", "hold")
$councilIntentRequired = @("ssot_duplication", "silent_error", "edge_case", "resource_security_perf")

function Test-IsGovernanceScopedRecord([object]$record) {
  $owners = Get-PropertyValue $record "ssot_owner_paths"
  if ($null -eq $owners) { return $false }

  $ownerPaths = Convert-ToArray $owners
  foreach ($ownerPath in $ownerPaths) {
    if (-not ($ownerPath -is [string])) { continue }
    $norm = $ownerPath.Trim().Replace("\\", "/")
    if ($norm -eq "AGENTS.md" -or
        $norm -eq "agents-manifest.yaml" -or
        $norm.StartsWith("docs/agents/") -or
        $norm.StartsWith("scripts/check_")) {
      return $true
    }
  }

  return $false
}

$issues = New-Object System.Collections.Generic.List[string]
$validRecords = 0

foreach ($recordFile in $recordFiles) {
  $record = $null
  $recordText = $null

  try {
    $recordText = Get-Content -Raw -Path $recordFile.FullName
  } catch {
    Add-Issue $issues "Failed to read $($recordFile.FullName): $($_.Exception.Message)"
    continue
  }

  try {
    $record = ConvertFrom-JsonCompat $recordText
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

  if ((Get-JsonPathValueKind $recordText @("invariants")) -ne "Array") {
    Add-Issue $issues "'invariants' must be a JSON array in $($recordFile.FullName)."
    $recordHasErrors = $true
  }
  $invariants = Convert-ToArray (Get-PropertyValue $record "invariants")
  $invariantCount = 0
  foreach ($invariant in $invariants) {
    $invariantCount++
    if (-not ($invariant -is [string]) -or [string]::IsNullOrWhiteSpace($invariant)) {
      Add-Issue $issues "invariants[$invariantCount] must be a non-empty string in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }
  if ($invariantCount -eq 0) {
    Add-Issue $issues "invariants must contain at least one entry in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  if ((Get-JsonPathValueKind $recordText @("ssot_owner_paths")) -ne "Array") {
    Add-Issue $issues "'ssot_owner_paths' must be a JSON array in $($recordFile.FullName)."
    $recordHasErrors = $true
  }
  $ssotOwnerPaths = Convert-ToArray (Get-PropertyValue $record "ssot_owner_paths")
  $ownerPathCount = 0
  foreach ($ownerPath in $ssotOwnerPaths) {
    $ownerPathCount++
    if (-not ($ownerPath -is [string]) -or [string]::IsNullOrWhiteSpace($ownerPath)) {
      Add-Issue $issues "ssot_owner_paths[$ownerPathCount] must be a non-empty string in $($recordFile.FullName)."
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

  if ((Get-JsonPathValueKind $recordText @("verification_commands")) -ne "Array") {
    Add-Issue $issues "'verification_commands' must be a JSON array in $($recordFile.FullName)."
    $recordHasErrors = $true
  }
  $verificationCommands = Convert-ToArray (Get-PropertyValue $record "verification_commands")
  $verificationCount = 0
  foreach ($command in $verificationCommands) {
    $verificationCount++
    if (-not ($command -is [string]) -or [string]::IsNullOrWhiteSpace($command)) {
      Add-Issue $issues "verification_commands[$verificationCount] must be a non-empty string in $($recordFile.FullName)."
      $recordHasErrors = $true
    }
  }
  if ($verificationCount -eq 0) {
    Add-Issue $issues "verification_commands must contain at least one command in $($recordFile.FullName)."
    $recordHasErrors = $true
  }

  if ((Get-JsonPathValueKind $recordText @("witnesses")) -ne "Array") {
    Add-Issue $issues "'witnesses' must be a JSON array in $($recordFile.FullName)."
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
    if ((Get-JsonPathValueKind $recordText @("mre")) -ne "Object") {
      Add-Issue $issues "mre must be a JSON object in $($recordFile.FullName)."
      $recordHasErrors = $true
    } else {
      foreach ($field in $mreRequired) {
        $value = Get-PropertyValue $mre $field
        if (-not (Test-HasProperty $mre $field) -or -not (Test-NonEmptyValue $value)) {
          Add-Issue $issues "mre missing or empty '$field' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }
    }

    $tests = Get-PropertyValue $record "tests"
    if ((Get-JsonPathValueKind $recordText @("tests")) -ne "Object") {
      Add-Issue $issues "tests must be a JSON object in $($recordFile.FullName)."
      $recordHasErrors = $true
    } else {
      foreach ($field in $testsRequired) {
        $value = Get-PropertyValue $tests $field
        if (-not (Test-HasProperty $tests $field) -or -not (Test-NonEmptyValue $value)) {
          Add-Issue $issues "tests missing or empty '$field' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }
    }
  }

  if ($changeType -eq "docs" -and (Test-IsGovernanceScopedRecord $record)) {
    $council = Get-PropertyValue $record "council_summary"
    if (-not $council -or -not ($council -is [pscustomobject])) {
      Add-Issue $issues "Governance docs change record missing object field 'council_summary' in $($recordFile.FullName)."
      $recordHasErrors = $true
    } else {
      $missingFullFields = @()
      foreach ($field in $councilFullRequired) {
        $value = Get-PropertyValue $council $field
        if (-not (Test-HasProperty $council $field) -or -not (Test-NonEmptyValue $value)) {
          $missingFullFields += $field
        }
      }

      $missingAbbreviatedFields = @()
      foreach ($field in $councilAbbreviatedRequired) {
        $value = Get-PropertyValue $council $field
        if (-not (Test-HasProperty $council $field) -or -not (Test-NonEmptyValue $value)) {
          $missingAbbreviatedFields += $field
        }
      }
      $hasFullOnlyKeys = $false
      foreach ($field in $councilFullOnlyFields) {
        if (Test-HasProperty $council $field) {
          $hasFullOnlyKeys = $true
          break
        }
      }

      $councilMode = "full"
      if ($missingFullFields.Count -gt 0) {
        if ($hasFullOnlyKeys) {
          foreach ($field in $missingFullFields) {
            Add-Issue $issues "Governance docs council_summary missing or empty '$field' in $($recordFile.FullName)."
          }
          Add-Issue $issues "Governance docs council_summary includes full-summary fields and must satisfy the full required set [$($councilFullRequired -join ', ')] in $($recordFile.FullName)."
          $recordHasErrors = $true
        } elseif ($missingAbbreviatedFields.Count -gt 0) {
          foreach ($field in $missingAbbreviatedFields) {
            Add-Issue $issues "Governance docs council_summary missing or empty '$field' in $($recordFile.FullName)."
          }
          Add-Issue $issues "Governance docs council_summary must provide either the full summary fields [$($councilFullRequired -join ', ')] or the abbreviated fields [$($councilAbbreviatedRequired -join ', ')] in $($recordFile.FullName)."
          $recordHasErrors = $true
        } else {
          $councilMode = "abbreviated"
        }
      }

      if ($councilMode -eq "full") {
        $reviewersValue = Get-PropertyValue $council "reviewers"
        if ((Get-JsonPathValueKind $recordText @("council_summary", "reviewers")) -ne "Array") {
          Add-Issue $issues "Governance docs council_summary.reviewers must be a non-empty array in $($recordFile.FullName)."
          $recordHasErrors = $true
        } else {
          $reviewers = Convert-ToArray $reviewersValue
          $reviewersNonEmpty = @($reviewers | Where-Object { Test-NonEmptyArrayElement $_ })
          if ($reviewersNonEmpty.Count -eq 0) {
            Add-Issue $issues "Governance docs council_summary.reviewers must be a non-empty array in $($recordFile.FullName)."
            $recordHasErrors = $true
          }
        }
      }

      $findingsValue = Get-PropertyValue $council "findings"
      $findingsKind = Get-JsonPathValueKind $recordText @("council_summary", "findings")
      $findingsAreNonEmptyArray = $false
      if ($findingsKind -eq "Array") {
        $findings = Convert-ToArray $findingsValue
        $findingsNonEmpty = @($findings | Where-Object { Test-NonEmptyArrayElement $_ })
        if ($findingsNonEmpty.Count -gt 0) {
          $findingsAreNonEmptyArray = $true
        }
      }

      if ($councilMode -eq "full") {
        if (-not $findingsAreNonEmptyArray) {
          Add-Issue $issues "Governance docs council_summary.findings must be a non-empty array in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      } else {
        $explicitNoFindings = ($findingsValue -is [string]) -and ($findingsValue.Trim().ToLowerInvariant() -eq "no findings")
        if (-not $findingsAreNonEmptyArray -and -not $explicitNoFindings) {
          Add-Issue $issues "Governance docs abbreviated council_summary.findings must be a non-empty array or the explicit string 'No findings' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }

      if ($councilMode -eq "full") {
        $verificationLinksValue = Get-PropertyValue $council "verification_links"
        if ((Get-JsonPathValueKind $recordText @("council_summary", "verification_links")) -ne "Array") {
          Add-Issue $issues "Governance docs council_summary.verification_links must be a non-empty array in $($recordFile.FullName)."
          $recordHasErrors = $true
        } else {
          $verificationLinks = Convert-ToArray $verificationLinksValue
          $validVerificationLinks = 0
          $invalidVerificationLinks = 0
          foreach ($verificationLink in $verificationLinks) {
            if ($verificationLink -is [string] -and -not [string]::IsNullOrWhiteSpace($verificationLink)) {
              $validVerificationLinks++
            } else {
              $invalidVerificationLinks++
            }
          }
          if ($validVerificationLinks -eq 0 -or $invalidVerificationLinks -gt 0) {
            Add-Issue $issues "Governance docs council_summary.verification_links must be a non-empty array of strings in $($recordFile.FullName)."
            $recordHasErrors = $true
          }
        }
      }

      $phase = Get-PropertyValue $council "phase"
      if (Test-NonEmptyValue $phase) {
        if ($councilPhasesAllowed -notcontains $phase) {
          Add-Issue $issues "Governance docs council_summary.phase must be one of: $($councilPhasesAllowed -join ', ') in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }

      $goNoGo = Get-PropertyValue $council "go_no_go"
      if (Test-NonEmptyValue $goNoGo) {
        if ($councilGoNoGoAllowed -notcontains $goNoGo) {
          Add-Issue $issues "Governance docs council_summary.go_no_go must be one of: $($councilGoNoGoAllowed -join ', ') in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }

      $intentCoverageValue = Get-PropertyValue $council "intent_coverage"
      if ((Get-JsonPathValueKind $recordText @("council_summary", "intent_coverage")) -ne "Array") {
        Add-Issue $issues "Governance docs council_summary.intent_coverage must be a non-empty array in $($recordFile.FullName)."
        $recordHasErrors = $true
      } else {
        $intentCoverageRaw = Convert-ToArray $intentCoverageValue
        $intentCoverage = @()
        foreach ($intentItem in $intentCoverageRaw) {
          if (-not ($intentItem -is [string]) -or [string]::IsNullOrWhiteSpace($intentItem)) {
            Add-Issue $issues "Governance docs council_summary.intent_coverage must contain only non-empty strings in $($recordFile.FullName)."
            $recordHasErrors = $true
            continue
          }
          $intentCoverage += $intentItem.Trim()
        }

        if ($intentCoverage.Count -eq 0) {
          Add-Issue $issues "Governance docs council_summary.intent_coverage must be a non-empty array in $($recordFile.FullName)."
          $recordHasErrors = $true
        } else {
          foreach ($intent in $councilIntentRequired) {
            if ($intentCoverage -notcontains $intent) {
              Add-Issue $issues "Governance docs council_summary.intent_coverage missing '$intent' in $($recordFile.FullName)."
              $recordHasErrors = $true
            }
          }
        }
      }
    }

    $validationContext = Get-PropertyValue $record "validation_context"
    if (-not $validationContext -or -not ($validationContext -is [pscustomobject])) {
      Add-Issue $issues "Governance docs change record missing object field 'validation_context' in $($recordFile.FullName)."
      $recordHasErrors = $true
    } else {
      foreach ($field in @("intended_environment", "evidence_plan", "release_gate_decision")) {
        $value = Get-PropertyValue $validationContext $field
        if (-not (Test-HasProperty $validationContext $field) -or -not (Test-NonEmptyValue $value)) {
          Add-Issue $issues "Governance docs validation_context missing or empty '$field' in $($recordFile.FullName)."
          $recordHasErrors = $true
        }
      }

      $traceabilityRefs = Convert-ToArray (Get-PropertyValue $validationContext "traceability_refs")
      if ($traceabilityRefs.Count -eq 0) {
        Add-Issue $issues "Governance docs validation_context.traceability_refs must be a non-empty array in $($recordFile.FullName)."
        $recordHasErrors = $true
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
