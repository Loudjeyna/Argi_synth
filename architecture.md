# SynthAI — Global Architecture

## Overview

SynthAI is an agricultural synthetic data platform with **3 modes of operation**, **3 user roles** (Admin / Farmer / Company), and **2 auth systems** (frontend localStorage + backend SQLite).

---

## System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Mode A / Mode C)                        │
│                                                                           │
│   ┌──────────────────────────────────────────────────────────────────┐    │
│   │                    HTML Pages (22 pages)                         │    │
│   │  login  │  admin_home/training/models/model_details/users/       │    │
│   │  augmentation  │  company_home/augment  │  farmer_home/predict/  │    │
│   │  comparison/requirements/crop_conditions/conditions_crop  │      │    │
│   │  generate_data  │  datasets/viewer/evaluation  │  history  │    │    │
│   │  subscription  │  model_comparison                              │    │
│   └──────────────────────────────────────────────────────────────────┘    │
│                                    │                                      │
│   ┌──────────────────────────────────────────────────────────────────┐    │
│   │                    JavaScript Services Layer                      │    │
│   │                                                                   │    │
│   │  app.js          ← Router, sidebar, auth guard, logout           │    │
│   │  i18n.js         ← Translation engine (ar/fr/en, ~685 keys)     │    │
│   │  services/auth.js      ← localStorage + sessionStorage auth     │    │
│   │  services/api.js       ← Circuit-breaker to http://localhost:8000│    │
│   │  services/data.js      ← JS simulation (CTGAN-style generation) │    │
│   │  services/model.js     ← Model CRUD + versioning                │    │
│   │  services/recommendation.js ← 22 Algerian crops, Euclidian      │    │
│   │  services/payment.js   ← Plans: Free/Pro/Premium                │    │
│   │  services/history.js   ← Prediction history in localStorage     │    │
│   └──────────────────────────────────────────────────────────────────┘    │
│                                    │                                      │
│   ┌──────────────────────────────────────────────────────────────────┐    │
│   │  Styles: global.css ← Green theme, RTL support, responsive      │    │
│   └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
         ┌──────────────────────────┴──────────────┐
         │                                         │
         ▼                                         ▼
  ┌──────────────────────┐         ┌──────────────────────────────────────┐
  │  Mode B: Streamlit   │         │  Mode C: FastAPI Backend             │
  │  app.py (834 lines)  │         │  backend/main.py (256 lines)         │
  │  ───────────────     │         │  ────────────────────────────         │
  │  Direct Python UI    │         │  Routes:                              │
  │  Uses src/ directly  │         │  POST /api/auth/login                 │
  │  Session state auth  │         │  POST /api/auth/register              │
  │  SQLite persistence  │         │  GET  /api/users                      │
  │                      │         │  POST /api/model/train                │
  │                      │         │  GET  /api/model/status               │
  │                      │         │  POST /api/generate                   │
  │                      │         │  GET  /api/datasets                   │
  │                      │         │  GET  /api/validate/{id}              │
  │                      │         │  GET  /api/stats                       │
  │                      │         │  GET  /api/health                     │
  │                      │         │                                       │
  │                      │         │  CORS: all origins                    │
  │                      │         │  Env: JOBLIB_SINGLE_THREADED=1        │
  │                      │         └──────────┬────────────────────────────┘
  └──────────────────────┘                    │
                                              ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                      CORE PYTHON (src/)                                │
  │                                                                        │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
  │  │ data_loader  │  │ ctgan_model  │  │  generator   │  │ database  │  │
  │  │──────────────│  │──────────────│  │──────────────│  │───────────│  │
  │  │ CSV→DataFrame│  │ SDV CTGAN    │  │ Statistics   │  │ SQLite    │  │
  │  │ Column types │  │ Wrapper      │  │ Comparison   │  │ SHA-256   │  │
  │  │              │  │ batch_size   │  │ Similarity   │  │ 6 tables  │  │
  │  │              │  │ auto-adjusted│  │ SyntheticGen │  │           │  │
  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  recommender.py ← Singleton CropRecommender                    │    │
  │  │  data/Crop_recommendation.csv (2200 rows, 22 crops, 7 params)  │    │
  │  │  Water/fertilizer levels via rule-based thresholds             │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  Data Sources:                                                         │
  │    data/agroai.db           → SQLite (users, models, datasets, logs)   │
  │    data/Crop_recommendation.csv → Training dataset (7 numeric cols)     │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 3 Deployment Modes

