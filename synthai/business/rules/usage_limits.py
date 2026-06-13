"""Business Logic Layer — daily usage limits and quota rules."""

from datetime import datetime


class UsageLimits:
    """Stateless daily quota calculation rules."""

    @staticmethod
    def get_today_date() -> str:
        return datetime.utcnow().strftime("%Y-%m-%d")

    @staticmethod
    def needs_reset(last_reset_date: str) -> bool:
        return last_reset_date != UsageLimits.get_today_date()

    @staticmethod
    def remaining_attempts(plan: str, attempts_today: int) -> int:
        limits = {"free": 5, "pro": 50, "premium": 999999}
        max_att = limits.get(plan, 5)
        return max(0, max_att - attempts_today)

    @staticmethod
    def can_attempt(plan: str, role: str, attempts_today: int) -> bool:
        if role == "admin" or plan == "premium":
            return True
        max_att = {"free": 5, "pro": 50}.get(plan, 5)
        return attempts_today < max_att
