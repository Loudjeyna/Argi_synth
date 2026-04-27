import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any


class DataLoader:
    """Load and preprocess agricultural dataset for CTGAN training."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._column_types: Optional[Dict[str, str]] = None

    def load(self) -> pd.DataFrame:
        """Load dataset from CSV file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        self._df = pd.read_csv(self.data_path)
        self._infer_column_types()
        return self._df

    def _infer_column_types(self) -> None:
        """Infer SDV-compatible column types from DataFrame."""
        if self._df is None:
            return
        
        self._column_types = {}
        for col in self._df.columns:
            if self._df[col].dtype == 'object':
                self._column_types[col] = 'categorical'
            elif self._df[col].dtype in ['int64', 'float64']:
                if self._df[col].nunique() <= 50:
                    self._column_types[col] = 'categorical'
                else:
                    self._column_types[col] = 'numerical'

    def get_column_types(self) -> Dict[str, str]:
        """Return SDV-compatible column types."""
        if self._column_types is None:
            self._infer_column_types()
        return self._column_types

    def get_transformed_column_types(self) -> Dict[str, Any]:
        """Return properly formatted column types for SDV/CTGAN."""
        if self._df is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        sdtypes = {}
        for col in self._df.columns:
            dtype = str(self._df[col].dtype)
            if dtype == 'object':
                sdtypes[col] = 'categorical'
            elif dtype in ['int64', 'float64']:
                if self._df[col].nunique() <= 50:
                    sdtypes[col] = 'categorical'
                else:
                    sdtypes[col] = 'numerical'
        return sdtypes

    @property
    def data(self) -> pd.DataFrame:
        """Return loaded DataFrame."""
        if self._df is None:
            self.load()
        return self._df

    def get_info(self) -> Dict[str, Any]:
        """Get dataset information."""
        if self._df is None:
            self.load()
        
        return {
            'shape': self._df.shape,
            'columns': list(self._df.columns),
            'dtypes': self._df.dtypes.to_dict(),
            'missing_values': self._df.isnull().sum().to_dict(),
            'unique_counts': {col: self._df[col].nunique() for col in self._df.columns},
            'column_types': self.get_transformed_column_types()
        }