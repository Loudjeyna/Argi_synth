"""Service Layer — authentication and session workflow."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from synthai.data.database import Database
from synthai.data.repositories.user_repository import UserRepository
from synthai.data.repositories.session_repository import SessionRepository
from synthai.business.rules.usage_limits import UsageLimits


class AuthService:
    """Coordinates login, register, session management across repositories + rules."""

    @staticmethod
    def register(username: str, email: str, password: str, role: str = "farmer") -> dict:
        if role not in ("admin", "farmer", "company"):
            return {"success": False, "message": "Invalid role"}
        password_hash = Database.hash_password(password)
        user_id = UserRepository.create(username, email, password_hash, role)
        if user_id is None:
            return {"success": False, "message": "Username or email already exists"}
        return {"success": True, "user_id": user_id}

    @staticmethod
    def login(username: str, password: str) -> dict:
        password_hash = Database.hash_password(password)
        user = UserRepository.authenticate(username, password_hash)
        if user is None:
            return {"success": False, "message": "Invalid credentials or account disabled"}
        # reset daily attempts if needed — delegated to UsageLimits rule
        u = UserRepository.find_by_username(username)
        if u and UsageLimits.needs_reset(u.get("last_reset_date", "")):
            UserRepository.update_attempts(user["id"], 0, UsageLimits.get_today_date())
        # create session token via repository
        token = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        SessionRepository.create(user["id"], token, expires_at)
        return {"success": True, "user": user, "token": token}

    @staticmethod
    def logout(token: str) -> None:
        SessionRepository.delete(token)

    @staticmethod
    def get_current_user(token: str) -> Optional[dict]:
        return SessionRepository.find_user_by_token(token)
