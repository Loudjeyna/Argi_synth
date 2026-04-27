"""
Synthetic Agricultural Data Generator using CTGAN

This application demonstrates:
1. Loading real agricultural dataset
2. Training CTGAN model for synthetic data generation
3. Generating synthetic crop recommendation data
4. Visualizing statistics and comparisons
5. Exporting generated data as CSV
"""

__version__ = "1.0.0"
__author__ = "Agricultural AI Team"
__description__ = "Generate synthetic agricultural data using CTGAN"

from .data_loader import DataLoader
from .ctgan_model import CTGANModel, TVAEModel
from .generator import SyntheticDataGenerator, DataStatistics, DataComparison

__all__ = [
    "DataLoader",
    "CTGANModel",
    "TVAEModel",
    "SyntheticDataGenerator",
    "DataStatistics",
    "DataComparison",
]