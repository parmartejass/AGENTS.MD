$ErrorActionPreference = "Stop"

function Get-RegistryPropertyValue {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Object,
    [Parameter(Mandatory = $true)]
    [string]$Name
  )

  if ($null -eq $Object) {
    return $null
  }

  if ($Object -is [System.Collections.IDictionary]) {
    if ($Object.Contains($Name)) {
      return $Object[$Name]
    }
    return $null
  }

  $property = $Object.PSObject.Properties[$Name]
  if ($null -eq $property) {
    return $null
  }

  return $property.Value
}

function Test-RegistryObject {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Value
  )

  return $null -ne $Value -and (
    $Value -is [System.Collections.IDictionary] -or
    $Value -is [pscustomobject]
  )
}

function Require-RegistryObject {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Container,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [Parameter(Mandatory = $true)]
    [string]$RegistryDisplay
  )

  $value = Get-RegistryPropertyValue -Object $Container -Name $Name
  if (-not (Test-RegistryObject -Value $value)) {
    throw "Missing object key '$Label' in $RegistryDisplay."
  }
  return $value
}

function Require-RegistryString {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Container,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [Parameter(Mandatory = $true)]
    [string]$RegistryDisplay
  )

  $value = Get-RegistryPropertyValue -Object $Container -Name $Name
  if ($value -isnot [string] -or [string]::IsNullOrWhiteSpace($value)) {
    throw "Missing string key '$Label' in $RegistryDisplay."
  }
  return $value
}

function Require-RegistryStringList {
  param(
    [Parameter(Mandatory = $true)]
    [object]$Container,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [Parameter(Mandatory = $true)]
    [string]$RegistryDisplay
  )

  $value = Get-RegistryPropertyValue -Object $Container -Name $Name
  if ($null -eq $value -or $value -is [string] -or $value -isnot [System.Collections.IEnumerable]) {
    throw "Missing string-list key '$Label' in $RegistryDisplay."
  }

  $items = @()
  foreach ($item in $value) {
    if ($item -isnot [string] -or [string]::IsNullOrWhiteSpace($item)) {
      throw "Missing string-list key '$Label' in $RegistryDisplay."
    }
    $items += $item
  }

  if ($items.Count -eq 0) {
    throw "Missing string-list key '$Label' in $RegistryDisplay."
  }

  return $items
}

