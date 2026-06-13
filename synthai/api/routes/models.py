"""API Layer — model training & status endpoints (thin bridge, stateless)."""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from synthai.services.training_service import TrainingService

router = APIRouter()


class TrainRequest(BaseModel):
    epochs: int = 300
    batch_size: int = 256


@router.post("/train")
async def train_model(req: TrainRequest):
    svc = TrainingService()
    try:
        result = svc.train(user_id=1, epochs=req.epochs, batch_size=req.batch_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def model_status():
    svc = TrainingService()
    trained = svc.is_trained()
    return {"is_trained": trained, "model_type": "CTGAN"}
