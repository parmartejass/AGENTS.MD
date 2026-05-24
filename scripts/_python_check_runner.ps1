$ErrorActionPreference = "Stop"

$script:MinimumPythonMajor = 3
$script:MinimumPythonMinor = 11
$script:PythonVersionProbeTimeoutMilliseconds = 10000
$script:ProcessTreeCleanupTimeoutMilliseconds = 5000

function Stop-CheckProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [System.Diagnostics.Process]$Process,
    [Parameter(Mandatory = $true)]
    [string]$DisplayName
  )

  if ($Process.HasExited) {
    return
  }

  try {
    $Process.Kill($true)
    return
  } catch [System.Management.Automation.MethodException] {
  } catch [System.MissingMethodException] {
  }

  if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
    $taskkill = Get-Command "taskkill.exe" -ErrorAction SilentlyContinue
    if ($taskkill) {
      $startInfo = New-Object System.Diagnostics.ProcessStartInfo
      $startInfo.FileName = $taskkill.Source
      $startInfo.Arguments = "/PID $($Process.Id) /T /F"
      $startInfo.UseShellExecute = $false
      $startInfo.RedirectStandardOutput = $true
      $startInfo.RedirectStandardError = $true

      $taskkillProcess = New-Object System.Diagnostics.Process
      $taskkillProcess.StartInfo = $startInfo
      try {
        if (-not $taskkillProcess.Start()) {
          throw "FAILED_CLEANUP: Failed to start taskkill for $DisplayName."
        }
        if (-not $taskkillProcess.WaitForExit($script:ProcessTreeCleanupTimeoutMilliseconds)) {
          try {
            $taskkillProcess.Kill()
          } catch {
          }
          throw "FAILED_CLEANUP: taskkill timed out while terminating $DisplayName process tree."
        }
        if (-not $Process.HasExited) {
          [void]$Process.WaitForExit(1000)
        }
        if (-not $Process.HasExited -and $taskkillProcess.ExitCode -ne 0) {
          $details = ($taskkillProcess.StandardError.ReadToEnd() + " " + $taskkillProcess.StandardOutput.ReadToEnd()).Trim()
          throw "FAILED_CLEANUP: taskkill failed while terminating $DisplayName process tree: $details"
        }
        return
      } finally {
        $taskkillProcess.Dispose()
      }
    }
  }

  $Process.Kill()
}

function Invoke-PythonVersionProbe {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath
  )

  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = $PythonPath
  $startInfo.Arguments = "-c `"import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')`""
  $startInfo.UseShellExecute = $false
  $startInfo.RedirectStandardOutput = $true
  $startInfo.RedirectStandardError = $true

  $process = New-Object System.Diagnostics.Process
  $process.StartInfo = $startInfo

  try {
    if (-not $process.Start()) {
      return $null
    }
    if (-not $process.WaitForExit($script:PythonVersionProbeTimeoutMilliseconds)) {
      try {
        Stop-CheckProcessTree -Process $process -DisplayName "Python version probe"
      } catch {
        throw "FAILED_CLEANUP: Python version probe timed out after $script:PythonVersionProbeTimeoutMilliseconds ms and process termination failed: $($_.Exception.Message)"
      }
      if (-not $process.WaitForExit($script:ProcessTreeCleanupTimeoutMilliseconds)) {
        throw "FAILED_CLEANUP: Python version probe timed out after $script:PythonVersionProbeTimeoutMilliseconds ms and did not exit within $script:ProcessTreeCleanupTimeoutMilliseconds ms after termination."
      }
      throw "FAILED_VALIDATION: Python version probe timed out after $script:PythonVersionProbeTimeoutMilliseconds ms: $PythonPath"
    }
    if ($process.ExitCode -ne 0) {
      return $null
    }
    return $process.StandardOutput.ReadToEnd().Trim()
  } finally {
    $process.Dispose()
  }
}

function Resolve-CheckPythonExecutable {
  param(
    [string]$RequestedPython
  )

  $candidates = @()
  if (-not [string]::IsNullOrWhiteSpace($RequestedPython)) {
    $candidates += $RequestedPython
  } else {
    $candidates += "python3"
    $candidates += "python"
  }

  foreach ($candidate in $candidates) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if (-not $command) {
      continue
    }
    $source = $command.Source
    if ([string]::IsNullOrWhiteSpace($source)) {
      continue
    }
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
      continue
    }

    $versionText = Invoke-PythonVersionProbe -PythonPath $source
    if ([string]::IsNullOrWhiteSpace($versionText)) {
      continue
    }
    $parts = $versionText.Split(".")
    if ($parts.Count -lt 2) {
      continue
    }
    $major = 0
    $minor = 0
    if (-not [int]::TryParse($parts[0], [ref]$major)) {
      continue
    }
    if (-not [int]::TryParse($parts[1], [ref]$minor)) {
      continue
    }
    if ($major -gt $script:MinimumPythonMajor -or ($major -eq $script:MinimumPythonMajor -and $minor -ge $script:MinimumPythonMinor)) {
      Write-Host "Python selected: $source (policy: -PythonExe if provided, otherwise python3 then python; requires $script:MinimumPythonMajor.$script:MinimumPythonMinor+)."
      return $source
    }
  }

  if ([string]::IsNullOrWhiteSpace($RequestedPython)) {
    throw "FAILED_VALIDATION: Python $script:MinimumPythonMajor.$script:MinimumPythonMinor+ executable not found. Tried python3, then python."
  }
  throw "FAILED_VALIDATION: PythonExe must resolve to Python $script:MinimumPythonMajor.$script:MinimumPythonMinor+ executable: $RequestedPython"
}

