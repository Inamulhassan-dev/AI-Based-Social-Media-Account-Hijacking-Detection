@echo off
setlocal ENABLEDELAYEDEXPANSION

cd /d "%~dp0"

echo ======================================
echo AI-Hijacking-Detection Windows Setup
echo ======================================

echo.
echo [1/8] Checking required tools...
where winget >nul 2>&1
if errorlevel 1 (
  echo [ERROR] winget is not available on this system.
  echo Please install App Installer from Microsoft Store, then rerun this script.
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo Python not found. Installing Python 3.11...
  winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
) else (
  echo Python found.
)

where node >nul 2>&1
if errorlevel 1 (
  echo Node.js not found. Installing Node.js LTS...
  winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
) else (
  echo Node.js found.
)

where git >nul 2>&1
if errorlevel 1 (
  echo Git not found. Installing Git...
  winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
) else (
  echo Git found.
)

echo.
echo [2/8] Refreshing shell PATH (new installs may require reopening terminal)...

set "PYTHON_CMD=python"
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

echo.
echo [3/8] Preparing backend virtual environment...
if not exist backend\venv (
  cmd /c %PYTHON_CMD% -m venv backend\venv
  if errorlevel 1 (
    echo [ERROR] Failed to create backend virtual environment.
    exit /b 1
  )
) else (
  echo backend\venv already exists.
)

echo.
echo [4/8] Installing backend dependencies...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
if errorlevel 1 (
  echo [ERROR] Backend dependency installation failed.
  exit /b 1
)

echo.
echo [5/8] Preparing backend environment file...
if not exist backend\.env (
  copy /Y backend\.env.example backend\.env >nul
  echo Created backend\.env from template.
) else (
  echo backend\.env already exists.
)

echo.
echo [6/8] Installing frontend dependencies...
pushd frontend
call npm install
if errorlevel 1 (
  popd
  echo [ERROR] Frontend dependency installation failed.
  exit /b 1
)
popd

echo.
echo [7/8] Optional model bootstrap (dataset + training, first-time setup)...
pushd backend
python -c "import os; os.makedirs('data', exist_ok=True); from ml.generate_dataset import generate_dataset; from ml.train_model import train_all_models; generate_dataset(); train_all_models(); print('ML bootstrap completed')"
if errorlevel 1 (
  echo [WARN] ML bootstrap failed now. App can still run and train on first startup.
)
popd

echo.
echo [8/8] Setup finished.
echo Run start_project.bat to launch backend and frontend.

endlocal
