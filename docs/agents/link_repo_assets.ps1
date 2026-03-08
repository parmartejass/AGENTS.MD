[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$IncludeCompatibility,
    [string]$RepoRoot,
    [string[]]$Include = @("skills", "subagents", "mcp", "settings", "acp")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    return (Resolve-Path -LiteralPath $Path).ProviderPath.TrimEnd("\")
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
        return
    }

    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer) {
        throw "Expected a directory at '$Path', but found a file."
    }
}

function Test-IsLink {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileSystemInfo]$Item
    )

    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-LinkResolvedTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath
    )

    $item = Get-Item -LiteralPath $LinkPath -Force
    if (-not (Test-IsLink -Item $item)) {
        return Get-NormalizedPath -Path $LinkPath
    }

    $targetValue = @($item.Target) | Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($targetValue)) {
        return Get-NormalizedPath -Path $LinkPath
    }

    if (-not [System.IO.Path]::IsPathRooted($targetValue)) {
        $targetValue = Join-Path (Split-Path -Parent $LinkPath) $targetValue
    }

    return Get-NormalizedPath -Path $targetValue
}

function Get-RelativeLinkTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseDirectory,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    $baseUri = New-Object System.Uri(((Get-NormalizedPath -Path $BaseDirectory).TrimEnd("\") + "\"))
    $targetUri = New-Object System.Uri((Get-NormalizedPath -Path $TargetPath))
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace("/", "\")
}

function Test-HardLinkMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    return (Test-FileContentMatch -FirstPath $LinkPath -SecondPath $TargetPath)
}

function Remove-LinkPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Remove-Item -LiteralPath $Path -Force -ErrorAction Stop
}

function Test-FileContentMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FirstPath,
        [Parameter(Mandatory = $true)]
        [string]$SecondPath
    )

    if ((-not (Test-Path -LiteralPath $FirstPath -PathType Leaf)) -or (-not (Test-Path -LiteralPath $SecondPath -PathType Leaf))) {
        return $false
    }

    return ((Get-FileHash -LiteralPath $FirstPath).Hash -eq (Get-FileHash -LiteralPath $SecondPath).Hash)
}

function Ensure-DirectoryLink {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath,
        [switch]$UseRelativeTarget,
        [switch]$AllowReplace,
        [switch]$PreserveExistingNonLink
    )

    $expectedResolved = Get-NormalizedPath -Path $TargetPath
    $existing = Get-Item -LiteralPath $LinkPath -Force -ErrorAction SilentlyContinue

    if ($null -ne $existing) {
        if (-not (Test-IsLink -Item $existing)) {
            if ($PreserveExistingNonLink) {
                Write-Host "PRESERVED directory-link target '$LinkPath' as an existing non-link directory. The canonical source remains '$expectedResolved'."
                return
            }
            throw "Refusing to replace non-link path '$LinkPath'. Remove or rename it manually."
        }

        $actualResolved = $null
        try {
            $actualResolved = Get-LinkResolvedTarget -LinkPath $LinkPath
        } catch {
            $actualResolved = $null
        }

        if ($actualResolved -eq $expectedResolved) {
            Write-Output "OK     $LinkPath -> $expectedResolved"
            return
        }

        if (-not $AllowReplace) {
            $existingTarget = ""
            if ($null -ne $existing.Target) {
                $existingTarget = ($existing.Target -join ", ")
            }
            throw "Existing link '$LinkPath' points somewhere else ('$existingTarget'). Re-run with -Force to replace the link only."
        }

        try {
            Remove-LinkPath -Path $LinkPath
        } catch {
            throw "Failed to remove existing link directory '$LinkPath'. $($_.Exception.Message)"
        }
    }

    $linkParent = Split-Path -Parent $LinkPath
    Ensure-Directory -Path $linkParent

    $linkTarget = $TargetPath
    if ($UseRelativeTarget) {
        $linkTarget = Get-RelativeLinkTarget -BaseDirectory $linkParent -TargetPath $TargetPath
    }

    $linkKind = "symbolic-link"
    $symlinkError = $null
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $linkTarget | Out-Null
    } catch {
        $symlinkError = $_.Exception.Message
        if ($IsWindows) {
            try {
                New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
                $linkKind = "junction"
            } catch {
                $junctionError = $_.Exception.Message
                throw "Failed to create a directory link at '$LinkPath'. Tried symbolic link target '$linkTarget' and junction target '$TargetPath'. Enable Developer Mode or run an elevated shell for true symlinks, then rerun this script. Symlink error: '$symlinkError'. Junction error: '$junctionError'."
            }
        } else {
            throw "Failed to create a directory symbolic link at '$LinkPath'. Symlink error: '$symlinkError'."
        }
    }

    $verifiedResolved = Get-LinkResolvedTarget -LinkPath $LinkPath
    if ($verifiedResolved -ne $expectedResolved) {
        throw "Link verification failed for '$LinkPath'. Expected '$expectedResolved', got '$verifiedResolved'."
    }

    Write-Output "LINKED [$linkKind] $LinkPath -> $expectedResolved"
}

