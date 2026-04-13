@echo off
setlocal

cd /d "%~dp0"

echo Stopping backend and frontend...

taskkill /FI "WINDOWTITLE eq AIHD_BACKEND*" /T /F >nul 2>&1
if errorlevel 1 (
  echo Backend window/process not found.
) else (
  echo Backend stopped.
)

taskkill /FI "WINDOWTITLE eq AIHD_FRONTEND*" /T /F >nul 2>&1
if errorlevel 1 (
  echo Frontend window/process not found.
) else (
  echo Frontend stopped.
)

if exist .runtime\windows.info del /q .runtime\windows.info >nul 2>&1

echo.
echo Stop command finished.

endlocal
