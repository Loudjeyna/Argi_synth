"""API Layer — dataset generation, listing, and validation endpoints (thin bridge)."""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from synthai.services.generation_service import GenerationService
from synthai.services.dataset_service import DatasetService

router = APIRouter()


class GenerateRequest(BaseModel):
    num_rows: int = 1000
    dataset_type: str = "crop"
    level: str = "Medium"


@router.post("/generate")
async def generate(req: GenerateRequest):
    try:
        svc = GenerationService()
        result = svc.generate(
            user_id=1,
            num_rows=req.num_rows,
            dataset_type=req.dataset_type,
            level=req.level,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_datasets():
    return DatasetService.list_all()


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: int):
    entry = DatasetService.get_by_id(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return entry


@router.get("/validate/{dataset_id}")
async def validate_dataset(dataset_id: int):
    svc = GenerationService()
    result = svc.validate(dataset_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
