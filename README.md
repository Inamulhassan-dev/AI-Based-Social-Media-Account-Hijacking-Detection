# AI-Based Social Media Account Hijacking Detection

Full-stack project with:
- Backend: Flask + SQLAlchemy + JWT + Socket.IO
- Frontend: React + Vite + Tailwind
- ML: behavior anomaly detection models

## Current Readiness Status

The project is mostly ready to run and upload to GitHub.

Verified checks:
- Frontend production build passes (`npm run build`).
- Backend Python syntax compile passes.
- VS Code diagnostics currently report no code errors.

Not a blocker, but note:
- Frontend bundle is large and Vite warns about chunk size. This is optimization work, not a startup failure.

## Prerequisites

On Windows:
- Python 3.11+ (project was designed around 3.11)
- Node.js LTS
- npm
- Git
- Optional: Docker Desktop (for containerized run)

## Fastest Setup (Windows Scripts)

From project root, run in this order:

1. `setup_windows.bat`
2. `start_project.bat`
3. `stop_project.bat` (when done)

What each script does:

1. `setup_windows.bat`
- Checks/installs Python, Node, Git via winget.
- Creates `backend/venv`.
- Installs backend and frontend dependencies.
- Creates `backend/.env` from `backend/.env.example`.
- Attempts first-time ML bootstrap.

2. `start_project.bat`
- Starts backend and frontend in separate terminal windows.
- Uses `backend/run_backend.bat` and `frontend/run_frontend.bat`.

3. `stop_project.bat`
- Stops both windows/processes by window title.

Open:
- Frontend: http://localhost:3000
- Backend health: http://localhost:5000/api/health

## Manual Setup (No Scripts)

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### Frontend

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

## Environment Variables

### Backend: `backend/.env`

Required to review/change before production:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `FLASK_DEBUG`
- `FRONTEND_ORIGIN`
- `JWT_COOKIE_SECURE`
- Mail credentials (`MAIL_USERNAME`, `MAIL_PASSWORD`) if email features are used

### Frontend: `frontend/.env`

`VITE_API_BASE_URL` controls API target.

Default example:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## Docker Setup

1. Ensure `backend/.env` exists (copy from example if needed).
2. Build and run:

```powershell
docker compose up --build
```

3. Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## How To Check Errors / Malfunctions

### 1) Backend health endpoint

Open:
- `http://localhost:5000/api/health`

Expected JSON:
- `status: healthy`

### 2) Frontend build check

```powershell
cd frontend
npm run build
```

### 3) Backend syntax check

```powershell
cd ..
backend\venv\Scripts\python.exe -m compileall backend
```

### 4) Typical issues

- Port conflict on `3000` or `5000`: stop other apps using those ports.
- CORS errors: ensure backend `FRONTEND_ORIGIN` matches frontend URL.
- Missing Python/Node: rerun `setup_windows.bat`.
- Docker startup issues: confirm Docker Desktop is running.

## GitHub Upload Guide (Full)

This workspace is not initialized as a Git repository yet.

From project root:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial commit: AI Hijacking Detection"
```

Create an empty GitHub repository, then connect and push:

```powershell
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Important Git Safety

Already ignored by `.gitignore`:
- `backend/.env`
- `backend/venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- local runtime/editor folders

Before pushing, run:

```powershell
git status
```

Verify no secrets are staged.

## Suggested Next Improvements

1. Add automated tests for backend routes and auth flow.
2. Add CI (GitHub Actions) for lint + build checks on each push.
3. Split large frontend bundle with lazy routes/dynamic imports.
