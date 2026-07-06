@echo off
setlocal
set "SOURCE_DIR=%~dp0NetworkWatchdog"
set "APP_DIR=%LOCALAPPDATA%\NetworkWatchdog"
set "BACKUP_SETTINGS=%TEMP%\network_watchdog_settings_backup.json"

if not exist "%SOURCE_DIR%\NetworkWatchdog.exe" (
  echo NetworkWatchdog.exe was not found in "%SOURCE_DIR%".
  pause
  exit /b 1
)

if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if exist "%APP_DIR%\watchdog_settings.json" copy /Y "%APP_DIR%\watchdog_settings.json" "%BACKUP_SETTINGS%" >nul

xcopy "%SOURCE_DIR%\*" "%APP_DIR%\" /E /I /Y >nul

if exist "%BACKUP_SETTINGS%" (
  copy /Y "%BACKUP_SETTINGS%" "%APP_DIR%\watchdog_settings.json" >nul
  del "%BACKUP_SETTINGS%" >nul 2>nul
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$desk=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desk 'Network Watchdog.lnk')); $s.TargetPath=(Join-Path $env:LOCALAPPDATA 'NetworkWatchdog\NetworkWatchdog.exe'); $s.WorkingDirectory=(Join-Path $env:LOCALAPPDATA 'NetworkWatchdog'); $s.Save()"

echo Network Watchdog has been installed to:
echo %APP_DIR%
start "" "%APP_DIR%\NetworkWatchdog.exe"
pause
