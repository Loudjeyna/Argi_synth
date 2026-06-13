"""Dataset repository — CRUD for generations, generation_data, augmentations."""

import json
from typing import Optional
from synthai.data.database import Database


class DatasetRepository:
    """Persistence for `generations`, `generation_data`, and `augmentations`."""

    # ── generations ───────────────────────────────────────────────────
    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            """SELECT g.*, u.username AS admin_username
               FROM generations g JOIN users u ON g.user_id = u.id
               ORDER BY g.created_at DESC"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def find_by_id(gen_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM generations WHERE id = ?", (gen_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(data: dict) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            """INSERT INTO generations (user_id, model_id, model_version, dataset_type,
               dataset_level, rows_generated, status, headers, preview_data,
               full_data_stored, validation_report, correlation_similarity,
               file_url, cloudinary_url)
               VALUES (:user_id, :model_id, :model_version, :dataset_type,
               :dataset_level, :rows_generated, :status, :headers, :preview_data,
               :full_data_stored, :validation_report, :correlation_similarity,
               :file_url, :cloudinary_url)""",
            data,
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    # ── generation_data (full storage) ────────────────────────────────
    @staticmethod
    def store_full_data(generation_id: int, data_rows: list, file_path: str = None) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO generation_data (generation_id, row_count, data_json, file_path) "
            "VALUES (?, ?, ?, ?)",
            (generation_id, len(data_rows), json.dumps(data_rows), file_path),
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def find_full_data(generation_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT * FROM generation_data WHERE generation_id = ?", (generation_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    # ── augmentations ─────────────────────────────────────────────────
    @staticmethod
    def find_augmentations(user_id: int = None) -> list:
        conn = Database.get_connection()
        if user_id:
            rows = conn.execute(
                "SELECT * FROM augmentations WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM augmentations ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def find_augmentation_by_id(aug_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM augmentations WHERE id = ?", (aug_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_augmentation(data: dict) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            """INSERT INTO augmentations (user_id, file_name, original_rows, augmented_rows,
               multiplier, dataset_type, headers, quality_score, quality_label,
               correlation_similarity, original_stats, augmented_stats, preview_data)
               VALUES (:user_id, :file_name, :original_rows, :augmented_rows,
               :multiplier, :dataset_type, :headers, :quality_score, :quality_label,
               :correlation_similarity, :original_stats, :augmented_stats, :preview_data)""",
            data,
        )
        conn.commit()
        conn.close()
        return c.lastrowid
