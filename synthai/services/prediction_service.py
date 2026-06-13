"""Service Layer — crop prediction workflow."""

import json

from synthai.business.recommendation.crop_recommender import CropRecommender
from synthai.data.repositories.crop_repository import CropRepository
from synthai.data.repositories.crop_data_repository import CropDataRepository
from synthai.data.repositories.prediction_repository import PredictionRepository
from synthai.data.repositories.payment_repository import UsageLogRepository


class PredictionService:
    """Coordinates prediction: input → recommender engine → persist."""

    @staticmethod
    def _build_recommender() -> CropRecommender:
        df = CropDataRepository.load_all()
        return CropRecommender(crop_df=df)

    @staticmethod
    def predict(user_id: int, conditions: dict) -> dict:
        recommender = PredictionService._build_recommender()
        results = recommender.predict(conditions)
        top_crop = results[0]["crop"] if results else None
        top_crop_id = None
        if top_crop:
            crop = CropRepository.find_by_name_en(top_crop)
            if crop:
                top_crop_id = crop["id"]

        PredictionRepository.create_recommendation(
            user_id=user_id,
            input_data=json.dumps(conditions),
            results=json.dumps(results),
            top_crop_id=top_crop_id,
        )
        UsageLogRepository.add(user_id, "prediction")
        return {"results": results, "top_crop": top_crop}

    @staticmethod
    def get_crop_requirements(crop_name: str) -> dict:
        recommender = PredictionService._build_recommender()
        rec = recommender.get_recommendation(crop_name)
        if rec:
            return rec
        return {}

    @staticmethod
    def get_all_crops() -> list:
        return CropDataRepository.get_crop_names()

    @staticmethod
    def get_prediction_history(user_id: int, limit: int = 100) -> list:
        return PredictionRepository.find_recommendations(user_id, limit)
