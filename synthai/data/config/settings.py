"""Application-wide paths, defaults, and constants."""

import os
from pathlib import Path

# ── Project root ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # SynthAI/

# ── Data paths ────────────────────────────────────────────────
DATA_DIR = PROJECT_ROOT / "data"
DATASETS_DIR = DATA_DIR / "datasets"
DB_PATH = DATA_DIR / "agroai.db"
CROP_CSV_PATH = DATA_DIR / "Crop_recommendation.csv"

# ── Backend generated CSV output ──────────────────────────────
GENERATED_DIR = PROJECT_ROOT / "data" / "generated"

# ── Defaults ──────────────────────────────────────────────────
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_EMAIL = "admin@synthai.com"

# ── CTGAN defaults ────────────────────────────────────────────
CTGAN_DEFAULT_EPOCHS = 300
CTGAN_DEFAULT_BATCH_SIZE = 256
CTGAN_DEFAULT_EMBEDDING_DIM = 128
CTGAN_DEFAULT_GENERATOR_DIM = (256, 256)
CTGAN_DEFAULT_DISCRIMINATOR_DIM = (256, 256)
CTGAN_DEFAULT_GENERATOR_LR = 0.0002
CTGAN_DEFAULT_DISCRIMINATOR_LR = 0.0002
CTGAN_PAC = 10  # batches must be divisible by this

# ── Dataset sizes ─────────────────────────────────────────────
DATASET_SIZES = {
    "medium": 1_000,
    "large": 10_000,
    "bigdata": 100_000,
}

DATASET_TYPES = ["crop", "soil", "weather"]

ROLES = ["admin", "farmer", "company"]

# ── Ensures required directories exist ────────────────────────
def ensure_dirs() -> None:
    """Create required directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