function Ensure-FileLink {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath,
        [switch]$AllowReplace
    )

    $expectedResolved = Get-NormalizedPath -Path $TargetPath
    $existing = Get-Item -LiteralPath $LinkPath -Force -ErrorAction SilentlyContinue

    if ($null -ne $existing) {
        if ($existing.PSIsContainer) {
            throw "Refusing to replace directory '$LinkPath' with a file link."
        }

        $isExpectedLink = $false
        $isRepairablePlainFile = $false
        if (Test-IsLink -Item $existing) {
            try {
                $isExpectedLink = ((Get-LinkResolvedTarget -LinkPath $LinkPath) -eq $expectedResolved)
            } catch {
                $isExpectedLink = $false
            }
        } elseif (Test-HardLinkMatch -LinkPath $LinkPath -TargetPath $TargetPath) {
            $isExpectedLink = $true
        } elseif (Test-FileContentMatch -FirstPath $LinkPath -SecondPath $TargetPath) {
            $isRepairablePlainFile = $true
        }

        if ($isExpectedLink) {
            Write-Output "OK     $LinkPath -> $expectedResolved"
            return
        }

        if ($isRepairablePlainFile -and (-not $AllowReplace)) {
            throw "Existing plain file '$LinkPath' matches canonical content but is not linked. Re-run with -Force to repair the link."
        }

        if ((-not (Test-IsLink -Item $existing)) -and (-not (Test-HardLinkMatch -LinkPath $LinkPath -TargetPath $TargetPath)) -and (-not $isRepairablePlainFile)) {
            throw "Refusing to replace non-link file '$LinkPath'. Remove or rename it manually."
        }

        if (-not $AllowReplace) {
            throw "Existing file link '$LinkPath' points somewhere else. Re-run with -Force to replace the link only."
        }

        try {
            Remove-LinkPath -Path $LinkPath
        } catch {
            throw "Failed to remove existing file link '$LinkPath'. $($_.Exception.Message)"
        }
    }

    $linkParent = Split-Path -Parent $LinkPath
    Ensure-Directory -Path $linkParent

    $linkKind = "symbolic-link"
    $symlinkError = $null
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $TargetPath | Out-Null
    } catch {
        $symlinkError = $_.Exception.Message
        try {
            New-Item -ItemType HardLink -Path $LinkPath -Target $TargetPath | Out-Null
            $linkKind = "hard-link"
        } catch {
            $hardLinkError = $_.Exception.Message
            throw "Failed to create a file link at '$LinkPath'. Tried symbolic link and hard link. Enable Developer Mode or run an elevated shell for true symlinks. Symlink error: '$symlinkError'. Hard-link error: '$hardLinkError'."
        }
    }

    $verified = $false
    $newItem = Get-Item -LiteralPath $LinkPath -Force
    if (Test-IsLink -Item $newItem) {
        $verified = ((Get-LinkResolvedTarget -LinkPath $LinkPath) -eq $expectedResolved)
    } else {
        $verified = (Test-FileContentMatch -FirstPath $LinkPath -SecondPath $TargetPath)
    }

    if (-not $verified) {
        throw "File link verification failed for '$LinkPath'. Expected '$expectedResolved'."
    }

    Write-Output "LINKED [$linkKind] $LinkPath -> $expectedResolved"
}

function Ensure-ManagedTextFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Content,
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix
    )

    $existing = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        if ($existing.PSIsContainer) {
            throw "Refusing to replace directory '$Path' with a managed file."
        }

        $existingContent = Get-Content -LiteralPath $Path -Raw
        if ($existingContent -eq $Content) {
            Write-Output "OK     $Path (managed file)"
            return
        }

        if (-not (Test-IsManagedTextContent -Content $existingContent -ManagedPrefix $ManagedPrefix)) {
            throw "Refusing to replace non-managed file '$Path'. Remove or rename it manually."
        }
    }

    $parent = Split-Path -Parent $Path
    Ensure-Directory -Path $parent
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
    Write-Output "WROTE  $Path"
}

function Test-IsManagedTextContent {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Content,
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix
    )

    $normalizedContent = $Content.TrimStart([char]0xFEFF)
    if ($normalizedContent.StartsWith($ManagedPrefix)) {
        return $true
    }

    $lines = $normalizedContent -split "`r?`n"
    if ($lines.Length -lt 3 -or $lines[0].Trim() -ne "---") {
        return $false
    }

    $closingIndex = -1
    for ($i = 1; $i -lt $lines.Length; $i++) {
        if ($lines[$i].Trim() -eq "---") {
            $closingIndex = $i
            break
        }
    }

    if ($closingIndex -lt 0) {
        return $false
    }

    for ($i = $closingIndex + 1; $i -lt $lines.Length; $i++) {
        if ([string]::IsNullOrWhiteSpace($lines[$i])) {
            continue
        }

        return $lines[$i].StartsWith($ManagedPrefix)
    }

    return $false
}

