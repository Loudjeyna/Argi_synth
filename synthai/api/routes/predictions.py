"""Prediction endpoints."""

from pydantic import BaseModel
from fastapi import APIRouter

from synthai.services.prediction_service import PredictionService

router = APIRouter()


class PredictRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


@router.post("")
async def predict(req: PredictRequest):
    conditions = {
        "N": req.N, "P": req.P, "K": req.K,
        "temperature": req.temperature,
        "humidity": req.humidity,
        "ph": req.ph,
        "rainfall": req.rainfall,
    }
    result = PredictionService.predict(user_id=1, conditions=conditions)
    return result


@router.get("/crops")
async def list_crops():
    return {"crops": PredictionService.get_all_crops()}


@router.get("/crops/{crop_name}")
async def crop_requirements(crop_name: str):
    return PredictionService.get_crop_requirements(crop_name)


@router.get("/history/{user_id}")
async def prediction_history(user_id: int):
    return PredictionService.get_prediction_history(user_id)
