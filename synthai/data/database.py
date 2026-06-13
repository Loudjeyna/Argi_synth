"""Data Layer — SQLite connection management and schema initialisation."""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional

from synthai.data.config.settings import DB_PATH, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD


class Database:
    """Manages the SQLite connection and provides low-level helpers."""

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Return a new SQLite connection (row_factory = sqlite3.Row)."""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ── helpers ──────────────────────────────────────────────────────
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def now() -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # ── schema ───────────────────────────────────────────────────────
    @classmethod
    def init_db(cls) -> None:
        """Create all tables and seed the admin user."""
        os.makedirs(str(DB_PATH.parent), exist_ok=True)
        conn = cls.get_connection()
        c = conn.cursor()

        # ── 1. users ─────────────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                username       TEXT UNIQUE NOT NULL,
                email          TEXT UNIQUE NOT NULL,
                password_hash  TEXT NOT NULL,
                role           TEXT NOT NULL DEFAULT 'farmer',
                plan           TEXT NOT NULL DEFAULT 'free',
                is_active      INTEGER NOT NULL DEFAULT 1,
                attempts       INTEGER NOT NULL DEFAULT 0,
                last_reset_date TEXT,
                subscription_expires_at TEXT,
                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── 2. user_settings ─────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                setting_key   TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                UNIQUE(user_id, setting_key),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 3. sessions ──────────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                token      TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 4. crops ─────────────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en     TEXT UNIQUE NOT NULL,
                name_ar     TEXT,
                name_fr     TEXT,
                category    TEXT,
                is_algerian INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── 5. crop_requirements ─────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS crop_requirements (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id          INTEGER NOT NULL UNIQUE,
                n_min REAL,  n_max REAL,
                p_min REAL,  p_max REAL,
                k_min REAL,  k_max REAL,
                temperature_min REAL, temperature_max REAL,
                humidity_min    REAL, humidity_max    REAL,
                ph_min REAL,  ph_max REAL,
                rainfall_min    REAL, rainfall_max    REAL,
                water_level     TEXT,
                fertilizer_level TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
            )
        """)

        # ── 6. crop_recommendations ──────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS crop_recommendations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                input_data  TEXT NOT NULL,
                results     TEXT NOT NULL,
                top_crop_id INTEGER,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (top_crop_id) REFERENCES crops(id) ON DELETE SET NULL
            )
        """)

        # ── 7. soil_textures ─────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS soil_textures (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en           TEXT UNIQUE NOT NULL,
                name_ar           TEXT,
                name_fr           TEXT,
                om_min REAL,  om_max REAL,
                moisture_min REAL, moisture_max REAL,
                bulk_density      REAL,
                drainage          TEXT,
                nutrient_retention TEXT,
                created_at        TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── 8. weather_zones ─────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS weather_zones (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_key     TEXT UNIQUE NOT NULL,
                name_ar      TEXT,  name_fr      TEXT,
                temp_min REAL,  temp_max REAL,
                hum_min  REAL,  hum_max  REAL,
                precip_min REAL, precip_max REAL,
                wind_min  REAL,  wind_max  REAL,
                pressure_min REAL, pressure_max REAL,
                cloud_min REAL,  cloud_max REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── 9. models ────────────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id              INTEGER NOT NULL,
                name                 TEXT NOT NULL,
                status               TEXT NOT NULL DEFAULT 'in_progress',
                is_production        INTEGER NOT NULL DEFAULT 0,
                config_epochs        INTEGER NOT NULL DEFAULT 10,
                config_batch_size    INTEGER NOT NULL DEFAULT 32,
                config_learning_rate REAL NOT NULL DEFAULT 0.0002,
                dataset_file_name    TEXT,
                dataset_original_rows INTEGER DEFAULT 0,
                dataset_original_cols INTEGER DEFAULT 0,
                dataset_headers      TEXT,
                cleaning_report      TEXT,
                trained_model_path   TEXT,
                evaluation           TEXT,
                created_at           TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at           TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 10. model_versions ───────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS model_versions (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id             INTEGER NOT NULL,
                version_number       INTEGER NOT NULL,
                version_type         TEXT NOT NULL DEFAULT 'initial',
                status               TEXT NOT NULL DEFAULT 'in_progress',
                config_epochs        INTEGER NOT NULL DEFAULT 10,
                config_batch_size    INTEGER NOT NULL DEFAULT 32,
                config_learning_rate REAL NOT NULL DEFAULT 0.0002,
                dataset_file_name    TEXT,
                dataset_original_rows INTEGER DEFAULT 0,
                dataset_original_cols INTEGER DEFAULT 0,
                dataset_headers      TEXT,
                cleaning_report      TEXT,
                evaluation           TEXT,
                created_at           TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(model_id, version_number),
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
            )
        """)

        # ── 11. model_datasets ───────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS model_datasets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id    INTEGER NOT NULL,
                version_id  INTEGER,
                headers     TEXT NOT NULL,
                row_count   INTEGER NOT NULL DEFAULT 0,
                data_json   TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
                FOREIGN KEY (version_id) REFERENCES model_versions(id) ON DELETE SET NULL
            )
        """)

        # ── 12. generations ──────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id              INTEGER NOT NULL,
                model_id             INTEGER,
                model_version        INTEGER,
                dataset_type         TEXT NOT NULL,
                dataset_level        TEXT NOT NULL,
                rows_generated       INTEGER NOT NULL DEFAULT 1000,
                status               TEXT NOT NULL DEFAULT 'completed',
                headers              TEXT NOT NULL,
                preview_data         TEXT,
                full_data_stored     INTEGER NOT NULL DEFAULT 0,
                validation_report    TEXT,
                correlation_similarity REAL,
                file_url             TEXT,
                cloudinary_url       TEXT,
                created_at           TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
            )
        """)

        # ── 13. generation_data ──────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS generation_data (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id INTEGER NOT NULL UNIQUE,
                row_count     INTEGER NOT NULL DEFAULT 0,
                data_json     TEXT NOT NULL,
                file_path     TEXT,
                created_at    TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
            )
        """)

        # ── 14. augmentations ────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS augmentations (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id               INTEGER NOT NULL,
                file_name             TEXT NOT NULL,
                original_rows         INTEGER NOT NULL DEFAULT 0,
                augmented_rows        INTEGER NOT NULL DEFAULT 0,
                multiplier            INTEGER NOT NULL DEFAULT 2,
                dataset_type          TEXT,
                headers               TEXT NOT NULL,
                quality_score         INTEGER DEFAULT 0,
                quality_label         TEXT DEFAULT 'N/A',
                correlation_similarity REAL,
                original_stats        TEXT,
                augmented_stats       TEXT,
                preview_data          TEXT,
                created_at            TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 15. predictions ──────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                prediction_type TEXT NOT NULL,
                input_data      TEXT NOT NULL,
                output_result   TEXT NOT NULL,
                crop_search     TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 16. payments ─────────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                plan_id      TEXT NOT NULL,
                plan_name    TEXT NOT NULL,
                price        REAL NOT NULL DEFAULT 0,
                status       TEXT NOT NULL DEFAULT 'active',
                subscribed_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at   TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 17. usage_logs ───────────────────────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                action_type   TEXT NOT NULL DEFAULT 'generation',
                rows_affected INTEGER DEFAULT 0,
                created_at    TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── 18. model_status (singleton row) ─────────────────────────
        c.execute("""
            CREATE TABLE IF NOT EXISTS model_status (
                id          INTEGER PRIMARY KEY DEFAULT 1,
                is_trained  INTEGER NOT NULL DEFAULT 0,
                model_type  TEXT NOT NULL DEFAULT 'CTGAN',
                last_trained TEXT,
                CHECK (id = 1)
            )
        """)

        # ── Seed admin user ──────────────────────────────────────────
        c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (DEFAULT_ADMIN_USER,))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO users (username, email, password_hash, role, plan) VALUES (?, ?, ?, ?, ?)",
                (DEFAULT_ADMIN_USER, DEFAULT_ADMIN_EMAIL,
                 cls.hash_password(DEFAULT_ADMIN_PASSWORD), "admin", "premium"),
            )

        conn.commit()
        conn.close()