function Remove-StaleManagedFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RootPath,
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$ExpectedPaths,
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix
    )

    if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) {
        return
    }

    $expected = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($path in $ExpectedPaths) {
        $null = $expected.Add([System.IO.Path]::GetFullPath($path))
    }

    foreach ($file in Get-ChildItem -LiteralPath $RootPath -File -Recurse -ErrorAction SilentlyContinue) {
        $normalized = [System.IO.Path]::GetFullPath($file.FullName)
        if ($expected.Contains($normalized)) {
            continue
        }

        $content = Get-Content -LiteralPath $file.FullName -Raw
        if (Test-IsManagedTextContent -Content $content -ManagedPrefix $ManagedPrefix) {
            Remove-Item -LiteralPath $file.FullName -Force
            Write-Output "REMOVED stale managed file $($file.FullName)"
        }
    }

    $directories = @(Get-ChildItem -LiteralPath $RootPath -Directory -Recurse -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)
    foreach ($directory in $directories) {
        $hasChildren = Get-ChildItem -LiteralPath $directory.FullName -Force -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -eq $hasChildren) {
            Remove-Item -LiteralPath $directory.FullName -Force
        }
    }

    $rootHasChildren = Get-ChildItem -LiteralPath $RootPath -Force -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $rootHasChildren) {
        Remove-Item -LiteralPath $RootPath -Force
    }
}

function Remove-StaleChildDirectoryLinks {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetRoot,
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$ExpectedLinkPaths,
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [switch]$AllowBrokenLinkRemoval
    )

    if (-not (Test-Path -LiteralPath $TargetRoot -PathType Container)) {
        return
    }

    $expected = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($path in $ExpectedLinkPaths) {
        $null = $expected.Add([System.IO.Path]::GetFullPath($path))
    }

    $normalizedSourceRoot = Get-NormalizedPath -Path $SourceRoot
    $sourcePrefix = $normalizedSourceRoot + "\"

    foreach ($child in Get-ChildItem -LiteralPath $TargetRoot -Directory -Force -ErrorAction SilentlyContinue) {
        if (-not (Test-IsLink -Item $child)) {
            continue
        }

        $normalizedChildPath = [System.IO.Path]::GetFullPath($child.FullName)
        if ($expected.Contains($normalizedChildPath)) {
            continue
        }

        try {
            $resolvedTarget = Get-LinkResolvedTarget -LinkPath $child.FullName
        } catch {
            if ($AllowBrokenLinkRemoval) {
                Remove-LinkPath -Path $child.FullName

                Write-Output "REMOVED stale broken directory link $($child.FullName)"
            }
            continue
        }

        $isCanonicalTarget =
            $resolvedTarget.Equals($normalizedSourceRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
            $resolvedTarget.StartsWith($sourcePrefix, [System.StringComparison]::OrdinalIgnoreCase)
        if (-not $isCanonicalTarget) {
            continue
        }

        Remove-LinkPath -Path $child.FullName

        Write-Output "REMOVED stale directory link $($child.FullName)"
    }

    $rootHasChildren = Get-ChildItem -LiteralPath $TargetRoot -Force -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $rootHasChildren) {
        Remove-Item -LiteralPath $TargetRoot -Force
    }
}

function Remove-StaleDirectoryLink {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot,
        [switch]$AllowBrokenLinkRemoval
    )

    if (-not (Test-Path -LiteralPath $LinkPath)) {
        return
    }

    $existing = Get-Item -LiteralPath $LinkPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $existing -or -not (Test-IsLink -Item $existing)) {
        return
    }

    $normalizedSourceRoot = Get-NormalizedPath -Path $SourceRoot

    try {
        $resolvedTarget = Get-LinkResolvedTarget -LinkPath $LinkPath
    } catch {
        if (-not $AllowBrokenLinkRemoval) {
            return
        }

        Remove-LinkPath -Path $LinkPath

        Write-Output "REMOVED stale broken directory link $LinkPath"
        return
    }

    if (-not $resolvedTarget.Equals($normalizedSourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return
    }

    Remove-LinkPath -Path $LinkPath

    Write-Output "REMOVED stale directory link $LinkPath"
}

function Test-DirectoryHasFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [string]$Filter = "*"
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return $false
    }

    return [bool](Get-ChildItem -LiteralPath $Path -Filter $Filter -File -ErrorAction SilentlyContinue | Select-Object -First 1)
}

function Test-ValidMcpConfig {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    try {
        $json = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        throw "Invalid MCP JSON at '$Path': $($_.Exception.Message)"
    }

    if ($null -eq $json.mcpServers) {
        throw "MCP config '$Path' is missing 'mcpServers'."
    }
}

function Test-ValidJsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    try {
        $null = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        throw "Invalid JSON at '$Path': $($_.Exception.Message)"
    }
}

function Test-ValidTomlFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if ($null -eq $pythonCmd) {
        throw "Python (python or python3) is required to validate TOML settings at '$Path'."
    }

    $validationScript = "import pathlib, sys, tomllib; tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))"
    $validationOutput = & $pythonCmd.Source -c $validationScript $Path 2>&1
    if ($LASTEXITCODE -ne 0) {
        $detail = @($validationOutput | ForEach-Object { $_.ToString().Trim() } | Where-Object { $_ }) -join " "
        if ([string]::IsNullOrWhiteSpace($detail)) {
            $detail = "python exited with code $LASTEXITCODE."
        }
        throw "Invalid TOML at '$Path': $detail"
    }
}

function Should-Include {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    return $normalizedInclude -contains $Name.ToLowerInvariant()
}

function Resolve-GovernancePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathSpec
    )

    $expanded = $PathSpec.Replace("{HOME}", $HOME)
    if ([System.IO.Path]::IsPathRooted($expanded)) {
        return $expanded
    }

    return Join-Path $governanceRoot $expanded
}

