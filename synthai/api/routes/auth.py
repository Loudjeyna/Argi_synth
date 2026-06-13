"""Authentication endpoints."""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from synthai.services.auth_service import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "farmer"


@router.post("/login")
async def login(req: LoginRequest):
    result = AuthService.login(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@router.post("/register")
async def register(req: RegisterRequest):
    result = AuthService.register(req.username, req.email, req.password, req.role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/logout")
async def logout(token: str):
    AuthService.logout(token)
    return {"success": True}
