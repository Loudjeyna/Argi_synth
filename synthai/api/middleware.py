"""API Layer — CORS + auth middleware."""
from typing import Callable

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from synthai.services.auth_service import AuthService


async def require_auth(request: Request) -> dict:
    """Extract and validate Bearer token, return current user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ", 1)[1]
    user = AuthService.get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    return user


def require_role(role: str) -> Callable:
    """Factory: returns a dependency that requires a specific role."""
    async def _check(request: Request) -> dict:
        user = await require_auth(request)
        if user["role"] != role and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return _check