function Resolve-TargetPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathSpec
    )

    $expanded = $PathSpec.Replace("{HOME}", $HOME)
    if ([System.IO.Path]::IsPathRooted($expanded)) {
        return $expanded
    }

    return Join-Path $resolvedRepoRoot $expanded
}

function Get-RepoRelativeReferenceRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,
        [Parameter(Mandatory = $true)]
        [string]$GovernanceRoot
    )

    $normalizedRepoRoot = Get-NormalizedPath -Path $RepoRoot
    $normalizedGovernanceRoot = Get-NormalizedPath -Path $GovernanceRoot

    if ($normalizedGovernanceRoot.Equals($normalizedRepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return ""
    }

    $repoPrefix = $normalizedRepoRoot + "\"
    if (-not $normalizedGovernanceRoot.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Repo root '$normalizedRepoRoot' must contain the governance root '$normalizedGovernanceRoot' so generated adapters only point at canonical in-repo governance files."
    }

    $baseUri = New-Object System.Uri(($normalizedRepoRoot.TrimEnd("\") + "\"))
    $targetUri = New-Object System.Uri(($normalizedGovernanceRoot.TrimEnd("\") + "\"))
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).TrimEnd("/")
}

function Join-MarkdownReferencePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,
        [string]$BasePath = ""
    )

    $normalizedRelative = $RelativePath.Replace("\", "/").TrimStart("/")
    if ([string]::IsNullOrWhiteSpace($BasePath)) {
        return $normalizedRelative
    }

    return ($BasePath.Trim("/").Replace("\", "/") + "/" + $normalizedRelative)
}

function Read-ProjectionManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManifestPath
    )

    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Missing runtime projection manifest: $ManifestPath"
    }

    try {
        return (Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json)
    } catch {
        throw "Failed to parse runtime projection manifest '$ManifestPath': $($_.Exception.Message)"
    }
}

function Get-ProjectionEntries {
    param(
        [Parameter(Mandatory = $true)]
        $Manifest,
        [Parameter(Mandatory = $true)]
        [string]$AssetClass
    )

    $allEntries = @($Manifest.asset_classes.$AssetClass)
    $selected = @()
    foreach ($entry in $allEntries) {
        $supportLevel = [string]$entry.support_level
        $reason = ""
        if ($entry.PSObject.Properties.Name -contains "reason") {
            $reason = [string]$entry.reason
        }

        switch ($supportLevel) {
            "official" {
                $selected += $entry
            }
            "compatibility" {
                if ($IncludeCompatibility) {
                    $selected += $entry
                } else {
                    Write-Host "SKIPPED $AssetClass $($entry.platform) [compatibility] '$($entry.id)' is disabled by default. Re-run with -IncludeCompatibility."
                }
            }
            default {
                if ([string]::IsNullOrWhiteSpace($reason)) {
                    $reason = "No runtime projection is configured."
                }
                Write-Host "SKIPPED $AssetClass $($entry.platform) [$supportLevel] $reason"
            }
        }
    }

    return $selected
}

function Test-EntryBooleanFlag {
    param(
        [Parameter(Mandatory = $true)]
        $Entry,
        [Parameter(Mandatory = $true)]
        [string]$PropertyName
    )

    if (-not ($Entry.PSObject.Properties.Name -contains $PropertyName)) {
        return $false
    }

    $rawValue = $Entry.$PropertyName
    if ($null -eq $rawValue) {
        return $false
    }

    try {
        return [bool]$rawValue
    } catch {
        return $false
    }
}

function Preserve-DisabledProjectionIfRequested {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AssetClass,
        [Parameter(Mandatory = $true)]
        $Entry
    )

    if (-not (Test-EntryBooleanFlag -Entry $Entry -PropertyName "preserve_existing_when_disabled")) {
        return $false
    }

    $targetSpec = $null
    if ($Entry.PSObject.Properties.Name -contains "target_root") {
        $targetSpec = [string]$Entry.target_root
    } elseif ($Entry.PSObject.Properties.Name -contains "target_path") {
        $targetSpec = [string]$Entry.target_path
    }

    if ([string]::IsNullOrWhiteSpace($targetSpec)) {
        return $false
    }

    $targetPath = Resolve-TargetPath -PathSpec $targetSpec
    $existing = Get-Item -LiteralPath $targetPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $existing) {
        return $false
    }

    $preserveDetail = "retained existing '$targetPath' while disabled by default."
    if (Test-IsLink -Item $existing) {
        try {
            $null = Get-LinkResolvedTarget -LinkPath $targetPath
        } catch {
            $preserveDetail = "retained existing broken link '$targetPath' while disabled by default; rerun with -IncludeCompatibility after repairing the target if you want to relink it."
        }
    }

    Write-Host "PRESERVED $AssetClass $($entry.platform) [compatibility] '$($entry.id)' $preserveDetail"
    return $true
}

function Get-SkillDirectories {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
        Write-Host "SKIPPED skills no canonical skill root was found under '$SourceRoot'."
        return @()
    }

    $allSkillDirs = @(Get-ChildItem -LiteralPath $SourceRoot -Directory -ErrorAction SilentlyContinue | Sort-Object Name)
    foreach ($skillDir in $allSkillDirs) {
        if (-not (Test-Path -LiteralPath (Join-Path $skillDir.FullName "SKILL.md") -PathType Leaf)) {
            Write-Host "SKIPPED skills $($skillDir.Name) no SKILL.md was found under '$($skillDir.FullName)'."
        }
    }

    return @(
        $allSkillDirs |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf }
    )
}

