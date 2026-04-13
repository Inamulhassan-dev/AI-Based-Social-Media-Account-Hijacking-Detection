@echo off
setlocal

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] backend\venv is missing. Run ..\setup_windows.bat first.
  exit /b 1
)

"venv\Scripts\python.exe" app.py

endlocal
