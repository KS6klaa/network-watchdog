@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer was not found.
  echo Please install Python for Windows first, then run this file again.
  echo Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Creating local virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo Installing dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip.
  pause
  exit /b 1
)

call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install requirements.
  pause
  exit /b 1
)

echo Starting Network Watchdog...
start "" ".venv\Scripts\pythonw.exe" "%~dp0network_watchdog.py"
exit /b 0
