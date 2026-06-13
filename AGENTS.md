# SynthAI — Agent Guide

## Project Overview

SynthAI is an agricultural synthetic data platform with three independent modes of operation, three user roles (admin/farmer/company), and two separate auth systems.

## Quick Start

```powershell
# Mode A — Static frontend (no backend needed, JS simulation fallback)
python run.py                       # ThreadingHTTPServer on 127.0.0.1:8080
# → http://127.0.0.1:8080/pages/login.html

# Mode B — Streamlit app (Python only)
streamlit run app.py

# Mode C — FastAPI backend (REST layer)
python main.py                      # uvicorn on 127.0.0.1:8001 (use --reload flag for dev)
```

Default login: `admin` / `admin123` (auto-seeded in both localStorage and SQLite).

## Architecture (6-Layer Python Package)

```
synthai/                     # New 6-layer backend package
├── data/                    # Data Layer — SQLite + config + repositories
│   ├── config/settings.py   # Paths, defaults, CTGAN params, plan limits
│   ├── database.py          # 18-table SQLite schema + seed admin
│   └── repositories/        # 6 repos: user, model, dataset, prediction, payment, crop
├── ai/                      # AI Core Layer — ML models + preprocessing
│   ├── models/ctgan.py      # SDV CTGAN wrapper (batch_size divisible by PAC=10)
│   ├── preprocessing/       # DataLoader (CSV → DataFrame + column type inference)
│   ├── generation/          # SyntheticDataGenerator
│   └── evaluation/          # DataStatistics, DataComparison
├── business/                # Business Logic Layer — rules + recommendations
│   ├── recommendation/      # CropRecommender (singleton, 22 crops, Euclidean distance)
│   └── rules/               # subscription_rules, validation_rules, access_control, usage_limits
├── services/                # Application Service Layer — 6 services
│   ├── auth_service.py      # register/login/logout + session tokens
│   ├── training_service.py  # DataLoader → CTGAN → Generator → persist
│   ├── generation_service.py# generate + validate + CSV export
│   ├── prediction_service.py# recommender + persist history
│   ├── subscription_service.py # plan change + payment
│   └── augmentation_service.py # CSV parse + multiplier + validate
└── api/                     # API Layer — FastAPI
    ├── app.py               # App factory (lifespan, CORS, 6 routers)
    ├── middleware.py         # require_auth (Bearer token), require_role (factory)
    └── routes/              # health, auth, users, models, datasets, predictions

frontend/                    # Static HTML/CSS/JS — Presentation Layer for Mode A
├── pages/                   # 16 HTML files
├── js/app.js                # Router, sidebar, global logout event delegation
├── js/services/             # 7 modules: auth, data, history, recommendation, api, payment, model
└── styles/global.css

data/                        # Data files
├── Crop_recommendation.csv  # 2200 rows, 7 numerical + 1 categorical label, 22 crops
├── agroai.db                # SQLite (18 tables)
└── generated/               # Output CSVs from generation
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
- **Admin page flow:** `admin_training.html` → `admin_models.html` → `admin_model_details.html`.

### Backend / Python
- **6-layer architecture:** Data → AI → Business → Services → API → Presentation (strict dependency direction, no circular imports).
- **`synthai/data/config/settings.py`** is the single source of truth for paths, CTGAN defaults, and plan limits.
- **Single Responsibility:** business logic (`business/`) does not import from storage (`data/`). Services (`services/`) orchestrate across layers.
- **CTGAN batch_size must be divisible by PAC (default 10)** — auto-adjusted in `ctgan.py` via `_adjust_batch_size()`. If adjusting, ensure `batch_size >= pac`.
- **Joblib must run single-threaded** — `JOBLIB_SINGLE_THREADED=1` and `LOKY_MAX_CPU_COUNT=1` set in `main.py:8-9` before importing `sdv` to avoid pickle errors.
- **All paths are absolute** (derived from `Path(__file__).resolve().parents[3]` in settings.py). No relative-path dependencies.
- **`database.py`** creates 18 tables: users, user_settings, sessions, crops, crop_requirements, crop_recommendations, soil_textures, weather_zones, models, model_versions, model_datasets, generations, generation_data, augmentations, predictions, payments, usage_logs, model_status.
- **`CropRecommender`** is a singleton; reads `data/Crop_recommendation.csv` via `CROP_CSV_PATH`.

## Files You Should Not Touch
- `admin.txt`, `farmer.txt`, `company.txt` — role documentation, not code.
- `run.py` — uses `ThreadingHTTPServer` (NOT `http.server`) because Python's built-in server blocks on parallel CSS/JS requests. Do not change the server class.
