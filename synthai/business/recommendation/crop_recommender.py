"""Business Logic Layer — crop recommendation engine (ports src/recommender.py)."""

from typing import Optional
import pandas as pd
import numpy as np


class CropRecommender:
    """Scores crops against input conditions using Euclidean distance.

    Receits crop data via constructor (dependency injection) — no direct
    filesystem or database access.  The service layer is responsible for
    loading data via a repository and passing the DataFrame in.
    """

    def __init__(self, crop_df: Optional[pd.DataFrame] = None):
        self._df = crop_df

    @staticmethod
    def _determine_water_level(rainfall_mean: float) -> str:
        if rainfall_mean > 200:
            return "High"
        if rainfall_mean > 100:
            return "Medium"
        return "Low"

    @staticmethod
    def _determine_fertilizer_level(n: float, p: float, k: float) -> str:
        avg = (n + p + k) / 3
        if avg > 80:
            return "High"
        if avg > 40:
            return "Medium"
        return "Low"

    @property
    def data(self) -> pd.DataFrame:
        return self._df.copy() if self._df is not None else pd.DataFrame()

    def get_all_crops(self) -> list:
        return sorted(self._df["label"].unique().tolist()) if self._df is not None else []

    def get_crop_stats(self, crop: str) -> Optional[dict]:
        if self._df is None:
            return None
        subset = self._df[self._df["label"] == crop.lower()]
        if subset.empty:
            return None
        numeric = subset.select_dtypes(include=[np.number])
        stats = {
            "count": len(subset),
            "sample_data": subset.head(5).to_dict(orient="records"),
        }
        for col in numeric.columns:
            stats[col] = {
                "min": float(numeric[col].min()),
                "max": float(numeric[col].max()),
                "mean": float(numeric[col].mean()),
                "optimal_min": float(numeric[col].quantile(0.25)),
                "optimal_max": float(numeric[col].quantile(0.75)),
            }
        stats["water_level"] = self._determine_water_level(
            stats.get("rainfall", {}).get("mean", 0)
        )
        stats["fertilizer_level"] = self._determine_fertilizer_level(
            stats.get("N", {}).get("mean", 0),
            stats.get("P", {}).get("mean", 0),
            stats.get("K", {}).get("mean", 0),
        )
        return stats

    def get_recommendation(self, crop: str) -> Optional[dict]:
        stats = self.get_crop_stats(crop)
        if stats is None:
            return None
        rec = {"crop": crop.lower()}
        for field in ["temperature", "humidity", "ph", "rainfall", "N", "P", "K"]:
            if field in stats:
                rec[field] = {
                    "optimal_min": stats[field]["optimal_min"],
                    "optimal_max": stats[field]["optimal_max"],
                }
        rec["water_level"] = stats.get("water_level")
        rec["fertilizer_level"] = stats.get("fertilizer_level")
        return rec

    def get_all_recommendations(self) -> pd.DataFrame:
        rows = []
        for crop in self.get_all_crops():
            r = self.get_recommendation(crop)
            if r:
                rows.append(r)
        return pd.DataFrame(rows)

    def predict(self, conditions: dict) -> list:
        """Score all crops by Euclidean distance against input conditions.

        Returns top-5 crops sorted by match percentage.
        """
        if self._df is None:
            return []

        numeric_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        centroids = self._df.groupby("label")[numeric_cols].mean()

        input_vec = np.array([
            conditions.get(k, 0) for k in numeric_cols
        ], dtype=float)

        distances = np.sqrt(((centroids.values - input_vec) ** 2).sum(axis=1))
        max_dist = distances.max() or 1
        match_pcts = ((1 - distances / max_dist) * 100).clip(0, 100)

        results = []
        for idx in np.argsort(distances)[:5]:
            crop = centroids.index[idx]
            stats = self.get_crop_stats(crop)
            results.append({
                "crop": crop,
                "match_pct": round(float(match_pcts[idx]), 1),
                "water_level": stats.get("water_level", "Medium") if stats else "Medium",
                "fertilizer_level": stats.get("fertilizer_level", "Medium") if stats else "Medium",
            })

        return results
