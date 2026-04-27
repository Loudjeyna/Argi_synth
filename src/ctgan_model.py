from sdv.single_table import CTGANSynthesizer
from sdv.metadata import SingleTableMetadata
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import pickle
import warnings


class CTGANModel:
    """CTGAN model wrapper for synthetic data generation (CTGAN ONLY)."""

    def __init__(
        self,
        epochs: int = 300,
        batch_size: int = 256,
        embedding_dim: int = 128,
        generator_dim: tuple = (256, 256),
        discriminator_dim: tuple = (256, 256),
        generator_lr: float = 0.0002,
        discriminator_lr: float = 0.0002,
        verbose: bool = True
    ):
        self.epochs = epochs
        self.batch_size = batch_size
        self.embedding_dim = embedding_dim
        self.generator_dim = generator_dim
        self.discriminator_dim = discriminator_dim
        self.generator_lr = generator_lr
        self.discriminator_lr = discriminator_lr
        self.verbose = verbose
        
        self._model: Optional[CTGANSynthesizer] = None
        self._metadata: Optional[SingleTableMetadata] = None
        self._is_trained = False

    def _create_metadata(self, df: pd.DataFrame) -> SingleTableMetadata:
        """Create SDV metadata from DataFrame."""
        warnings.filterwarnings('ignore', category=FutureWarning)
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(df)
        return metadata

    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train CTGAN model on provided DataFrame (CTGAN ONLY)."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            self._metadata = self._create_metadata(df)
        
        import os
        original_val = os.environ.get('JOBLIB_SINGLE_THREADED', '0')
        os.environ['JOBLIB_SINGLE_THREADED'] = '1'
        
        try:
            self._model = CTGANSynthesizer(
                metadata=self._metadata,
                enforce_min_max_values=True,
                enforce_rounding=True,
                epochs=self.epochs,
                batch_size=self.batch_size,
                embedding_dim=self.embedding_dim,
                generator_dim=self.generator_dim,
                discriminator_dim=self.discriminator_dim,
                generator_lr=self.generator_lr,
                discriminator_lr=self.discriminator_lr,
                verbose=self.verbose
            )
            
            self._model.fit(df)
            self._is_trained = True
        finally:
            os.environ['JOBLIB_SINGLE_THREADED'] = original_val
        
        return {
            'status': 'success',
            'epochs': self.epochs,
            'model_type': 'CTGAN',
            'metadata': self._metadata
        }

    def generate(self, num_rows: int) -> pd.DataFrame:
        """Generate synthetic data."""
        if not self._is_trained or self._model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self._model.sample(num_rows)

    def save(self, path: str) -> None:
        """Save trained model to disk using SDV built-in method."""
        if not self._is_trained or self._model is None:
            raise ValueError("No trained model to save.")
        
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._model.save(filepath=str(save_path))

    def load(self, path: str) -> None:
        """Load trained model from disk using SDV built-in method."""
        load_path = Path(path)
        
        if not load_path.exists():
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        self._model = CTGANSynthesizer.load(filepath=str(load_path))
        self._is_trained = True

    @property
    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self._is_trained
    
    @property
    def model_type(self) -> str:
        """Return the type of model."""
        return 'CTGAN'