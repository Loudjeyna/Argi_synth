"""Data Layer — model_status singleton persistence."""

from typing import Optional
from synthai.data.database import Database


class ModelStatusRepository:
    """CRUD for the singleton `model_status` table (id=1)."""

    @staticmethod
    def set_trained(is_trained: bool = True, model_type: str = "CTGAN") -> None:
        conn = Database.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO model_status (id, is_trained, model_type, last_trained) "
            "VALUES (1, ?, ?, datetime('now'))",
            (1 if is_trained else 0, model_type),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def is_trained() -> bool:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT is_trained FROM model_status WHERE id = 1"
        ).fetchone()
        conn.close()
        return bool(row and row["is_trained"])

    @staticmethod
    def get_status() -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT * FROM model_status WHERE id = 1"
        ).fetchone()
        conn.close()
        return dict(row) if row else None
