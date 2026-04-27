import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path


class DataStatistics:
    """Compute statistics for real and synthetic datasets."""

    @staticmethod
    def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
        """Compute mean, std, min, max for numerical columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return pd.DataFrame()
        
        stats = df[numeric_cols].describe().T
        stats['median'] = df[numeric_cols].median()
        stats['variance'] = df[numeric_cols].var()
        stats['range'] = stats['max'] - stats['min']
        return stats[['count', 'mean', 'std', 'median', 'min', 'max', 'range', 'variance']]

    @staticmethod
    def compute_correlation(df: pd.DataFrame) -> pd.DataFrame:
        """Compute correlation matrix for numerical columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return pd.DataFrame()
        return numeric_df.corr()

    @staticmethod
    def compute_distribution_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Compute distribution statistics for each column."""
        stats = {}
        for col in df.columns:
            col_stats = {}
            if df[col].dtype in [np.int64, np.float64]:
                col_stats['mean'] = float(df[col].mean())
                col_stats['std'] = float(df[col].std())
                col_stats['q25'] = float(df[col].quantile(0.25))
                col_stats['q50'] = float(df[col].quantile(0.50))
                col_stats['q75'] = float(df[col].quantile(0.75))
                col_stats['skewness'] = float(df[col].skew())
                col_stats['kurtosis'] = float(df[col].kurtosis())
            else:
                col_stats['unique_count'] = int(df[col].nunique())
                col_stats['most_common'] = str(df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A')
                col_stats['value_counts'] = df[col].value_counts().head(5).to_dict()
            stats[col] = col_stats
        return stats


class DataComparison:
    """Compare real and synthetic datasets."""

    @staticmethod
    def compare_statistics(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> pd.DataFrame:
        """Compare statistics between real and synthetic data."""
        real_stats = DataStatistics.compute_descriptive_stats(real_df)
        synth_stats = DataStatistics.compute_descriptive_stats(synthetic_df)
        
        if real_stats.empty or synth_stats.empty:
            return pd.DataFrame()
        
        comparison = pd.DataFrame({
            'Real Mean': real_stats['mean'],
            'Synthetic Mean': synth_stats['mean'],
            'Mean Diff (%)': ((synth_stats['mean'] - real_stats['mean']) / real_stats['mean'] * 100).round(2),
            'Real Std': real_stats['std'],
            'Synthetic Std': synth_stats['std'],
            'Std Diff (%)': ((synth_stats['std'] - real_stats['std']) / real_stats['std'] * 100).round(2),
        })
        return comparison

    @staticmethod
    def compute_similarity_score(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> Dict[str, float]:
        """Compute overall similarity scores between datasets."""
        scores = {}
        numeric_cols = real_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            real_mean, synth_mean = real_df[col].mean(), synthetic_df[col].mean()
            real_std, synth_std = real_df[col].std(), synthetic_df[col].std()
            
            mean_diff = abs(real_mean - synth_mean) / (real_mean + 1e-10)
            std_diff = abs(real_std - synth_std) / (real_std + 1e-10)
            
            scores[col] = float(max(0, 100 - (mean_diff + std_diff) * 100))
        
        scores['overall'] = float(np.mean(list(scores.values())))
        return scores


class SyntheticDataGenerator:
    """Main class for generating synthetic agricultural data."""

    def __init__(self, model):
        self.model = model
        self._real_data: Optional[pd.DataFrame] = None
        self._synthetic_data: Optional[pd.DataFrame] = None
        self._last_generation_params: Optional[Dict[str, Any]] = None

    def set_real_data(self, df: pd.DataFrame) -> None:
        """Set the real dataset."""
        self._real_data = df.copy()

    def generate(self, num_rows: int, save_path: Optional[str] = None) -> pd.DataFrame:
        """Generate synthetic data."""
        if not self.model.is_trained:
            raise ValueError("Model not trained. Train the model first.")
        
        self._synthetic_data = self.model.generate(num_rows)
        self._last_generation_params = {'num_rows': num_rows}
        
        if save_path:
            self._save_to_csv(save_path)
        
        return self._synthetic_data

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for real data."""
        if self._real_data is None:
            raise ValueError("No real data set. Load data first.")
        
        return {
            'descriptive': DataStatistics.compute_descriptive_stats(self._real_data),
            'correlation': DataStatistics.compute_correlation(self._real_data),
            'distribution': DataStatistics.compute_distribution_stats(self._real_data)
        }

    def get_synthetic_statistics(self) -> Dict[str, Any]:
        """Get statistics for synthetic data."""
        if self._synthetic_data is None:
            raise ValueError("No synthetic data generated. Generate data first.")
        
        return {
            'descriptive': DataStatistics.compute_descriptive_stats(self._synthetic_data),
            'correlation': DataStatistics.compute_correlation(self._synthetic_data),
            'distribution': DataStatistics.compute_distribution_stats(self._synthetic_data)
        }

    def compare_datasets(self) -> Dict[str, Any]:
        """Compare real and synthetic datasets."""
        if self._real_data is None or self._synthetic_data is None:
            raise ValueError("Both real and synthetic data must be available.")
        
        return {
            'statistics_comparison': DataComparison.compare_statistics(
                self._real_data, self._synthetic_data
            ),
            'similarity_scores': DataComparison.compute_similarity_score(
                self._real_data, self._synthetic_data
            )
        }

    def save_synthetic_data(self, path: str) -> str:
        """Save synthetic data to CSV file."""
        if self._synthetic_data is None:
            raise ValueError("No synthetic data to save.")
        
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._synthetic_data.to_csv(save_path, index=False)
        return str(save_path.absolute())

    def get_data(self, data_type: str = 'synthetic') -> Optional[pd.DataFrame]:
        """Get loaded data."""
        if data_type == 'real':
            return self._real_data
        elif data_type == 'synthetic':
            return self._synthetic_data
        return None

    @property
    def real_data(self) -> Optional[pd.DataFrame]:
        return self._real_data

    @property
    def synthetic_data(self) -> Optional[pd.DataFrame]:
        return self._synthetic_data