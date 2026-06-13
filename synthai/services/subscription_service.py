"""Service Layer — subscription and payment workflow."""

from datetime import datetime, timedelta

from synthai.data.repositories.user_repository import UserRepository
from synthai.data.repositories.payment_repository import PaymentRepository
from synthai.business.rules.subscription_rules import SubscriptionRules, PLANS


class SubscriptionService:
    """Coordinates plan changes, payment recording, and limit enforcement."""

    @staticmethod
    def subscribe(user_id: int, plan_id: str) -> dict:
        if plan_id not in PLANS:
            return {"success": False, "message": "Invalid plan"}
        plan = PLANS[plan_id]
        expires_at = SubscriptionRules.compute_expiry(30)
        # record payment
        PaymentRepository.create(user_id, plan_id, plan["name"], plan["price"], expires_at)
        # update user plan
        UserRepository.update_subscription(user_id, plan_id, expires_at)
        return {
            "success": True,
            "plan": plan_id,
            "expires_at": expires_at,
        }

    @staticmethod
    def get_user_plan(user_id: int) -> str:
        active = PaymentRepository.find_active(user_id)
        if active:
            return active["plan_id"]
        user = UserRepository.find_by_id(user_id)
        return user["plan"] if user else "free"

    @staticmethod
    def get_payment_history(user_id: int) -> list:
        return PaymentRepository.find_by_user(user_id)

    @staticmethod
    def allowed_sizes(user_id: int) -> list:
        plan = SubscriptionService.get_user_plan(user_id)
        return SubscriptionRules.allowed_dataset_sizes(plan)

    @staticmethod
    def allowed_multipliers(user_id: int) -> list:
        plan = SubscriptionService.get_user_plan(user_id)
        return SubscriptionRules.allowed_augmentation_multipliers(plan)