function Resolve-PreferredSourcePath {
    param(
        [Parameter(Mandatory = $true)]
        $Entry
    )

    foreach ($candidate in @($Entry.source_preference)) {
        $resolved = Resolve-GovernancePath -PathSpec ([string]$candidate)
        if (Test-Path -LiteralPath $resolved -PathType Leaf) {
            return $resolved
        }
    }

    return $null
}

function New-CursorGovernanceRuleContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix,
        [string]$GovernanceReferenceRoot = ""
    )

    $agentsPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "AGENTS.md"
    $platformIndexPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/platforms/index.md"
    $skillsRootPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills"
    $tick = [char]96
    $agentsCode = "$tick$agentsPath$tick"
    $platformIndexCode = "$tick$platformIndexPath$tick"
    $skillsRootCode = "$tick$skillsRootPath/$tick"

    return @"
---
description: Repo governance entrypoint for Cursor.
globs: []
alwaysApply: true
---
$ManagedPrefix source: $agentsPath -->
Use $agentsCode as the canonical governance source for this repo.
Use $platformIndexCode for current official runtime mappings and setup expectations.
Treat generated `skill-*` rules as adapters only. The canonical skill bundles remain under $skillsRootCode.
"@
}

function New-CursorSkillRuleContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix,
        [Parameter(Mandatory = $true)]
        [string]$SkillName,
        [string]$GovernanceReferenceRoot = ""
    )

    $skillDocPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills/$SkillName/SKILL.md"
    $skillBundlePath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills/$SkillName"
    $tick = [char]96
    $skillDocCode = "$tick$skillDocPath$tick"
    $skillBundleCode = "$tick$skillBundlePath/$tick"

    return @"
---
description: Adapter rule for the repo-owned skill '$SkillName'.
globs: []
alwaysApply: false
---
$ManagedPrefix source: $skillDocPath -->
When the '$SkillName' skill is relevant, load and follow $skillDocCode.
Use supporting files from $skillBundleCode when the bundle references them.
Do not treat this Cursor rule as the authority. The SSOT remains the canonical skill bundle.
"@
}

function Sync-CursorSkillRules {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetRoot,
        [Parameter(Mandatory = $true)]
        [object[]]$SkillDirs,
        [string]$GovernanceReferenceRoot = ""
    )

    $managedPrefix = "<!-- Managed by docs/agents/link_repo_assets.ps1;"
    $expectedPaths = New-Object System.Collections.Generic.List[string]

    $governanceRulePath = Join-Path $TargetRoot "project-governance.mdc"
    Ensure-ManagedTextFile -Path $governanceRulePath -Content (New-CursorGovernanceRuleContent -ManagedPrefix $managedPrefix -GovernanceReferenceRoot $GovernanceReferenceRoot) -ManagedPrefix $managedPrefix
    $expectedPaths.Add([System.IO.Path]::GetFullPath($governanceRulePath))

    foreach ($skillDir in $SkillDirs) {
        $rulePath = Join-Path $TargetRoot ("skill-" + $skillDir.Name + ".mdc")
        Ensure-ManagedTextFile -Path $rulePath -Content (New-CursorSkillRuleContent -ManagedPrefix $managedPrefix -SkillName $skillDir.Name -GovernanceReferenceRoot $GovernanceReferenceRoot) -ManagedPrefix $managedPrefix
        $expectedPaths.Add([System.IO.Path]::GetFullPath($rulePath))
    }

    Remove-StaleManagedFiles -RootPath $TargetRoot -ExpectedPaths $expectedPaths.ToArray() -ManagedPrefix $managedPrefix
}

function New-ClaudeGovernanceCommandContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix,
        [string]$GovernanceReferenceRoot = ""
    )

    $agentsPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "AGENTS.md"
    $platformIndexPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/platforms/index.md"
    $skillsRootPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills"
    $tick = [char]96
    $agentsCode = "$tick$agentsPath$tick"
    $platformIndexCode = "$tick$platformIndexPath$tick"
    $skillsRootCode = "$tick$skillsRootPath/$tick"

    return @"
$ManagedPrefix source: $agentsPath -->
Use $agentsCode as the canonical governance source for this repo.
Use $platformIndexCode for official runtime mappings and bootstrap rules.
Treat generated `skill-*` commands as adapters only. The canonical skill bundles remain under $skillsRootCode.
"@
}

function New-ClaudeSkillCommandContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix,
        [Parameter(Mandatory = $true)]
        [string]$SkillName,
        [string]$GovernanceReferenceRoot = ""
    )

    $skillDocPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills/$SkillName/SKILL.md"
    $skillBundlePath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/skills/$SkillName"
    $tick = [char]96
    $skillDocCode = "$tick$skillDocPath$tick"
    $skillBundleCode = "$tick$skillBundlePath/$tick"

    return @"
