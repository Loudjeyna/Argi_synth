"""AI Core Layer — synthetic data generation orchestration (ports src/generator.py)."""

from typing import Optional
import pandas as pd
from synthai.ai.models.ctgan import CTGANModel
from synthai.ai.evaluation.metrics import DataStatistics, DataComparison


class SyntheticDataGenerator:
    """Wraps a trained CTGANModel to generate, compare, and export synthetic data."""

    def __init__(self, model: CTGANModel):
        self._model = model
        self._real_data: Optional[pd.DataFrame] = None
        self._synthetic_data: Optional[pd.DataFrame] = None

    def set_real_data(self, df: pd.DataFrame) -> None:
        self._real_data = df.copy()

    def generate(self, num_rows: int, save_path: Optional[str] = None) -> pd.DataFrame:
        self._synthetic_data = self._model.generate(num_rows)
        if save_path:
            self._synthetic_data.to_csv(save_path, index=False)
        return self._synthetic_data

    # ── statistics ─────────────────────────────────────────────────────
    def get_statistics(self) -> dict:
        if self._real_data is None:
            return {}
        return {
            "descriptive": DataStatistics.compute_descriptive_stats(self._real_data),
            "correlation": DataStatistics.compute_correlation(self._real_data),
            "distribution": DataStatistics.compute_distribution_stats(self._real_data),
        }

    def get_synthetic_statistics(self) -> dict:
        if self._synthetic_data is None:
            return {}
        return {
            "descriptive": DataStatistics.compute_descriptive_stats(self._synthetic_data),
            "correlation": DataStatistics.compute_correlation(self._synthetic_data),
            "distribution": DataStatistics.compute_distribution_stats(self._synthetic_data),
        }

    def compare_datasets(self) -> dict:
        if self._real_data is None or self._synthetic_data is None:
            return {}
        return {
            "statistics_comparison": DataComparison.compare_statistics(
                self._real_data, self._synthetic_data
            ),
            "similarity_scores": DataComparison.compute_similarity_score(
                self._real_data, self._synthetic_data
            ),
        }

    # ── persistence ────────────────────────────────────────────────────
    def save_synthetic_data(self, path: str) -> None:
        if self._synthetic_data is not None:
            self._synthetic_data.to_csv(path, index=False)

    @property
    def real_data(self) -> Optional[pd.DataFrame]:
        return self._real_data

    @property
    def synthetic_data(self) -> Optional[pd.DataFrame]:
        return self._synthetic_data
