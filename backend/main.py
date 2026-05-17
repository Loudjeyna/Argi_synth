"""
SynthAI FastAPI Backend Server
Wraps src/ CTGAN modules with REST API endpoints for training, generation, and validation.
"""
import sys
import os
from pathlib import Path

# Force single-threaded joblib to avoid pickling issues in FastAPI thread pool
os.environ['JOBLIB_SINGLE_THREADED'] = '1'
os.environ['LOKY_MAX_CPU_COUNT'] = '1'

# Add src directory to Python path so imports work
_src = str(Path(__file__).resolve().parent.parent / 'src')
if _src not in sys.path:
    sys.path.insert(0, _src)

# Ensure working directory is project root for relative paths in src/database.py
os.chdir(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import pandas as pd
import uuid
import threading
import logging
import json

from database import Database
from data_loader import DataLoader
from ctgan_model import CTGANModel
from generator import SyntheticDataGenerator, DataStatistics, DataComparison

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "Crop_recommendation.csv"
GENERATED_DIR = PROJECT_ROOT / "backend" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# Initialize DB & seed admin user
Database.init_db()
try:
    Database.add_user("admin", "admin@agroai.com", "admin123", "admin")
except Exception:
    pass

app = FastAPI(title="SynthAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state: model, generator, real data
_model_lock = threading.Lock()
_ctgan: Optional[CTGANModel] = None
_generator: Optional[SyntheticDataGenerator] = None
_real_df: Optional[pd.DataFrame] = None


# ===================== Pydantic Models =====================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "farmer"

class TrainRequest(BaseModel):
    epochs: int = 300
    batch_size: int = 256

class GenerateRequest(BaseModel):
    num_rows: int = 1000


# ===================== Auth Routes =====================

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = Database.authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user": user}

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    ok = Database.add_user(req.username, req.email, req.password, req.role)
    if not ok:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"success": True}

@app.get("/api/users")
def list_users():
    rows = Database.get_all_users()
    return [
        {"id": r[0], "username": r[1], "email": r[2], "role": r[3], "plan": r[4], "created_at": r[5]}
        for r in rows
    ]


# ===================== Model Routes =====================

@app.post("/api/model/train")
def train_model(req: TrainRequest):
    global _ctgan, _generator, _real_df
    with _model_lock:
        if not DATA_FILE.exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {DATA_FILE}")
        try:
            loader = DataLoader(str(DATA_FILE))
            _real_df = loader.load()
            _ctgan = CTGANModel(epochs=req.epochs, batch_size=req.batch_size)
            _ctgan.train(_real_df)
            _generator = SyntheticDataGenerator(_ctgan)
            _generator.set_real_data(_real_df)
            Database.set_model_trained(True, "CTGAN")
            logger.info("Model trained successfully (%d epochs)", req.epochs)
            return {"status": "success", "epochs": req.epochs, "model_type": "CTGAN"}
        except Exception as e:
            logger.error("Training failed: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model/status")
def model_status():
    trained, model_type = Database.is_model_trained()
    return {"is_trained": trained, "model_type": model_type}


# ===================== Generation Routes =====================

@app.post("/api/generate")
def generate_data(req: GenerateRequest):
    global _generator
    if not _ctgan or not _ctgan.is_trained:
        raise HTTPException(status_code=400, detail="Model not trained. Call /api/model/train first.")
    with _model_lock:
        if _generator is None:
            raise HTTPException(status_code=400, detail="Generator not initialised")
        try:
            df = _generator.generate(req.num_rows)
            ds_id = uuid.uuid4().hex[:8]
            csv_path = GENERATED_DIR / f"dataset_{ds_id}.csv"
            _generator.save_synthetic_data(str(csv_path))
            admin = Database.authenticate("admin", "admin123")
            if admin:
                Database.add_synthetic_dataset(admin["id"], req.num_rows, str(csv_path))
            comparison = _generator.compare_datasets()
            return {
                "dataset_id": ds_id,
                "num_rows": req.num_rows,
                "file_path": str(csv_path),
                "columns": list(df.columns),
                "preview": json.loads(df.head(50).to_json(orient="records")),
                "similarity_scores": comparison["similarity_scores"],
                "generated_at": pd.Timestamp.now().isoformat()
            }
        except Exception as e:
            logger.error("Generation failed: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets")
def list_datasets():
    return Database.get_all_datasets()

@app.get("/api/validate/{dataset_id}")
def validate_dataset(dataset_id: str):
    csv_path = GENERATED_DIR / f"dataset_{dataset_id}.csv"
    if not csv_path.exists():
        datasets = Database.get_all_datasets()
        for ds in datasets:
            if str(ds.get("id")) == dataset_id and ds.get("file_path"):
                csv_path = Path(ds["file_path"])
                break
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        synth = pd.read_csv(str(csv_path))
        loader = DataLoader(str(DATA_FILE))
        real = loader.load()
        sim = DataComparison.compute_similarity_score(real, synth)
        cmp_df = DataComparison.compare_statistics(real, synth)
        real_corr = DataStatistics.compute_correlation(real)
        synth_corr = DataStatistics.compute_correlation(synth)
        real_dist = DataStatistics.compute_distribution_stats(real)
        synth_dist = DataStatistics.compute_distribution_stats(synth)
        return {
            "dataset_id": dataset_id,
            "num_rows": len(synth),
            "similarity_scores": sim,
            "statistics_comparison": json.loads(cmp_df.to_json(orient="index")) if not cmp_df.empty else {},
            "real_distribution": _dist_json(real_dist),
            "synthetic_distribution": _dist_json(synth_dist),
            "real_correlation": json.loads(real_corr.to_json()) if not real_corr.empty else {},
            "synthetic_correlation": json.loads(synth_corr.to_json()) if not synth_corr.empty else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Stats =====================

@app.get("/api/stats")
def stats():
    datasets = Database.get_all_datasets()
    total_rows = sum(d["rows_generated"] for d in datasets)
    trained, mtype = Database.is_model_trained()
    return {
        "total_datasets": len(datasets),
        "total_rows": total_rows,
        "total_users": len(Database.get_all_users()),
        "model_trained": trained,
        "model_type": mtype,
        "last_generated": datasets[0]["created_at"] if datasets else None
    }


# ===================== Health =====================

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# ===================== Helpers =====================

def _dist_json(dist):
    result = {}
    for col, col_stats in dist.items():
        result[col] = {}
        for k, v in col_stats.items():
            if isinstance(v, (pd.Series, pd.DataFrame)):
                result[col][k] = json.loads(v.to_json())
            else:
                try:
                    json.dumps(v)
                    result[col][k] = v
                except (TypeError, ValueError):
                    result[col][k] = str(v)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
