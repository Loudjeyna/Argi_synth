"""Prediction & recommendation repository — CRUD for predictions and crop_recommendations."""

from typing import Optional
from synthai.data.database import Database


class PredictionRepository:
    """Persistence for `predictions` and `crop_recommendations` tables."""

    # ── predictions ───────────────────────────────────────────────────
    @staticmethod
    def find_by_user(user_id: int, limit: int = 100) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(user_id: int, ptype: str, input_data: str, output_result: str, crop_search: str = None) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO predictions (user_id, prediction_type, input_data, output_result, crop_search) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, ptype, input_data, output_result, crop_search),
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def search_by_crop(user_id: int, crop: str) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT * FROM predictions WHERE user_id = ? AND crop_search LIKE ? ORDER BY created_at DESC LIMIT 50",
            (user_id, f"%{crop}%"),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def search_by_date(user_id: int, date_prefix: str) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT * FROM predictions WHERE user_id = ? AND created_at LIKE ? ORDER BY created_at DESC",
            (user_id, f"{date_prefix}%"),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def count_by_user(user_id: int) -> int:
        conn = Database.get_connection()
        row = conn.execute("SELECT COUNT(*) AS cnt FROM predictions WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        return row["cnt"]

    # ── crop_recommendations ──────────────────────────────────────────
    @staticmethod
    def find_recommendations(user_id: int, limit: int = 20) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            """SELECT cr.*, c.name_en AS top_crop_name
               FROM crop_recommendations cr
               LEFT JOIN crops c ON cr.top_crop_id = c.id
               WHERE cr.user_id = ?
               ORDER BY cr.created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create_recommendation(user_id: int, input_data: str, results: str, top_crop_id: int = None) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO crop_recommendations (user_id, input_data, results, top_crop_id) VALUES (?, ?, ?, ?)",
            (user_id, input_data, results, top_crop_id),
        )
        conn.commit()
        conn.close()
        return c.lastrowid
