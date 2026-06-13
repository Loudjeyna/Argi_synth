"""AI Core Layer — CSV loading and column-type inference (ports src/data_loader.py)."""

from pathlib import Path
from typing import Optional
import pandas as pd


class DataLoader:
    """Reads a CSV, infers column types for SDV compatibility."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self._data: Optional[pd.DataFrame] = None
        self._column_types: Optional[dict] = None

    def load(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        self._data = pd.read_csv(str(self.data_path))
        self._infer_column_types()
        return self._data

    def _infer_column_types(self) -> None:
        if self._data is None:
            return
        self._column_types = {}
        for col in self._data.columns:
            dtype = self._data[col].dtype
            if dtype == "object" or (
                dtype in ("int64", "float64") and self._data[col].nunique() <= 50
            ):
                self._column_types[col] = "categorical"
            else:
                self._column_types[col] = "numerical"

    def get_column_types(self) -> dict:
        return dict(self._column_types) if self._column_types else {}

    def get_transformed_column_types(self) -> dict:
        """Return types in SDV-compatible format."""
        return dict(self._column_types) if self._column_types else {}

    @property
    def data(self) -> Optional[pd.DataFrame]:
        return self._data

    def get_info(self) -> dict:
        if self._data is None:
            return {"shape": (0, 0)}
        return {
            "shape": list(self._data.shape),
            "columns": list(self._data.columns),
            "dtypes": {c: str(d) for c, d in self._data.dtypes.items()},
            "missing_values": int(self._data.isnull().sum().sum()),
            "unique_counts": {c: int(self._data[c].nunique()) for c in self._data.columns},
            "column_types": self.get_column_types(),
        }
