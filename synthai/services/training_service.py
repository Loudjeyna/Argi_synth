"""Service Layer — model training workflow."""

from typing import Optional
import pandas as pd

from synthai.ai.models.ctgan import CTGANModel
from synthai.ai.preprocessing.data_loader import DataLoader
from synthai.ai.generation.generator import SyntheticDataGenerator
from synthai.data.repositories.model_repository import ModelRepository
from synthai.data.repositories.model_status_repository import ModelStatusRepository
from synthai.data.repositories.payment_repository import UsageLogRepository
from synthai.data.config.settings import CROP_CSV_PATH


class TrainingService:
    """Coordinates training: DataLoader → CTGANModel → SyntheticDataGenerator → persistence."""

    def __init__(self):
        self._model: Optional[CTGANModel] = None
        self._generator: Optional[SyntheticDataGenerator] = None
        self._real_df: Optional[pd.DataFrame] = None

    def train(self, user_id: int, epochs: int = 300, batch_size: int = 256) -> dict:
        loader = DataLoader(str(CROP_CSV_PATH))
        self._real_df = loader.load()
        self._model = CTGANModel(epochs=epochs, batch_size=batch_size)
        result = self._model.train(self._real_df)
        self._generator = SyntheticDataGenerator(self._model)
        self._generator.set_real_data(self._real_df)

        ModelStatusRepository.set_trained(True, "CTGAN")
        UsageLogRepository.add(user_id, "training")
        return result

    def is_trained(self) -> bool:
        return ModelStatusRepository.is_trained()

    def get_generator(self) -> Optional[SyntheticDataGenerator]:
        return self._generator

    def get_real_data(self) -> Optional[pd.DataFrame]:
        return self._real_df
