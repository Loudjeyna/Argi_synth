"""Model repository — CRUD for models, versions, and their datasets."""

import json
from typing import Optional
from synthai.data.database import Database


class ModelRepository:
    """Persistence for the `models`, `model_versions`, and `model_datasets` tables."""

    # ── models ────────────────────────────────────────────────────────
    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute("SELECT * FROM models ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def find_by_id(model_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(data: dict) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            """INSERT INTO models (user_id, name, status, config_epochs, config_batch_size,
               config_learning_rate, dataset_file_name, dataset_original_rows,
               dataset_original_cols, dataset_headers, cleaning_report)
               VALUES (:user_id, :name, :status, :config_epochs, :config_batch_size,
               :config_learning_rate, :dataset_file_name, :dataset_original_rows,
               :dataset_original_cols, :dataset_headers, :cleaning_report)""",
            data,
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def update(model_id: int, updates: dict) -> bool:
        if not updates:
            return True
        sets = ", ".join(f"{k} = :{k}" for k in updates)
        updates["id"] = model_id
        conn = Database.get_connection()
        conn.execute(f"UPDATE models SET {sets}, updated_at = datetime('now') WHERE id = :id", updates)
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(model_id: int) -> None:
        conn = Database.get_connection()
        conn.execute("DELETE FROM models WHERE id = ?", (model_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def find_production() -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM models WHERE is_production = 1 LIMIT 1").fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def set_production(model_id: int) -> None:
        conn = Database.get_connection()
        conn.execute("UPDATE models SET is_production = 0")
        conn.execute("UPDATE models SET is_production = 1 WHERE id = ?", (model_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def unset_production() -> None:
        conn = Database.get_connection()
        conn.execute("UPDATE models SET is_production = 0")
        conn.commit()
        conn.close()

    # ── model_versions ────────────────────────────────────────────────
    @staticmethod
    def find_versions(model_id: int) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT * FROM model_versions WHERE model_id = ? ORDER BY version_number ASC",
            (model_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create_version(data: dict) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            """INSERT INTO model_versions (model_id, version_number, version_type, status,
               config_epochs, config_batch_size, config_learning_rate,
               dataset_file_name, dataset_original_rows, dataset_original_cols,
               dataset_headers, cleaning_report, evaluation)
               VALUES (:model_id, :version_number, :version_type, :status,
               :config_epochs, :config_batch_size, :config_learning_rate,
               :dataset_file_name, :dataset_original_rows, :dataset_original_cols,
               :dataset_headers, :cleaning_report, :evaluation)""",
            data,
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    # ── model_datasets ────────────────────────────────────────────────
    @staticmethod
    def save_dataset(model_id: int, headers: list, rows: list, version_id: int = None) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO model_datasets (model_id, version_id, headers, row_count, data_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (model_id, version_id, json.dumps(headers), len(rows), json.dumps(rows)),
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def find_dataset(model_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT * FROM model_datasets WHERE model_id = ? ORDER BY id DESC LIMIT 1",
            (model_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None
