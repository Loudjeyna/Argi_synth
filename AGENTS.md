# SynthAI — Agent Guide

## Project Overview

SynthAI is an agricultural synthetic data platform with three independent modes of operation, three user roles (admin/farmer/company), and two separate auth systems.

## Quick Start

```powershell
# Mode A — Static frontend (no backend needed, JS simulation fallback)
python run.py                       # ThreadingHTTPServer on 127.0.0.1:8080
# → http://127.0.0.1:8080/pages/login.html

# Mode B — Streamlit app (Python only, uses src/ directly)
streamlit run app.py                # or: python main.py

# Mode C — FastAPI backend (REST layer between frontend and src/)
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Default login: `admin` / `admin123` (auto-seeded in both localStorage and SQLite).

## Architecture

```
frontend/                  # Static HTML/CSS/JS — works alone with localStorage
├── pages/                 # 16 HTML files (removed: admin_model.html)
├── js/app.js              # Router, sidebar, global logout event delegation
├── js/services/           # 7 modules: auth, data, history, recommendation, api, payment, model
└── styles/global.css

backend/                   # FastAPI — wraps src/ as REST API
├── main.py                # Self-contained (controllers/, services/, models/, utils/ are empty)
├── controllers/           # Empty (reserved)
├── services/              # Empty (reserved)
├── models/                # Empty (reserved)
├── utils/                 # Empty (reserved)
└── generated/             # Output CSVs

src/                       # Core Python — can be used standalone
├── ctgan_model.py         # SDV CTGAN wrapper, requires batch_size divisible by 10
├── database.py            # SQLite (data/agroai.db)
├── data_loader.py         # CSV → DataFrame with column type inference
├── generator.py           # Statistics, comparison, synthetic data
└── recommender.py         # Crop recommender (singleton, reads data/Crop_recommendation.csv)

data/Crop_recommendation.csv   # Source dataset: 2200 rows, 7 numerical + 1 categorical label, 22 crops
```

## Critical Conventions

### Frontend
- **All page redirects must use absolute `/pages/xxx.html`** — defined in `app.js` as `PREFIX = '/pages/'`. Relative paths break because pages are served from subdirectories.
- **Auth is dual:** `AuthService` stores user DB in `localStorage` (`synthai_users`), active session in `sessionStorage` (`synthai_session`). Logout clears sessionStorage.
- **Logout must go through event delegation** (`app.js:108`) — catches `#logout-btn` clicks globally regardless of per-page JS setup. Do NOT rely on `setupLogout()` succeeding.
- **API circuit-breaker:** `ApiService` does a 3s health check on load, caches result in `sessionStorage` (`synthai_api_available`). On network error it falls back to JS simulation via `DataService`. Do not remove the fallback.
- **Data generation** stores full dataset in-memory (`_fullDatasetCache`), only first 50 rows in localStorage (5MB limit). `exportCSV()` accepts optional `fullData` parameter.
- **Recommendation service** (`recommendation.js`) uses Algerian-relevant crops with French display names. The Python `CropRecommender` uses the original 22 English crop names from the CSV.
- **Three dataset types:** crop, soil, weather. Three fixed sizes: Medium (1,000), Large (10,000), Big Data (100,000).
- **Model management** (`ModelService` in `model.js`) stores model list in `synthai_models` localStorage key, full cleaned dataset in `synthai_model_data_<id>`. Models have status: trained/in_progress/failed. Training is separate from generation — train once, generate anytime.
- **New admin pages:** `admin_training.html` (upload, clean, configure, Add Training), `admin_models.html` (list/search/filter models), `admin_model_details.html` (view model, generate data from it). Sidebar links added in `app.js`.
- **Old `admin_model.html` deleted** — replaced by the new training system (admin_training → admin_models → admin_model_details).

### Backend / Python
- **`backend/main.py` is self-contained** — the `controllers/`, `services/`, `utils/`, `models/` subdirectories are empty. All routes are in `main.py`.
- **CTGAN batch_size must be divisible by PAC (default 10)** — auto-adjusted in `ctgan_model.py:45` via `_adjust_batch_size()`. If adjusting, ensure `batch_size >= pac`.
- **Joblib must run single-threaded** — `JOBLIB_SINGLE_THREADED=1` and `LOKY_MAX_CPU_COUNT=1` must be set before importing `sdv` to avoid pickle errors in FastAPI thread pools (`backend/main.py:10-11`).
- **Working directory must be project root** for Python modules that use relative paths (`src/database.py` → `data/agroai.db`, `src/recommender.py` → `data/Crop_recommendation.csv`). `backend/main.py` does `os.chdir()` to project root at startup.
- **`src/database.py`** uses SQLite with tables: `users`, `usage_logs`, `model_status`, `synthetic_datasets`. `Database.init_db()` creates them.

## Files You Should Not Touch
- `admin.txt`, `farmer.txt`, `company.txt` — role documentation, not code.
- `run.py` — uses `ThreadingHTTPServer` (NOT `http.server`) because Python's built-in server blocks on parallel CSS/JS requests. Do not change the server class.
