"""Data Layer — read-only CSV-based crop data repository."""

from typing import Optional
import pandas as pd

from synthai.data.config.settings import CROP_CSV_PATH


class CropDataRepository:
    """Reads the reference crop dataset from CSV and returns DataFrames.

    This repository isolates filesystem access for crop data, keeping the
    business layer free of storage concerns.
    """

    @staticmethod
    def load_all() -> pd.DataFrame:
        if not CROP_CSV_PATH.exists():
            raise FileNotFoundError(f"Crop data not found: {CROP_CSV_PATH}")
        df = pd.read_csv(str(CROP_CSV_PATH))
        df["label"] = df["label"].str.lower()
        return df

    @staticmethod
    def count_rows() -> int:
        df = CropDataRepository.load_all()
        return len(df)

    @staticmethod
    def get_crop_names() -> list:
        df = CropDataRepository.load_all()
        return sorted(df["label"].unique().tolist())
