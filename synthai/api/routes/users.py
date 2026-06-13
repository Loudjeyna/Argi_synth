"""API Layer — user-management endpoints (admin only, thin bridge)."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from synthai.services.user_service import UserService
from synthai.api.middleware import require_role

router = APIRouter()


class UpdateUserRequest(BaseModel):
    plan: str = None
    is_active: bool = None


@router.get("")
async def list_users(user: dict = Depends(require_role("admin"))):
    return UserService.list_users()


@router.get("/{user_id}")
async def get_user(user_id: int, user: dict = Depends(require_role("admin"))):
    u = UserService.get_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.put("/{user_id}")
async def update_user(user_id: int, req: UpdateUserRequest,
                      user: dict = Depends(require_role("admin"))):
    if req.plan:
        UserService.update_plan(user_id, req.plan)
    if req.is_active is not None:
        UserService.toggle_active(user_id)
    return {"success": True}
