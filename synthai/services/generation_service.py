"""Service Layer — synthetic data generation and validation workflow."""

import json
from typing import Optional
import pandas as pd

from synthai.ai.generation.sampler import SimpleSampler
from synthai.ai.preprocessing.data_loader import DataLoader
from synthai.ai.evaluation.metrics import DataStatistics, DataComparison
from synthai.data.repositories.dataset_repository import DatasetRepository
from synthai.data.repositories.payment_repository import UsageLogRepository
from synthai.data.config.settings import DATASET_SIZES, CROP_CSV_PATH


class GenerationService:
    """Coordinates generation: generate → validate → persist (stateless)."""

    @staticmethod
    def generate(user_id: int, num_rows: int = 1000,
                 dataset_type: str = "crop", level: str = "Medium",
                 model_id: int = None, model_version: int = None) -> dict:
        result = SimpleSampler.sample(num_rows=num_rows)
        synth_df = result["synth_df"]
        headers = result["headers"]
        preview = result["preview"]
        csv_path = result["file_path"]

        # stats
        headers = list(synth_df.columns)
        preview = synth_df.head(50).to_dict(orient="records")

        # persist
        gen_data = {
            "user_id": user_id,
            "model_id": model_id,
            "model_version": model_version,
            "dataset_type": dataset_type,
            "dataset_level": level,
            "rows_generated": num_rows,
            "status": "completed",
            "headers": json.dumps(headers),
            "preview_data": json.dumps(preview),
            "full_data_stored": 0,
            "validation_report": None,
            "correlation_similarity": None,
            "cloudinary_url": None,
            "file_url": str(csv_path),
        }
        gen_id = DatasetRepository.create(gen_data)
        UsageLogRepository.add(user_id, "generation", num_rows)

        return {
            "id": gen_id,
            "rows": num_rows,
            "headers": headers,
            "preview": preview,
            "file_path": str(csv_path),
            "created_at": gen_data.get("created_at"),
        }

    @staticmethod
    def validate(dataset_id: int, real_df: Optional[pd.DataFrame] = None) -> dict:
        entry = DatasetRepository.find_by_id(dataset_id)
        if not entry:
            return {"error": "Dataset not found"}
        file_path = entry.get("file_path")
        if not file_path or not pd.io.common.file_exists(file_path):
            return {"error": "Dataset file not found"}
        synth_df = pd.read_csv(file_path)
        if real_df is None:
            loader = DataLoader(str(CROP_CSV_PATH))
            real_df = loader.load()
        stats = {
            "synthetic": DataStatistics.compute_descriptive_stats(synth_df),
            "real": DataStatistics.compute_descriptive_stats(real_df),
        }
        comparison = DataComparison.compare_statistics(real_df, synth_df)
        similarity = DataComparison.compute_similarity_score(real_df, synth_df)
        return {
            "statistics": stats,
            "comparison": comparison.to_dict(orient="index"),
            "similarity": similarity,
        }
