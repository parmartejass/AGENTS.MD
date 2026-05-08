[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$IncludeCompatibility,
    [string]$RepoRoot,
    [string[]]$Include = @("skills", "mcp", "settings", "acp"),
    [switch]$RepairPlainDirectoryStubs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$IsWindowsRuntime = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)

function Remove-TrailingDirectorySeparators {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $pathRoot = [System.IO.Path]::GetPathRoot($fullPath)
    if ($fullPath.Length -le $pathRoot.Length) {
        return $fullPath
    }

    return $fullPath.TrimEnd([char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
}

function Get-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [switch]$AllowMissing
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if ((-not $AllowMissing) -or (Test-Path -LiteralPath $fullPath)) {
        return Remove-TrailingDirectorySeparators -Path ((Resolve-Path -LiteralPath $fullPath).ProviderPath)
    }

    return Remove-TrailingDirectorySeparators -Path $fullPath
}

function Get-NormalizedChildPathPrefix {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $normalizedPath = Get-NormalizedPath -Path $Path
    $pathRoot = [System.IO.Path]::GetPathRoot($normalizedPath)
    if ($normalizedPath.Length -le $pathRoot.Length) {
        return $normalizedPath
    }

    return $normalizedPath + [System.IO.Path]::DirectorySeparatorChar
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

function Test-IsHardLink {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileSystemInfo]$Item,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    if ($Item.PSIsContainer) {
        return $false
    }

    if (-not ($Item.PSObject.Properties.Name -contains "LinkType")) {
        return $false
    }

    $linkType = [string]$Item.LinkType
    if (-not $linkType.Equals("HardLink", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $false
    }

    $expectedResolved = Get-NormalizedPath -Path $TargetPath
    foreach ($candidate in @($Item.Target)) {
        if ([string]::IsNullOrWhiteSpace([string]$candidate)) {
            continue
        }
        try {
            $normalizedCandidate = Get-NormalizedPath -Path ([string]$candidate) -AllowMissing
        } catch {
            continue
        }
        if ($normalizedCandidate -eq $expectedResolved) {
            return $true
        }
    }

    return $false
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

    return Get-NormalizedPath -Path $targetValue -AllowMissing
}

function Get-RelativeLinkTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseDirectory,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    $normalizedBase = Get-NormalizedPath -Path $BaseDirectory
    $normalizedTarget = Get-NormalizedPath -Path $TargetPath
    if ([System.IO.Path].GetMethod("GetRelativePath", [type[]]@([string], [string]))) {
        return [System.IO.Path]::GetRelativePath($normalizedBase, $normalizedTarget)
    }

    $baseWithSeparator = $normalizedBase
    if (-not $baseWithSeparator.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $baseWithSeparator += [System.IO.Path]::DirectorySeparatorChar
    }
    $baseUri = [System.Uri]::new($baseWithSeparator)
    $targetUri = [System.Uri]::new($normalizedTarget)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri).ToString()
    return [System.Uri]::UnescapeDataString($relativeUri).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

function Resolve-PlainTextLinkStubTarget {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath
    )

    try {
        $stubText = (Get-Content -Raw -LiteralPath $LinkPath -ErrorAction Stop).Trim().TrimStart([char]0xFEFF)
    } catch {
        return $null
    }

    if ([string]::IsNullOrWhiteSpace($stubText) -or $stubText -match "[`r`n]") {
        return $null
    }

    $isRooted = $false
    try {
        $isRooted = [System.IO.Path]::IsPathRooted($stubText)
    } catch {
        return $null
    }

    if (-not $isRooted) {
        try {
            $stubText = Join-Path (Split-Path -Parent $LinkPath) $stubText
        } catch {
            return $null
        }
    }

    try {
        return Get-NormalizedPath -Path $stubText -AllowMissing
    } catch {
        return $null
    }
}

function Test-PlainTextDirectoryLinkStub {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileSystemInfo]$Item,
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    if ($Item.PSIsContainer) {
        return $false
    }

    $resolvedStubTarget = Resolve-PlainTextLinkStubTarget -LinkPath $LinkPath
    if ($null -eq $resolvedStubTarget) {
        return $false
    }

    return ($resolvedStubTarget -eq (Get-NormalizedPath -Path $TargetPath))
}

