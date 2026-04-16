# AI-Based Social Media Account Hijacking Detection

![CI](https://github.com/Inamulhassan-dev/AI-Based-Social-Media-Account-Hijacking-Detection/actions/workflows/ci.yml/badge.svg)

Professional full-stack security platform for detecting suspicious login behavior and possible social media account takeover attempts.

## Why This Project Matters Today

Social media account hijacking is one of the fastest-growing security problems for students, creators, freelancers, and businesses. This system helps detect suspicious behavior early by combining:

- Rule-based risk scoring
- ML anomaly scoring
- Real-time alerts and risk feed
- Social-media-focused threat insights

It is useful for today's generation because many people use social apps as identity, business, and communication channels. Early hijacking detection reduces account loss, data leakage, and reputation damage.

## What This System Analyzes

The backend analyzes login telemetry and behavior signals such as:

- Device fingerprint and new device detection
- New location and impossible travel patterns
- Unusual login times
- VPN/proxy usage indicators
- Failed login attempts and brute-force patterns
- ML ensemble anomaly score

The dashboard then visualizes:

- Current risk score
- Risk history trend
- Alert severity and live security feed
- Country-based threat map
- Social media threat insights panel

## Main Features

- Secure authentication with JWT
- Login risk scoring engine
- ML-powered anomaly detection
- Real-time alerting and security feed
- Threat map and impossible travel detection
- Social insights endpoint for takeover risk summary
- Admin views for users, alerts, and model performance

## Roles and Access

- First registered account becomes `admin`
- Later accounts become `user`
- Admin can unlock users and manage alerts
- Users can view their own dashboard, alerts, and risk history

## Tech Stack

- Backend: Flask, SQLAlchemy, Flask-JWT-Extended, Flask-SocketIO
- Frontend: React, Vite, Tailwind CSS
- ML/Data: scikit-learn, XGBoost, pandas, numpy
- Database: SQLite (default)

## Project Structure

```text
backend/
	app.py
	routes/
	services/
	models/
	ml/
frontend/
	src/
	components/
	pages/
docker-compose.yml
setup_windows.bat
start_project.bat
stop_project.bat
```

## Step-by-Step Setup

### Option A: Automatic Setup (Windows)

From project root, run:

1. `setup_windows.bat`
2. `start_project.bat`

Then open:

- Frontend app: http://localhost:3000
- Backend health: http://localhost:5000/api/health

To stop both services:

3. `stop_project.bat`

### Option B: Manual Setup (Windows)

#### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

#### Frontend

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

### Option C: Manual Setup (Linux / macOS)

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

#### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Then open:

- Frontend app: http://localhost:3000
- Backend health: http://localhost:5000/api/health

## Datasets & ML Models

The project generates its own synthetic dataset and trains ML models on first startup — **no external downloads required**.

### How it works

1. On first run (`python app.py` from `backend/`), the app detects missing models and automatically:
   - Generates `backend/data/user_behavior_dataset.csv` (6 000 synthetic login records)
   - Trains three models and saves them to `backend/ml/saved_models/`:
     - `random_forest.pkl`
     - `xgboost_model.pkl`
     - `isolation_forest.pkl`
     - `scaler.pkl`
     - `training_results.json`

2. You can also trigger this manually:

   ```bash
   cd backend
   source venv/bin/activate   # Windows: venv\Scripts\activate
   python -c "from ml.generate_dataset import generate_dataset; from ml.train_model import train_all_models; generate_dataset(); train_all_models()"
   ```

> The generated dataset and trained model files are excluded from version control via `.gitignore`.



### Backend `.env`

Key variables to review:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `FRONTEND_ORIGIN`
- `FLASK_DEBUG`
- `JWT_COOKIE_SECURE`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`

### Frontend `.env`

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## API Overview

Important API groups:

- Auth: `/api/auth/*`
- Dashboard: `/api/dashboard/*`
- Alerts: `/api/alerts/*`
- Analysis: `/api/analysis/*`
- Admin: `/api/admin/*`

Social insights endpoint:

- `GET /api/analysis/social-insights` (JWT required)

## How To Use the App

1. Register your first account (this becomes admin).
2. Login and open the dashboard.
3. Review risk score, alerts, and threat map.
4. Use demo scenarios (if available in UI) to simulate suspicious events.
5. Check alerts and take actions (mark legit, report suspicious, lock behavior).
6. Use admin panel for user/alert oversight.

## Docker Setup

```powershell
docker compose up --build
```

Access:

- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Troubleshooting

1. Frontend not opening:
- Verify Node.js and npm are installed
- Re-run `setup_windows.bat`

2. Backend not starting:
- Confirm `backend/.env` exists
- Confirm Python venv exists at `backend/venv`

3. CORS/API errors:
- Ensure `FRONTEND_ORIGIN` matches frontend URL
- Ensure `VITE_API_BASE_URL` points to backend API

4. Port conflicts:
- Free ports `3000` and `5000` or change config

## Production Notes

- Set strong random values for `SECRET_KEY` and `JWT_SECRET_KEY`
- Set `FLASK_DEBUG=false`
- Use HTTPS and set `JWT_COOKIE_SECURE=true`
- Use a production database instead of SQLite for scale

## GitHub Upload Guide

If this is a new repo:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial commit: AI-Based Social Media Account Hijacking Detection"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If repo already exists locally:

```powershell
git add .
git commit -m "Update project documentation and features"
git push
```

Before pushing, always verify:

```powershell
git status
```

## Roadmap

Planned improvements:

1. Session takeover controls (view/revoke active sessions)
2. DM phishing/scam content detector
3. Social action anomaly detection (mass follow/unfollow, spam bursts)
4. Automated backend/frontend tests
5. ~~CI pipeline with GitHub Actions~~ ✅ Added

## License

Add your preferred open-source license (MIT, Apache-2.0, etc.) before public release.