function ConvertTo-CheckCommandArgument {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Value
  )

  if ($Value.Length -eq 0) {
    return '""'
  }
  if ($Value -notmatch '[\s"]') {
    return $Value
  }

  $builder = New-Object System.Text.StringBuilder
  [void]$builder.Append('"')
  $backslashes = 0
  foreach ($char in $Value.ToCharArray()) {
    if ($char -eq '\') {
      $backslashes++
      continue
    }
    if ($char -eq '"') {
      [void]$builder.Append('\' * (($backslashes * 2) + 1))
      [void]$builder.Append('"')
      $backslashes = 0
      continue
    }
    if ($backslashes -gt 0) {
      [void]$builder.Append('\' * $backslashes)
      $backslashes = 0
    }
    [void]$builder.Append($char)
  }
  if ($backslashes -gt 0) {
    [void]$builder.Append('\' * ($backslashes * 2))
  }
  [void]$builder.Append('"')
  return $builder.ToString()
}

function Invoke-PythonCheck {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath,
    [Parameter(Mandatory = $true)]
    [string[]]$Arguments,
    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory,
    [Parameter(Mandatory = $true)]
    [int]$TimeoutMilliseconds,
    [Parameter(Mandatory = $true)]
    [string]$DisplayName,
    [string]$ExpectedSuccessMarker,
    [string]$NonZeroExitPhase = "FAILED_VALIDATION"
  )

  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = $PythonPath
  $startInfo.Arguments = (($Arguments | ForEach-Object { ConvertTo-CheckCommandArgument $_ }) -join " ")
  $startInfo.WorkingDirectory = $WorkingDirectory
  $startInfo.UseShellExecute = $false
  $startInfo.RedirectStandardOutput = $true
  $startInfo.RedirectStandardError = $true

  $process = New-Object System.Diagnostics.Process
  $process.StartInfo = $startInfo
  $stdoutTask = $null
  $stderrTask = $null

  try {
    if (-not $process.Start()) {
      throw "FAILED_VALIDATION: Failed to start $DisplayName."
    }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()

    if (-not $process.WaitForExit($TimeoutMilliseconds)) {
      try {
        Stop-CheckProcessTree -Process $process -DisplayName $DisplayName
      } catch {
        throw "FAILED_CLEANUP: $DisplayName timed out after $TimeoutMilliseconds ms and process termination failed: $($_.Exception.Message)"
      }
      if (-not $process.WaitForExit($script:ProcessTreeCleanupTimeoutMilliseconds)) {
        throw "FAILED_CLEANUP: $DisplayName timed out after $TimeoutMilliseconds ms and did not exit within $script:ProcessTreeCleanupTimeoutMilliseconds ms after termination."
      }
      throw "FAILED_VALIDATION: $DisplayName timed out after $TimeoutMilliseconds ms."
    }

    $stdoutText = $stdoutTask.Result
    $stderrText = $stderrTask.Result
    if (-not [string]::IsNullOrEmpty($stdoutText)) {
      Write-Host $stdoutText.TrimEnd()
    }
    if (-not [string]::IsNullOrEmpty($stderrText)) {
      [Console]::Error.WriteLine($stderrText.TrimEnd())
    }

    if ($process.ExitCode -ne 0) {
      throw "${NonZeroExitPhase}: $DisplayName failed with exit code $($process.ExitCode)."
    }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedSuccessMarker)) {
      $combinedOutput = $stdoutText + "`n" + $stderrText
      if ($combinedOutput -notlike "*$ExpectedSuccessMarker*") {
        $excerpt = $combinedOutput
        if ($excerpt.Length -gt 1000) {
          $excerpt = $excerpt.Substring(0, 1000) + "..."
        }
        throw "FAILED_VALIDATION: $DisplayName exited 0 but did not emit expected success marker '$ExpectedSuccessMarker'. Output excerpt: $excerpt"
      }
    }
  } finally {
    $process.Dispose()
  }
}
