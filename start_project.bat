@echo off
setlocal

cd /d "%~dp0"
if not exist .runtime mkdir .runtime

set "BACKEND_WINDOW=AIHD_BACKEND"
set "FRONTEND_WINDOW=AIHD_FRONTEND"
set "BACKEND_DIR=%CD%\backend"
set "FRONTEND_DIR=%CD%\frontend"

echo Starting backend and frontend...

if not exist "%BACKEND_DIR%\app.py" (
	echo [ERROR] Backend app.py not found at "%BACKEND_DIR%\app.py"
	exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
	echo [ERROR] Frontend package.json not found at "%FRONTEND_DIR%\package.json"
	exit /b 1
)

if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
	echo [ERROR] Backend virtual environment is missing.
	echo Run setup_windows.bat first.
	exit /b 1
)

if not exist "%BACKEND_DIR%\run_backend.bat" (
	echo [ERROR] Backend launcher not found at "%BACKEND_DIR%\run_backend.bat"
	exit /b 1
)

if not exist "%FRONTEND_DIR%\run_frontend.bat" (
	echo [ERROR] Frontend launcher not found at "%FRONTEND_DIR%\run_frontend.bat"
	exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
	echo [ERROR] npm is not available in PATH.
	echo Install Node.js or run setup_windows.bat first.
	exit /b 1
)

echo Launching backend...
start "%BACKEND_WINDOW%" cmd /k "call \"%BACKEND_DIR%\run_backend.bat\""

echo Launching frontend...
start "%FRONTEND_WINDOW%" cmd /k "call \"%FRONTEND_DIR%\run_frontend.bat\""

> .runtime\windows.info echo BACKEND_WINDOW=%BACKEND_WINDOW%
>> .runtime\windows.info echo FRONTEND_WINDOW=%FRONTEND_WINDOW%

echo.
echo Project started.
echo Backend and frontend windows were opened.
echo To stop both, run stop_project.bat.

endlocal
