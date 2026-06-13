"""Service Layer — dataset read operations."""

from typing import Optional

from synthai.data.repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Coordinates dataset read operations — wraps DatasetRepository for the API layer."""

    @staticmethod
    def list_all() -> list:
        return DatasetRepository.find_all()

    @staticmethod
    def get_by_id(dataset_id: int) -> Optional[dict]:
        return DatasetRepository.find_by_id(dataset_id)

    @staticmethod
    def get_full_data(generation_id: int) -> Optional[dict]:
        return DatasetRepository.find_full_data(generation_id)