$ManagedPrefix source: $skillDocPath -->
Load and follow $skillDocCode.
Use supporting files from $skillBundleCode when the bundle references them.
This command is a Claude adapter only; the SSOT remains the canonical repo-owned skill bundle.
"@
}

function Convert-ToClaudeAgentContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManagedPrefix,
        [Parameter(Mandatory = $true)]
        [string]$SourcePath,
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    $raw = Get-Content -LiteralPath $SourcePath -Raw
    $lines = $raw -split "`r?`n"
    if ($lines.Length -lt 3 -or $lines[0].Trim() -ne "---") {
        throw "Expected frontmatter in subagent source '$SourcePath'."
    }

    $closingIndex = -1
    for ($i = 1; $i -lt $lines.Length; $i++) {
        if ($lines[$i].Trim() -eq "---") {
            $closingIndex = $i
            break
        }
    }

    if ($closingIndex -lt 0) {
        throw "Unterminated frontmatter in subagent source '$SourcePath'."
    }

    $frontmatter = @(
        $lines[1..($closingIndex - 1)] |
        Where-Object { $_ -notmatch '^\s*model:\s*' }
    )

    $body = @()
    if ($closingIndex + 1 -lt $lines.Length) {
        $body = $lines[($closingIndex + 1)..($lines.Length - 1)]
    }

    $relativeSource = [System.IO.Path]::GetRelativePath($SourceRoot, $SourcePath).Replace("\", "/")
    $contentLines = @("---")
    $contentLines += $frontmatter
    $contentLines += "---"
    $contentLines += "$ManagedPrefix source: $relativeSource -->"
    $contentLines += ""
    $contentLines += $body
    return ($contentLines -join "`r`n")
}

function Sync-ClaudeSkillCommands {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetRoot,
        [Parameter(Mandatory = $true)]
        [object[]]$SkillDirs,
        [string]$GovernanceReferenceRoot = ""
    )

    $managedPrefix = "<!-- Managed by docs/agents/link_repo_assets.ps1;"
    $expectedPaths = New-Object System.Collections.Generic.List[string]

    $governanceCommandPath = Join-Path $TargetRoot "project-governance.md"
    Ensure-ManagedTextFile -Path $governanceCommandPath -Content (New-ClaudeGovernanceCommandContent -ManagedPrefix $managedPrefix -GovernanceReferenceRoot $GovernanceReferenceRoot) -ManagedPrefix $managedPrefix
    $expectedPaths.Add([System.IO.Path]::GetFullPath($governanceCommandPath))

    foreach ($skillDir in $SkillDirs) {
        $commandPath = Join-Path $TargetRoot ("skill-" + $skillDir.Name + ".md")
        Ensure-ManagedTextFile -Path $commandPath -Content (New-ClaudeSkillCommandContent -ManagedPrefix $managedPrefix -SkillName $skillDir.Name -GovernanceReferenceRoot $GovernanceReferenceRoot) -ManagedPrefix $managedPrefix
        $expectedPaths.Add([System.IO.Path]::GetFullPath($commandPath))
    }

    Remove-StaleManagedFiles -RootPath $TargetRoot -ExpectedPaths $expectedPaths.ToArray() -ManagedPrefix $managedPrefix
}

function Sync-ClaudeAgentsFromSubagents {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetRoot,
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    $managedPrefix = "<!-- Managed by docs/agents/link_repo_assets.ps1;"
    $expectedPaths = New-Object System.Collections.Generic.List[string]
    $sourceFiles = @(Get-ChildItem -LiteralPath $SourceRoot -File -Filter "*.md" | Sort-Object Name)

    foreach ($sourceFile in $sourceFiles) {
        $targetPath = Join-Path $TargetRoot $sourceFile.Name
        $content = Convert-ToClaudeAgentContent -ManagedPrefix $managedPrefix -SourcePath $sourceFile.FullName -SourceRoot $SourceRoot
        Ensure-ManagedTextFile -Path $targetPath -Content $content -ManagedPrefix $managedPrefix
        $expectedPaths.Add([System.IO.Path]::GetFullPath($targetPath))
    }

    Remove-StaleManagedFiles -RootPath $TargetRoot -ExpectedPaths $expectedPaths.ToArray() -ManagedPrefix $managedPrefix
}

$allowedIncludes = @("skills", "subagents", "mcp", "settings", "acp")
$normalizedInclude = @($Include | ForEach-Object { $_.ToLowerInvariant() } | Select-Object -Unique)
$invalidIncludes = @($normalizedInclude | Where-Object { $allowedIncludes -notcontains $_ })
if ($invalidIncludes) {
    throw "Unsupported -Include value(s): $($invalidIncludes -join ', '). Allowed values: $($allowedIncludes -join ', ')."
}

$governanceRoot = Get-NormalizedPath -Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$requiredGovernanceFiles = @("AGENTS.md", "agents-manifest.yaml")
$missingGovernanceFiles = @(
    $requiredGovernanceFiles |
    Where-Object { -not (Test-Path -LiteralPath (Join-Path $governanceRoot $_) -PathType Leaf) }
)
if ($missingGovernanceFiles) {
    throw "Computed governance root '$governanceRoot' from script root '$PSScriptRoot' is invalid. Missing required file(s): $($missingGovernanceFiles -join ', ')."
}

