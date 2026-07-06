@echo off
setlocal
set "APP_DIR=%LOCALAPPDATA%\NetworkWatchdog"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desk=[Environment]::GetFolderPath('Desktop'); $lnk=Join-Path $desk 'Network Watchdog.lnk'; if (Test-Path $lnk) { Remove-Item $lnk -Force }"
echo This will remove "%APP_DIR%".
echo Your local settings in that folder will also be removed.
pause
if exist "%APP_DIR%" rmdir /S /Q "%APP_DIR%"
echo Uninstalled.
pause
