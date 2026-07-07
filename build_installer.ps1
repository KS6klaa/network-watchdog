$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $root "release"
$installerRoot = Join-Path $releaseRoot "NetworkWatchdogInstaller"
$appBundle = Join-Path $installerRoot "NetworkWatchdog"
$zipPath = Join-Path $releaseRoot "NetworkWatchdogInstaller.zip"
$liteRoot = Join-Path $releaseRoot "NetworkWatchdogLite"
$liteZipPath = Join-Path $releaseRoot "NetworkWatchdogLite.zip"
$semiLiteSetupBuildRoot = Join-Path $releaseRoot "SemiLiteSetupBuild"
$semiLitePayloadZip = Join-Path $semiLiteSetupBuildRoot "lite_payload.zip"
$semiLiteSetupScript = Join-Path $semiLiteSetupBuildRoot "install_lite_payload.ps1"
$semiLiteSedPath = Join-Path $semiLiteSetupBuildRoot "NetworkWatchdogSemiLiteSetup.sed"
$semiLiteExePath = Join-Path $releaseRoot "SetupNetworkWatchdogLite.exe"
$setupBuildRoot = Join-Path $releaseRoot "SetupBuild"
$payloadZip = Join-Path $setupBuildRoot "install_payload.zip"
$setupScript = Join-Path $setupBuildRoot "install_from_payload.ps1"
$sedPath = Join-Path $setupBuildRoot "NetworkWatchdogSetup.sed"
$setupExePath = Join-Path $releaseRoot "SetupNetworkWatchdog.exe"

Set-Location $root

if (Test-Path (Join-Path $root "build")) {
    Remove-Item -Recurse -Force (Join-Path $root "build")
}
if (Test-Path (Join-Path $root "dist")) {
    Remove-Item -Recurse -Force (Join-Path $root "dist")
}
if (Test-Path $installerRoot) {
    Remove-Item -Recurse -Force $installerRoot
}
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}
if (Test-Path $liteRoot) {
    Remove-Item -Recurse -Force $liteRoot
}
if (Test-Path $liteZipPath) {
    Remove-Item -Force $liteZipPath
}
if (Test-Path $semiLiteSetupBuildRoot) {
    Remove-Item -Recurse -Force $semiLiteSetupBuildRoot
}
if (Test-Path $setupBuildRoot) {
    Remove-Item -Recurse -Force $setupBuildRoot
}
if (Test-Path $setupExePath) {
    Remove-Item -Force $setupExePath
}
if (Test-Path $semiLiteExePath) {
    Remove-Item -Force $semiLiteExePath
}

python -m PyInstaller `
    --noconfirm `
    --onedir `
    --windowed `
    --noupx `
    --name NetworkWatchdog `
    network_watchdog.py

New-Item -ItemType Directory -Force $installerRoot | Out-Null
Copy-Item -Recurse -Force (Join-Path $root "dist\NetworkWatchdog") $appBundle
Copy-Item -Force (Join-Path $root "watchdog_targets.json") (Join-Path $appBundle "watchdog_targets.json")
Copy-Item -Force (Join-Path $root "packaging\default_watchdog_settings.json") (Join-Path $appBundle "watchdog_settings.json")
Copy-Item -Force (Join-Path $root "README.md") (Join-Path $appBundle "README.md")
Copy-Item -Force (Join-Path $root "packaging\install.bat") (Join-Path $installerRoot "install.bat")
Copy-Item -Force (Join-Path $root "packaging\uninstall.bat") (Join-Path $installerRoot "uninstall.bat")

Compress-Archive -Path (Join-Path $installerRoot "*") -DestinationPath $zipPath -Force

New-Item -ItemType Directory -Force $liteRoot | Out-Null
Copy-Item -Force (Join-Path $root "network_watchdog.py") (Join-Path $liteRoot "network_watchdog.py")
Copy-Item -Force (Join-Path $root "requirements.txt") (Join-Path $liteRoot "requirements.txt")
Copy-Item -Force (Join-Path $root "watchdog_targets.json") (Join-Path $liteRoot "watchdog_targets.json")
Copy-Item -Force (Join-Path $root "packaging\default_watchdog_settings.json") (Join-Path $liteRoot "watchdog_settings.json")
Copy-Item -Force (Join-Path $root "README.md") (Join-Path $liteRoot "README.md")
Copy-Item -Force (Join-Path $root "packaging\install_lite.bat") (Join-Path $liteRoot "install_lite.bat")
Compress-Archive -Path (Join-Path $liteRoot "*") -DestinationPath $liteZipPath -Force

New-Item -ItemType Directory -Force $semiLiteSetupBuildRoot | Out-Null
Compress-Archive -Path (Join-Path $liteRoot "*") -DestinationPath $semiLitePayloadZip -Force
Copy-Item -Force (Join-Path $root "packaging\install_lite_payload.ps1") $semiLiteSetupScript

New-Item -ItemType Directory -Force $setupBuildRoot | Out-Null
Compress-Archive -Path $appBundle -DestinationPath $payloadZip -Force
Copy-Item -Force (Join-Path $root "packaging\install_from_payload.ps1") $setupScript

$sedContent = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=$setupExePath
FriendlyName=Network Watchdog Setup
AppLaunched=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install_from_payload.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles
[Strings]
FILE0="install_payload.zip"
FILE1="install_from_payload.ps1"
[SourceFiles]
SourceFiles0=$setupBuildRoot
[SourceFiles0]
%FILE0%=
%FILE1%=
"@
$sedContent | Set-Content -Path $sedPath -Encoding ASCII

iexpress.exe /N /Q $sedPath | Out-Null

$semiLiteSedContent = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=$semiLiteExePath
FriendlyName=Network Watchdog Lite Setup
AppLaunched=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install_lite_payload.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles
[Strings]
FILE0="lite_payload.zip"
FILE1="install_lite_payload.ps1"
[SourceFiles]
SourceFiles0=$semiLiteSetupBuildRoot
[SourceFiles0]
%FILE0%=
%FILE1%=
"@
$semiLiteSedContent | Set-Content -Path $semiLiteSedPath -Encoding ASCII

iexpress.exe /N /Q $semiLiteSedPath | Out-Null

Write-Host "Installer package created:"
Write-Host $zipPath
Write-Host $liteZipPath
Write-Host $setupExePath
Write-Host $semiLiteExePath