if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    $resolvedRepoRoot = Get-NormalizedPath -Path $RepoRoot
} elseif ((Split-Path -Leaf $governanceRoot) -eq ".governance") {
    $resolvedRepoRoot = Split-Path -Parent $governanceRoot
} else {
    $resolvedRepoRoot = $governanceRoot
}
$governanceReferenceRoot = Get-RepoRelativeReferenceRoot -RepoRoot $resolvedRepoRoot -GovernanceRoot $governanceRoot

$manifestPath = Join-Path $governanceRoot "docs/agents/platforms/runtime-projections.json"
$manifest = Read-ProjectionManifest -ManifestPath $manifestPath

if (Should-Include -Name "skills") {
    $allSkillEntries = @($manifest.asset_classes.skills)
    $skillEntries = Get-ProjectionEntries -Manifest $manifest -AssetClass "skills"
    if (-not $skillEntries) {
        Write-Output "SKIPPED skills no enabled runtime projections are configured."
    } else {
        $skillSourceRoot = Resolve-GovernancePath -PathSpec ([string]$skillEntries[0].source_root)
        $skillDirs = Get-SkillDirectories -SourceRoot $skillSourceRoot

        if (-not $skillDirs) {
            Write-Output "SKIPPED skills no canonical skill directories were found under '$skillSourceRoot'."
        } else {
            foreach ($entry in $skillEntries) {
                $projectionMode = [string]$entry.projection_mode
                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                switch ($projectionMode) {
                    "child_directory_links" {
                        Ensure-Directory -Path $targetRoot
                        $expectedLinkPaths = New-Object System.Collections.Generic.List[string]
                        foreach ($skillDir in $skillDirs) {
                            $linkPath = Join-Path $targetRoot $skillDir.Name
                            $useRelative = ([string]$entry.scope -eq "project")
                            Ensure-DirectoryLink -LinkPath $linkPath -TargetPath $skillDir.FullName -UseRelativeTarget:$useRelative -AllowReplace:$Force
                            $expectedLinkPaths.Add([System.IO.Path]::GetFullPath($linkPath))
                        }
                        $allowBrokenLinkRemoval = ([string]$entry.scope -eq "project")
                        Remove-StaleChildDirectoryLinks -TargetRoot $targetRoot -ExpectedLinkPaths $expectedLinkPaths.ToArray() -SourceRoot $skillSourceRoot -AllowBrokenLinkRemoval:$allowBrokenLinkRemoval
                    }
                    "generated_cursor_rules_from_skills" {
                        Sync-CursorSkillRules -TargetRoot $targetRoot -SkillDirs $skillDirs -GovernanceReferenceRoot $governanceReferenceRoot
                    }
                    "generated_claude_commands_from_skills" {
                        Sync-ClaudeSkillCommands -TargetRoot $targetRoot -SkillDirs $skillDirs -GovernanceReferenceRoot $governanceReferenceRoot
                    }
                    default {
                        throw "Unsupported skills projection_mode '$projectionMode' for entry '$($entry.id)'."
                    }
                }
            }
        }
    }

    $managedPrefix = "<!-- Managed by docs/agents/link_repo_assets.ps1;"
    $selectedSkillEntryIds = @($skillEntries | ForEach-Object { [string]$_.id })
    foreach ($entry in $allSkillEntries) {
        $projectionMode = [string]$entry.projection_mode
        if ($selectedSkillEntryIds -contains [string]$entry.id) {
            continue
        }

        if (Preserve-DisabledProjectionIfRequested -AssetClass "skills" -Entry $entry) {
            continue
        }

        switch ($projectionMode) {
            "generated_cursor_rules_from_skills" {
                if (-not ($entry.PSObject.Properties.Name -contains "target_root")) {
                    continue
                }

                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                Remove-StaleManagedFiles -RootPath $targetRoot -ExpectedPaths @() -ManagedPrefix $managedPrefix
            }
            "generated_claude_commands_from_skills" {
                if (-not ($entry.PSObject.Properties.Name -contains "target_root")) {
                    continue
                }

                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                Remove-StaleManagedFiles -RootPath $targetRoot -ExpectedPaths @() -ManagedPrefix $managedPrefix
            }
            "child_directory_links" {
                if ((-not ($entry.PSObject.Properties.Name -contains "source_root")) -or (-not ($entry.PSObject.Properties.Name -contains "target_root"))) {
                    continue
                }

                $sourceRoot = Resolve-GovernancePath -PathSpec ([string]$entry.source_root)
                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                $allowBrokenLinkRemoval = ([string]$entry.scope -eq "project")
                Remove-StaleChildDirectoryLinks -TargetRoot $targetRoot -ExpectedLinkPaths @() -SourceRoot $sourceRoot -AllowBrokenLinkRemoval:$allowBrokenLinkRemoval
            }
        }
    }
}

