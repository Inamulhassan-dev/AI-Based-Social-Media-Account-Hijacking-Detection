@echo off
setlocal

cd /d "%~dp0"

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] npm not found. Install Node.js or run ..\setup_windows.bat first.
  exit /b 1
)

npm run dev

endlocal
