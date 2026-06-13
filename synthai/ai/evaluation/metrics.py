"""AI Core Layer — statistics and comparison utilities (ports src/generator.py)."""

import pandas as pd
import numpy as np


class DataStatistics:
    """Descriptive, distribution, and correlation stats for DataFrames."""

    @staticmethod
    def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
        numeric = df.select_dtypes(include=[np.number])
        stats = numeric.describe().T
        stats["range"] = stats["max"] - stats["min"]
        stats["variance"] = numeric.var()
        stats["median"] = numeric.median()
        return stats[["count", "mean", "std", "median", "min", "max", "range", "variance"]]

    @staticmethod
    def compute_correlation(df: pd.DataFrame) -> pd.DataFrame:
        numeric = df.select_dtypes(include=[np.number])
        if numeric.shape[1] < 2:
            return pd.DataFrame()
        return numeric.corr(method="pearson")

    @staticmethod
    def compute_distribution_stats(df: pd.DataFrame) -> dict:
        result = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                s = df[col].dropna()
                result[col] = {
                    "mean": float(s.mean()),
                    "std": float(s.std()),
                    "q25": float(s.quantile(0.25)),
                    "q50": float(s.median()),
                    "q75": float(s.quantile(0.75)),
                    "skewness": float(s.skew()),
                    "kurtosis": float(s.kurtosis()),
                }
            else:
                vc = df[col].value_counts()
                result[col] = {
                    "unique_count": int(df[col].nunique()),
                    "most_common": str(vc.index[0]) if len(vc) else "",
                    "value_counts": vc.head(10).to_dict(),
                }
        return result


class DataComparison:
    """Compare real vs. synthetic DataFrames."""

    @staticmethod
    def compare_statistics(real: pd.DataFrame, synth: pd.DataFrame) -> pd.DataFrame:
        real_stats = DataStatistics.compute_descriptive_stats(real)
        synth_stats = DataStatistics.compute_descriptive_stats(synth)
        comparison = pd.DataFrame(index=real_stats.index)
        comparison["Real Mean"] = real_stats["mean"]
        comparison["Synthetic Mean"] = synth_stats["mean"]
        comparison["Mean Diff (%)"] = (
            (comparison["Synthetic Mean"] - comparison["Real Mean"]).abs()
            / comparison["Real Mean"].replace(0, 1)
            * 100
        )
        comparison["Real Std"] = real_stats["std"]
        comparison["Synthetic Std"] = synth_stats["std"]
        comparison["Std Diff (%)"] = (
            (comparison["Synthetic Std"] - comparison["Real Std"]).abs()
            / comparison["Real Std"].replace(0, 1)
            * 100
        )
        return comparison

    @staticmethod
    def compute_similarity_score(real: pd.DataFrame, synth: pd.DataFrame) -> dict:
        comparison = DataComparison.compare_statistics(real, synth)
        scores = {}
        for col in comparison.index:
            mean_diff = comparison.loc[col, "Mean Diff (%)"]
            std_diff = comparison.loc[col, "Std Diff (%)"]
            col_score = max(0.0, 100.0 - (mean_diff + std_diff))
            scores[col] = round(col_score, 2)
        overall = round(sum(scores.values()) / len(scores), 2) if scores else 0.0
        return {
            "per_column": scores,
            "overall": overall,
        }
