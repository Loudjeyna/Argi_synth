"""Crop repository — read-only lookup for crops, crop_requirements, soil_textures, weather_zones."""

from typing import Optional
from synthai.data.database import Database


class CropRepository:
    """Persistence for `crops` and `crop_requirements` tables."""

    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute("SELECT * FROM crops ORDER BY name_en ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def find_by_id(crop_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM crops WHERE id = ?", (crop_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_by_name_en(name_en: str) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM crops WHERE name_en = ?", (name_en,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_requirements(crop_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute("SELECT * FROM crop_requirements WHERE crop_id = ?", (crop_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_requirements_with_crop(crop_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            """SELECT c.*, r.* FROM crops c
               LEFT JOIN crop_requirements r ON r.crop_id = c.id
               WHERE c.id = ?""",
            (crop_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_all_with_requirements() -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            """SELECT c.id, c.name_en, c.name_ar, c.name_fr, c.category, c.is_algerian,
               r.* FROM crops c
               LEFT JOIN crop_requirements r ON r.crop_id = c.id
               ORDER BY c.name_en ASC"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class SoilRepository:
    """Persistence for `soil_textures`."""

    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute("SELECT * FROM soil_textures ORDER BY name_en ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class WeatherRepository:
    """Persistence for `weather_zones`."""

    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute("SELECT * FROM weather_zones ORDER BY zone_key ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
