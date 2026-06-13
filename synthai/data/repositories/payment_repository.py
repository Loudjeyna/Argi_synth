"""Payment repository — CRUD for payments and usage_logs."""

from typing import Optional
from synthai.data.database import Database


class PaymentRepository:
    """Persistence for `payments` table."""

    @staticmethod
    def find_by_user(user_id: int) -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT * FROM payments WHERE user_id = ? ORDER BY subscribed_at DESC", (user_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def find_active(user_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT * FROM payments WHERE user_id = ? AND status = 'active' AND expires_at > datetime('now') "
            "ORDER BY subscribed_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(user_id: int, plan_id: str, plan_name: str, price: float, expires_at: str) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO payments (user_id, plan_id, plan_name, price, expires_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, plan_id, plan_name, price, expires_at),
        )
        conn.commit()
        conn.close()
        return c.lastrowid


class UsageLogRepository:
    """Persistence for `usage_logs` table."""

    @staticmethod
    def add(user_id: int, action_type: str, rows_affected: int = 0) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO usage_logs (user_id, action_type, rows_affected) VALUES (?, ?, ?)",
            (user_id, action_type, rows_affected),
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def count_today(user_id: int) -> int:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT COALESCE(SUM(rows_affected), 0) AS total FROM usage_logs "
            "WHERE user_id = ? AND created_at >= date('now')",
            (user_id,),
        ).fetchone()
        conn.close()
        return row["total"]

    @staticmethod
    def count_today_by_action(user_id: int, action_type: str) -> int:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM usage_logs "
            "WHERE user_id = ? AND action_type = ? AND created_at >= date('now')",
            (user_id, action_type),
        ).fetchone()
        conn.close()
        return row["cnt"]
