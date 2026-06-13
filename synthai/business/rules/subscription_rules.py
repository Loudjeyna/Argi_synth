"""Business Logic Layer — subscription & feature-access rules."""

from datetime import datetime, timedelta
from typing import Optional


PLANS = {
    "free":    {"name": "Free", "price": 0,     "max_daily_rows": 100,  "dataset_sizes": ["medium"],            "generations_per_day": 5},
    "pro":     {"name": "Pro", "price": 9.99,   "max_daily_rows": 1000, "dataset_sizes": ["medium", "large"],   "generations_per_day": 50},
    "premium": {"name": "Premium", "price": 29.99, "max_daily_rows": None, "dataset_sizes": ["medium", "large", "bigdata"], "generations_per_day": None},
}


class SubscriptionRules:
    """Pure business rules for plan limits — no storage logic."""

    @staticmethod
    def allowed_dataset_sizes(plan: str) -> list:
        return PLANS.get(plan, PLANS["free"])["dataset_sizes"]

    @staticmethod
    def max_daily_rows(plan: str) -> Optional[int]:
        return PLANS.get(plan, PLANS["free"]).get("max_daily_rows")

    @staticmethod
    def max_generations_per_day(plan: str) -> Optional[int]:
        return PLANS.get(plan, PLANS["free"]).get("generations_per_day")

    @staticmethod
    def can_access_size(plan: str, size: str) -> bool:
        return size in SubscriptionRules.allowed_dataset_sizes(plan)

    @staticmethod
    def can_access_feature(plan: str, feature: str) -> bool:
        if plan == "premium":
            return True
        if plan == "pro":
            return feature != "bigdata"
        return feature == "medium"

    @staticmethod
    def allowed_augmentation_multipliers(plan: str) -> list:
        mapping = {"free": [2], "pro": [2, 5], "premium": [2, 5, 10]}
        return mapping.get(plan, [2])

    @staticmethod
    def has_quota(plan: str, today_rows: int, requested_rows: int) -> bool:
        if plan == "premium":
            return True
        max_rows = SubscriptionRules.max_daily_rows(plan)
        if max_rows is None:
            return True
        return (today_rows + requested_rows) <= max_rows

    @staticmethod
    def compute_expiry(days: int = 30) -> str:
        return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
