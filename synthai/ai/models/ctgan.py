"""AI Core Layer — CTGAN model wrapper (ports src/ctgan_model.py)."""

import os
import threading
from typing import Optional, Tuple

import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer

from synthai.data.config.settings import (
    CTGAN_DEFAULT_EMBEDDING_DIM,
    CTGAN_DEFAULT_GENERATOR_DIM,
    CTGAN_DEFAULT_DISCRIMINATOR_DIM,
    CTGAN_DEFAULT_GENERATOR_LR,
    CTGAN_DEFAULT_DISCRIMINATOR_LR,
    CTGAN_PAC,
)


class CTGANModel:
    """Wraps SDV's CTGANSynthesizer with lifecycle management."""

    def __init__(
        self,
        epochs: int = 300,
        batch_size: int = 256,
        embedding_dim: int = CTGAN_DEFAULT_EMBEDDING_DIM,
        generator_dim: Tuple[int, int] = CTGAN_DEFAULT_GENERATOR_DIM,
        discriminator_dim: Tuple[int, int] = CTGAN_DEFAULT_DISCRIMINATOR_DIM,
        generator_lr: float = CTGAN_DEFAULT_GENERATOR_LR,
        discriminator_lr: float = CTGAN_DEFAULT_DISCRIMINATOR_LR,
        verbose: bool = True,
    ):
        self.epochs = epochs
        self.batch_size = self._adjust_batch_size(batch_size, CTGAN_PAC)
        self.embedding_dim = embedding_dim
        self.generator_dim = generator_dim
        self.discriminator_dim = discriminator_dim
        self.generator_lr = generator_lr
        self.discriminator_lr = discriminator_lr
        self.verbose = verbose
        self._model: Optional[CTGANSynthesizer] = None
        self._is_trained = False
        self._lock = threading.Lock()

    # ── metadata helpers ───────────────────────────────────────────────
    @staticmethod
    def _create_metadata(df: pd.DataFrame) -> SingleTableMetadata:
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(df)
        return metadata

    @staticmethod
    def _adjust_batch_size(batch_size: int, pac: int = CTGAN_PAC) -> int:
        if batch_size < pac:
            return pac
        remainder = batch_size % pac
        if remainder != 0:
            batch_size += pac - remainder
        return batch_size

    # ── lifecycle ──────────────────────────────────────────────────────
    def train(self, df: pd.DataFrame) -> dict:
        """Train the CTGAN model on the given DataFrame."""
        with self._lock:
            # single-threaded SDV requirement
            os.environ["JOBLIB_SINGLE_THREADED"] = "1"
            os.environ["LOKY_MAX_CPU_COUNT"] = "1"

            metadata = self._create_metadata(df)
            self._model = CTGANSynthesizer(
                metadata,
                epochs=self.epochs,
                batch_size=self.batch_size,
                embedding_dim=self.embedding_dim,
                generator_dim=self.generator_dim,
                discriminator_dim=self.discriminator_dim,
                generator_lr=self.generator_lr,
                discriminator_lr=self.discriminator_lr,
                enforce_min_max_values=True,
                enforce_rounding=True,
                verbose=self.verbose,
            )
            self._model.fit(df)
            self._is_trained = True

            return {
                "status": "success",
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "model_type": "CTGAN",
            }

    def generate(self, num_rows: int) -> pd.DataFrame:
        """Sample synthetic data from the trained model."""
        if not self._is_trained or self._model is None:
            raise RuntimeError("Model must be trained before generation.")
        return self._model.sample(num_rows)

    def save(self, path: str) -> None:
        if self._model is None:
            raise RuntimeError("No model to save.")
        self._model.save(path)

    def load(self, path: str) -> None:
        self._model = CTGANSynthesizer.load(path)
        self._is_trained = True

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    @property
    def model_type(self) -> str:
        return "CTGAN"
