$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$payloadZip = Join-Path $root "lite_payload.zip"
$installRoot = Join-Path $env:LOCALAPPDATA "NetworkWatchdogLite"

if (-not (Test-Path $payloadZip)) {
    [System.Windows.Forms.MessageBox]::Show(
        "lite_payload.zip was not found next to the setup launcher.",
        "Network Watchdog Lite Setup"
    ) | Out-Null
    exit 1
}

if (Test-Path $installRoot) {
    Remove-Item -Recurse -Force $installRoot
}

New-Item -ItemType Directory -Force $installRoot | Out-Null
Expand-Archive -Path $payloadZip -DestinationPath $installRoot -Force
Set-Location $installRoot

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    [System.Windows.Forms.MessageBox]::Show(
        "Python 3.10 or newer was not found.`n`nPlease install Python for Windows first, then run this setup again.`n`nDownload: https://www.python.org/downloads/windows/",
        "Network Watchdog Lite Setup"
    ) | Out-Null
    exit 1
}

$venvPython = Join-Path $installRoot ".venv\Scripts\python.exe"
$venvPythonW = Join-Path $installRoot ".venv\Scripts\pythonw.exe"

if (-not (Test-Path $venvPython)) {
    & python -m venv (Join-Path $installRoot ".venv")
}

if (-not (Test-Path $venvPython)) {
    [System.Windows.Forms.MessageBox]::Show(
        "Failed to create the local virtual environment.",
        "Network Watchdog Lite Setup"
    ) | Out-Null
    exit 1
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $installRoot "requirements.txt")

if (-not (Test-Path $venvPythonW)) {
    [System.Windows.Forms.MessageBox]::Show(
        "Dependencies were installed, but pythonw.exe was not found in the local virtual environment.",
        "Network Watchdog Lite Setup"
    ) | Out-Null
    exit 1
}

Start-Process -FilePath $venvPythonW -ArgumentList (Join-Path $installRoot "network_watchdog.py") -WorkingDirectory $installRoot -WindowStyle Hidden

[System.Windows.Forms.MessageBox]::Show(
    "Network Watchdog Lite has been prepared and started.",
    "Network Watchdog Lite Setup"
) | Out-Null
