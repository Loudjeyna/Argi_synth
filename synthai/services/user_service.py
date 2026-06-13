"""Service Layer — user management workflow."""

from typing import Optional

from synthai.data.repositories.user_repository import UserRepository


class UserService:
    """Coordinates user CRUD operations — wraps UserRepository for the API layer."""

    @staticmethod
    def list_users() -> list:
        users = UserRepository.find_all()
        for u in users:
            u.pop("password_hash", None)
        return users

    @staticmethod
    def get_user(user_id: int) -> Optional[dict]:
        return UserRepository.find_by_id(user_id)

    @staticmethod
    def update_plan(user_id: int, plan: str) -> bool:
        return UserRepository.update_plan(user_id, plan)

    @staticmethod
    def toggle_active(user_id: int) -> Optional[bool]:
        return UserRepository.toggle_active(user_id)