| Mode | Command | Tech | Auth | Data |
|------|---------|------|------|------|
| **A** | `python run.py` | ThreadingHTTPServer :8080 | localStorage/sessionStorage | JS simulation (DataService) |
| **B** | `streamlit run app.py` | Streamlit :8501 | Session state + SQLite | src/ directly |
| **C** | `uvicorn backend.main:app --host 0.0.0.0 --port 8000` | FastAPI :8000 | SQLite SHA-256 | FastAPI wraps src/ |

Mode A requires no Python dependencies beyond stdlib. Mode B & C use SDV, pandas, etc.

---

## Data Flow

```
1. User Action → HTML Page → JS Service → Decision:
   ├── Backend available? → ApiService → FastAPI → src/ modules → SQLite/CSV
   └── Backend unavailable → Local simulation (DataService, RecommendationService)
                                  ↓
                            localStorage/sessionStorage
```

---

## Auth System (Dual)

| Layer | Storage | Hash | Tables |
|-------|---------|------|--------|
| Frontend | `localStorage` (`synthai_users`) + `sessionStorage` (`synthai_session`) | Plaintext (frontend only) | — |
| Backend | SQLite `users` table | SHA-256 | `users`, `usage_logs`, `model_status`, `predictions`, `synthetic_datasets` |

**Roles:** `admin` (full access), `farmer` (predictions, conditions), `company` (data generation/augmentation)

**Default seed:** `admin` / `admin123` (both systems)

---

## Key Design Decisions

- **Circuit-breaker pattern**: `ApiService` health-checks backend on load (3s timeout), caches result in `sessionStorage`, falls back to JS simulation if unavailable
- **i18n first**: All user-facing text goes through `_t('key', 'Fallback')`, full RTL support for Arabic
- **Batch-size safety**: CTGAN `batch_size` auto-adjusted to be divisible by PAC=10
- **Single-threaded SDV**: `JOBLIB_SINGLE_THREADED=1` + `LOKY_MAX_CPU_COUNT=1` before importing SDV to avoid pickle errors
- **Model versioning**: Models support version history (initial + retrains), production model designation
- **Cloudinary integration**: Large generated datasets uploaded to Cloudinary for persistent storage
- **3 fixed data sizes**: Medium (1K), Large (10K), Big Data (100K) — premium-gated
- **3 dataset types**: crop, soil, weather — each with distinct generation logic

---

## Directory Structure

```
SynthAI/
├── frontend/
│   ├── pages/           # 22 HTML pages
│   ├── js/
│   │   ├── app.js       # Router, sidebar, auth guard
│   │   └── services/    # 8 service modules
│   ├── styles/
│   │   └── global.css   # 540 lines, green theme, RTL
│   └── locales/         # i18n JSON files
├── backend/
│   ├── main.py          # Self-contained FastAPI app
│   ├── controllers/     # Empty (reserved)
│   ├── services/        # Empty (reserved)
│   ├── models/          # Empty (reserved)
│   ├── utils/           # Empty (reserved)
│   └── generated/       # Output CSVs
├── src/
│   ├── ctgan_model.py   # SDV CTGAN wrapper
│   ├── database.py      # SQLite interface
│   ├── data_loader.py   # CSV loader
│   ├── generator.py     # Statistics & generation
│   └── recommender.py   # Crop recommender (singleton)
├── data/
│   ├── agroai.db        # SQLite database
│   └── Crop_recommendation.csv  # 2200 rows
├── run.py               # Mode A server
├── app.py               # Mode B Streamlit
└── main.py              # Mode B entry point
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS, no frameworks |
| Backend (Mode C) | FastAPI, uvicorn, CORS middleware |
| Data Science | SDV (CTGANSynthesizer), pandas, numpy |
| Database | SQLite (via built-in `sqlite3`) |
| ML Model | CTGAN (Generative Adversarial Network) |
| I18n | Custom engine, 3 languages (ar/fr/en) |
| Serving (Mode A) | ThreadingHTTPServer (non-blocking) |
| Serving (Mode B) | Streamlit |
| Cloud Storage | Cloudinary (for large generated datasets) |