if (Should-Include -Name "subagents") {
    $allSubagentEntries = @($manifest.asset_classes.subagents)
    $subagentEntries = Get-ProjectionEntries -Manifest $manifest -AssetClass "subagents"
    foreach ($entry in $subagentEntries) {
        $sourceRoot = Resolve-GovernancePath -PathSpec ([string]$entry.source_root)

        $sourceFileFilter = "*.md"
        if ($entry.PSObject.Properties.Name -contains "source_file_glob") {
            $candidateSourceFileFilter = [string]$entry.source_file_glob
            if (-not [string]::IsNullOrWhiteSpace($candidateSourceFileFilter)) {
                $sourceFileFilter = $candidateSourceFileFilter
            }
        }

        if (-not (Test-DirectoryHasFiles -Path $sourceRoot -Filter $sourceFileFilter)) {
            Write-Output "SKIPPED subagents $($entry.platform) no canonical subagent files matching '$sourceFileFilter' were found under '$sourceRoot'."
            continue
        }

        $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
        switch ([string]$entry.projection_mode) {
            "directory_link" {
                $useRelative = ([string]$entry.scope -eq "project")
                $preserveExistingNonLink = Test-EntryBooleanFlag -Entry $entry -PropertyName "preserve_existing_when_disabled"
                Ensure-DirectoryLink -LinkPath $targetRoot -TargetPath $sourceRoot -UseRelativeTarget:$useRelative -AllowReplace:$Force -PreserveExistingNonLink:$preserveExistingNonLink
            }
            "generated_claude_agents_from_subagents" {
                Sync-ClaudeAgentsFromSubagents -TargetRoot $targetRoot -SourceRoot $sourceRoot
            }
            default {
                throw "Unsupported subagents projection_mode '$([string]$entry.projection_mode)' for entry '$($entry.id)'."
            }
        }
    }

    $managedPrefix = "<!-- Managed by docs/agents/link_repo_assets.ps1;"
    $selectedSubagentEntryIds = @($subagentEntries | ForEach-Object { [string]$_.id })
    foreach ($entry in $allSubagentEntries) {
        if ($selectedSubagentEntryIds -contains [string]$entry.id) {
            continue
        }

        if (Preserve-DisabledProjectionIfRequested -AssetClass "subagents" -Entry $entry) {
            continue
        }

        switch ([string]$entry.projection_mode) {
            "directory_link" {
                if ((-not ($entry.PSObject.Properties.Name -contains "source_root")) -or (-not ($entry.PSObject.Properties.Name -contains "target_root"))) {
                    continue
                }

                $sourceRoot = Resolve-GovernancePath -PathSpec ([string]$entry.source_root)
                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                $allowBrokenLinkRemoval = ([string]$entry.scope -eq "project")
                Remove-StaleDirectoryLink -LinkPath $targetRoot -SourceRoot $sourceRoot -AllowBrokenLinkRemoval:$allowBrokenLinkRemoval
            }
            "generated_claude_agents_from_subagents" {
                if (-not ($entry.PSObject.Properties.Name -contains "target_root")) {
                    continue
                }

                $targetRoot = Resolve-TargetPath -PathSpec ([string]$entry.target_root)
                Remove-StaleManagedFiles -RootPath $targetRoot -ExpectedPaths @() -ManagedPrefix $managedPrefix
            }
        }
    }
}

if (Should-Include -Name "mcp") {
    $mcpEntries = Get-ProjectionEntries -Manifest $manifest -AssetClass "mcp"
    foreach ($entry in $mcpEntries) {
        $sourcePath = Resolve-PreferredSourcePath -Entry $entry
        if ($null -eq $sourcePath) {
            Write-Output "SKIPPED mcp $($entry.platform) no canonical MCP config was found for '$($entry.id)'."
            continue
        }

        if ([string]$entry.projection_mode -ne "mcp_file_link") {
            throw "Unsupported mcp projection_mode '$([string]$entry.projection_mode)' for entry '$($entry.id)'."
        }

        Test-ValidMcpConfig -Path $sourcePath
        $targetPath = Resolve-TargetPath -PathSpec ([string]$entry.target_path)
        Ensure-FileLink -LinkPath $targetPath -TargetPath $sourcePath -AllowReplace:$Force
    }
}

if (Should-Include -Name "settings") {
    $settingsEntries = Get-ProjectionEntries -Manifest $manifest -AssetClass "settings"
    foreach ($entry in $settingsEntries) {
        if ([string]$entry.projection_mode -ne "settings_file_link") {
            throw "Unsupported settings projection_mode '$([string]$entry.projection_mode)' for entry '$($entry.id)'."
        }

        $sourcePath = Resolve-GovernancePath -PathSpec ([string]$entry.source_path)
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "Missing canonical settings source '$sourcePath' for entry '$($entry.id)'."
        }

        $extension = [System.IO.Path]::GetExtension($sourcePath).ToLowerInvariant()
        switch ($extension) {
            ".json" {
                Test-ValidJsonFile -Path $sourcePath
            }
            ".toml" {
                Test-ValidTomlFile -Path $sourcePath
            }
            default {
                throw "Unsupported settings file extension '$extension' for entry '$($entry.id)'."
            }
        }

        $targetPath = Resolve-TargetPath -PathSpec ([string]$entry.target_path)
        Ensure-FileLink -LinkPath $targetPath -TargetPath $sourcePath -AllowReplace:$Force
    }
}

if (Should-Include -Name "acp") {
    $null = Get-ProjectionEntries -Manifest $manifest -AssetClass "acp"
}

Write-Output "NOTE   Re-run scripts/setup_repo_platform_assets.ps1 after moving the repo so runtime projections can be rebuilt."
