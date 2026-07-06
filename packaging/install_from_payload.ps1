$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$payloadZip = Join-Path $scriptRoot "install_payload.zip"
$appDir = Join-Path $env:LOCALAPPDATA "NetworkWatchdog"
$backupSettings = Join-Path $env:TEMP "network_watchdog_settings_backup.json"
$tempExtract = Join-Path $env:TEMP ("NetworkWatchdogInstall_" + [Guid]::NewGuid().ToString("N"))

if (!(Test-Path $payloadZip)) {
    throw "install_payload.zip was not found."
}

if (!(Test-Path $appDir)) {
    New-Item -ItemType Directory -Force $appDir | Out-Null
}

if (Test-Path (Join-Path $appDir "watchdog_settings.json")) {
    Copy-Item -Force (Join-Path $appDir "watchdog_settings.json") $backupSettings
}

New-Item -ItemType Directory -Force $tempExtract | Out-Null
Expand-Archive -Path $payloadZip -DestinationPath $tempExtract -Force

$sourceDir = Join-Path $tempExtract "NetworkWatchdog"
if (!(Test-Path (Join-Path $sourceDir "NetworkWatchdog.exe"))) {
    throw "NetworkWatchdog.exe was not found in installer payload."
}

Copy-Item -Recurse -Force (Join-Path $sourceDir "*") $appDir

if (Test-Path $backupSettings) {
    Copy-Item -Force $backupSettings (Join-Path $appDir "watchdog_settings.json")
    Remove-Item -Force $backupSettings
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Network Watchdog.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $appDir "NetworkWatchdog.exe"
$shortcut.WorkingDirectory = $appDir
$shortcut.Save()

Remove-Item -Recurse -Force $tempExtract
Start-Process -FilePath (Join-Path $appDir "NetworkWatchdog.exe") -WorkingDirectory $appDir