function Get-DocsEntrypointContractContext {
  param(
    [Parameter(Mandatory = $true)]
    [string]$RegistryPath
  )

  $registryDisplay = "scripts/entrypoint_contracts.json"
  if (-not (Test-Path $RegistryPath -PathType Leaf)) {
    throw "Missing entrypoint-contract registry: $RegistryPath"
  }

  try {
    $registry = Get-Content -Raw -Path $RegistryPath | ConvertFrom-Json
  } catch {
    throw "Invalid JSON in ${RegistryPath}: $($_.Exception.Message)"
  }

  $version = Get-RegistryPropertyValue -Object $registry -Name "version"
  if ($version -ne 1) {
    throw "Unsupported entrypoint-contract registry version in $RegistryPath."
  }

  $docsContract = Require-RegistryObject `
    -Container $registry `
    -Name "docs" `
    -Label "docs" `
    -RegistryDisplay $registryDisplay
  $authorityResolution = Require-RegistryObject `
    -Container $docsContract `
    -Name "authority_resolution" `
    -Label "docs.authority_resolution" `
    -RegistryDisplay $registryDisplay
  $publicLeafModel = Require-RegistryObject `
    -Container $docsContract `
    -Name "public_leaf_model" `
    -Label "docs.public_leaf_model" `
    -RegistryDisplay $registryDisplay
  $publicLeafPatterns = Require-RegistryObject `
    -Container $docsContract `
    -Name "public_leaf_patterns" `
    -Label "docs.public_leaf_patterns" `
    -RegistryDisplay $registryDisplay
  $exceptions = Require-RegistryObject `
    -Container $docsContract `
    -Name "explicit_family_exceptions" `
    -Label "docs.explicit_family_exceptions" `
    -RegistryDisplay $registryDisplay

  $routerPattern = Require-RegistryString `
    -Container $docsContract `
    -Name "router_pattern" `
    -Label "docs.router_pattern" `
    -RegistryDisplay $registryDisplay
  $numberedRegexPattern = Require-RegistryString `
    -Container $authorityResolution `
    -Name "numbered_governance_folder_regex" `
    -Label "docs.authority_resolution.numbered_governance_folder_regex" `
    -RegistryDisplay $registryDisplay
  $datedRegexPattern = Require-RegistryString `
    -Container $authorityResolution `
    -Name "dated_evidence_folder_regex" `
    -Label "docs.authority_resolution.dated_evidence_folder_regex" `
    -RegistryDisplay $registryDisplay
  $datedAuthority = Require-RegistryString `
    -Container $authorityResolution `
    -Name "dated_evidence_authority" `
    -Label "docs.authority_resolution.dated_evidence_authority" `
    -RegistryDisplay $registryDisplay
  $plainFolderDefault = Require-RegistryString `
    -Container $publicLeafPatterns `
    -Name "plain_folder_default" `
    -Label "docs.public_leaf_patterns.plain_folder_default" `
    -RegistryDisplay $registryDisplay
  $numberedGovernanceFolder = Require-RegistryString `
    -Container $publicLeafPatterns `
    -Name "numbered_governance_folder" `
    -Label "docs.public_leaf_patterns.numbered_governance_folder" `
    -RegistryDisplay $registryDisplay
  $datedEvidenceFolder = Require-RegistryString `
    -Container $publicLeafPatterns `
    -Name "dated_evidence_folder" `
    -Label "docs.public_leaf_patterns.dated_evidence_folder" `
    -RegistryDisplay $registryDisplay

  $minimumLeafCountRaw = Get-RegistryPropertyValue -Object $publicLeafModel -Name "minimum_public_leaf_count"
  $minimumLeafCount = 0
  if (
    $null -eq $minimumLeafCountRaw -or
    -not [int]::TryParse("$minimumLeafCountRaw", [ref]$minimumLeafCount) -or
    $minimumLeafCount -lt 0
  ) {
    throw "Missing integer key 'docs.public_leaf_model.minimum_public_leaf_count' in $registryDisplay."
  }

  $identityFiles = Require-RegistryStringList `
    -Container $exceptions `
    -Name "identity_files" `
    -Label "docs.explicit_family_exceptions.identity_files" `
    -RegistryDisplay $registryDisplay

  try {
    $numberedRegex = [regex]($numberedRegexPattern -replace '\(\?P<([A-Za-z_][A-Za-z0-9_]*)>', '(?<$1>')
  } catch {
    throw "Invalid regex for docs.authority_resolution.numbered_governance_folder_regex in ${registryDisplay}: $($_.Exception.Message)"
  }

  try {
    $datedRegex = [regex]$datedRegexPattern
  } catch {
    throw "Invalid regex for docs.authority_resolution.dated_evidence_folder_regex in ${registryDisplay}: $($_.Exception.Message)"
  }

  return [pscustomobject]@{
    Registry = $registry
    DocsContract = $docsContract
    NumberedRegex = $numberedRegex
    DatedRegex = $datedRegex
    DatedAuthority = $datedAuthority
    RouterPattern = $routerPattern
    MinimumLeafCount = $minimumLeafCount
    PlainFolderDefault = $plainFolderDefault
    NumberedGovernanceFolder = $numberedGovernanceFolder
    DatedEvidenceFolder = $datedEvidenceFolder
    IdentityFiles = $identityFiles
  }
}

function Resolve-EntrypointDocsAuthority {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FolderName,
    [Parameter(Mandatory = $true)]
    [object]$ContractContext
  )

  $match = $ContractContext.NumberedRegex.Match($FolderName)
  if ($match.Success) {
    return $match.Groups["authority"].Value
  }
  if ($ContractContext.DatedRegex.IsMatch($FolderName)) {
    return $ContractContext.DatedAuthority
  }
  return $FolderName
}

function Resolve-EntrypointDocsRouterFilename {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FolderName,
    [Parameter(Mandatory = $true)]
    [object]$ContractContext
  )

  return $ContractContext.RouterPattern.Replace(
    "<authority>",
    (Resolve-EntrypointDocsAuthority -FolderName $FolderName -ContractContext $ContractContext)
  )
}

function Resolve-EntrypointPrimaryLeafFilename {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FolderName,
    [Parameter(Mandatory = $true)]
    [object]$ContractContext
  )

  $authority = Resolve-EntrypointDocsAuthority -FolderName $FolderName -ContractContext $ContractContext
  if ($ContractContext.DatedRegex.IsMatch($FolderName)) {
    return $ContractContext.DatedEvidenceFolder.Replace("<authority>", $authority)
  }
  if ($ContractContext.NumberedRegex.IsMatch($FolderName)) {
    return $ContractContext.NumberedGovernanceFolder.Replace("<authority>", $authority)
  }
  return $ContractContext.PlainFolderDefault.Replace("<authority>", $authority)
}

function Test-EntrypointCaseSensitiveContains {
  param(
    [Parameter(Mandatory = $true)]
    [System.Collections.IEnumerable]$Values,
    [Parameter(Mandatory = $true)]
    [string]$Expected
  )

  foreach ($value in $Values) {
    if ("$value" -ceq $Expected) {
      return $true
    }
  }

  return $false
}