function Test-PlainTextFileLinkStub {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileSystemInfo]$Item,
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    if ($Item.PSIsContainer) {
        return $false
    }

    $resolvedStubTarget = Resolve-PlainTextLinkStubTarget -LinkPath $LinkPath
    if ($null -eq $resolvedStubTarget) {
        return $false
    }

    return ($resolvedStubTarget -eq (Get-NormalizedPath -Path $TargetPath))
}

function Remove-LinkPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer -and (Test-IsLink -Item $item)) {
        [System.IO.Directory]::Delete($Path, $false)
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
        [switch]$PreserveExistingNonLink,
        [switch]$RepairPlainStubs
    )

    $expectedResolved = Get-NormalizedPath -Path $TargetPath
    $existing = Get-Item -LiteralPath $LinkPath -Force -ErrorAction SilentlyContinue

    if ($null -ne $existing) {
        $linkResolutionFailed = $false
        if (-not (Test-IsLink -Item $existing)) {
            if ($PreserveExistingNonLink -and $existing.PSIsContainer) {
                Write-Host "PRESERVED directory-link target '$LinkPath' as an existing non-link directory. The canonical source remains '$expectedResolved'."
                return
            }
            if (Test-PlainTextDirectoryLinkStub -Item $existing -LinkPath $LinkPath -TargetPath $TargetPath) {
                if ((-not $AllowReplace) -or (-not $RepairPlainStubs)) {
                    throw "Existing plain-file link stub '$LinkPath' points to canonical source but is not a directory link. Re-run with -Force -RepairPlainDirectoryStubs to convert it, or remove/rename it manually."
                }
                Remove-LinkPath -Path $LinkPath
                $existing = $null
            } else {
                throw "Refusing to replace non-link path '$LinkPath'. Remove or rename it manually."
            }
        }

        if ($null -eq $existing) {
            $linkResolutionFailed = $false
        } elseif (-not (Test-IsLink -Item $existing)) {
            throw "Refusing to replace non-link path '$LinkPath'. Remove or rename it manually."
        }

        if ($null -ne $existing) {
            $actualResolved = $null
            try {
                $actualResolved = Get-LinkResolvedTarget -LinkPath $LinkPath
            } catch {
                $actualResolved = $null
                $linkResolutionFailed = $true
            }

            if ($actualResolved -eq $expectedResolved) {
                Write-Output "OK     $LinkPath -> $expectedResolved"
                return
            }

            if (-not $AllowReplace) {
                if ($linkResolutionFailed) {
                    throw "Existing link '$LinkPath' is broken or unresolvable. Re-run with -Force to replace the link only."
                }
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
        if ($IsWindowsRuntime) {
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
        $linkResolutionFailed = $false
        if (Test-IsLink -Item $existing) {
            try {
                $isExpectedLink = ((Get-LinkResolvedTarget -LinkPath $LinkPath) -eq $expectedResolved)
            } catch {
                $isExpectedLink = $false
                $linkResolutionFailed = $true
            }
        } elseif (Test-IsHardLink -Item $existing -TargetPath $TargetPath) {
            $isExpectedLink = $true
        } elseif (Test-PlainTextFileLinkStub -Item $existing -LinkPath $LinkPath -TargetPath $TargetPath) {
            $isRepairablePlainFile = $true
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

        if ((-not (Test-IsLink -Item $existing)) -and (-not $isRepairablePlainFile)) {
            throw "Refusing to replace non-link file '$LinkPath'. Remove or rename it manually."
        }

        if (-not $AllowReplace) {
            if ($linkResolutionFailed) {
                throw "Existing file link '$LinkPath' is broken or unresolvable. Re-run with -Force to replace the link only."
            }
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
    } elseif (Test-IsHardLink -Item $newItem -TargetPath $TargetPath) {
        $verified = $true
    } else {
        $verified = $false
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

    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
        Write-Output "SKIPPED stale child directory link cleanup under '$TargetRoot' because canonical source '$SourceRoot' is missing."
        return
    }

    $normalizedSourceRoot = Get-NormalizedPath -Path $SourceRoot
    $sourcePrefix = Get-NormalizedChildPathPrefix -Path $normalizedSourceRoot

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
            } else {
                Write-Output "SKIPPED broken directory link $($child.FullName) because broken-link removal is disabled."
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
    if ($null -eq $existing) {
        return
    }

    if (-not (Test-IsLink -Item $existing)) {
        Write-Output "PRESERVED non-link path $LinkPath during stale-link cleanup."
        return
    }

    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
        Write-Output "SKIPPED stale directory link cleanup for '$LinkPath' because canonical source '$SourceRoot' is missing."
        return
    }

    $normalizedSourceRoot = Get-NormalizedPath -Path $SourceRoot

    try {
        $resolvedTarget = Get-LinkResolvedTarget -LinkPath $LinkPath
    } catch {
        if (-not $AllowBrokenLinkRemoval) {
            Write-Output "SKIPPED broken directory link $LinkPath because broken-link removal is disabled."
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

    try {
        return [bool](Get-ChildItem -LiteralPath $Path -Filter $Filter -File -ErrorAction Stop | Select-Object -First 1)
    } catch {
        throw "Failed to enumerate files under '$Path' with filter '$Filter': $($_.Exception.Message)"
    }
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
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $pythonCmd.Source
    $escapedScript = $validationScript.Replace('"', '\"')
    $escapedPath = $Path.Replace('"', '\"')
    $startInfo.Arguments = "-c `"$escapedScript`" `"$escapedPath`""
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseShellExecute = $false

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    try {
        [void]$process.Start()
        if (-not $process.WaitForExit(10000)) {
            try {
                $process.Kill()
            } catch {
                Write-Host "SKIPPED killing timed-out TOML validator process because it already exited."
            }
            throw "TOML validation timed out after 10 seconds for '$Path'."
        }

        if ($process.ExitCode -ne 0) {
            $detail = (@($process.StandardOutput.ReadToEnd(), $process.StandardError.ReadToEnd()) |
                ForEach-Object { $_.ToString().Trim() } |
                Where-Object { $_ }) -join " "
            if ([string]::IsNullOrWhiteSpace($detail)) {
                $detail = "python exited with code $($process.ExitCode)."
            }
            throw "Invalid TOML at '$Path': $detail"
        }
    } finally {
        $process.Dispose()
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

    $repoPrefix = Get-NormalizedChildPathPrefix -Path $normalizedRepoRoot
    if (-not $normalizedGovernanceRoot.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Repo root '$normalizedRepoRoot' must contain the governance root '$normalizedGovernanceRoot' so generated adapters only point at canonical in-repo governance files."
    }

    return (Get-RelativeLinkTarget -BaseDirectory $normalizedRepoRoot -TargetPath $normalizedGovernanceRoot).Replace("\", "/")
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

    if ($rawValue -is [bool]) {
        return $rawValue
    }

    if ($rawValue -is [string]) {
        switch ($rawValue.Trim().ToLowerInvariant()) {
            "true" { return $true }
            "false" { return $false }
            default { return $false }
        }
    }

    if ($rawValue -is [int] -or $rawValue -is [long]) {
        switch ([int64]$rawValue) {
            1 { return $true }
            0 { return $false }
            default { return $false }
        }
    }

    return $false
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
    $platformIndexPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/platforms/platforms_index.md"
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
    $platformIndexPath = Join-MarkdownReferencePath -BasePath $GovernanceReferenceRoot -RelativePath "docs/agents/platforms/platforms_index.md"
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

$allowedIncludes = @("skills", "mcp", "settings", "acp")
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
                            Ensure-DirectoryLink -LinkPath $linkPath -TargetPath $skillDir.FullName -UseRelativeTarget:$useRelative -AllowReplace:$Force -RepairPlainStubs:$RepairPlainDirectoryStubs
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
