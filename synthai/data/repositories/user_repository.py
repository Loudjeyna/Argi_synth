"""User repository — CRUD for the users table."""

from typing import Optional
from synthai.data.database import Database


class UserRepository:
    """Persistence operations on the `users` table."""

    @staticmethod
    def find_by_username(username: str) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT id, username, email, password_hash, role, plan, is_active, "
            "attempts, last_reset_date, subscription_expires_at, created_at "
            "FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_by_id(user_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT id, username, email, role, plan, is_active, created_at "
            "FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_all() -> list:
        conn = Database.get_connection()
        rows = conn.execute(
            "SELECT id, username, email, role, plan, is_active, created_at "
            "FROM users ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(username: str, email: str, password_hash: str, role: str = "farmer") -> Optional[int]:
        conn = Database.get_connection()
        try:
            c = conn.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, role),
            )
            conn.commit()
            return c.lastrowid
        except Exception:
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def update_plan(user_id: int, plan: str) -> bool:
        conn = Database.get_connection()
        conn.execute("UPDATE users SET plan = ?, updated_at = datetime('now') WHERE id = ?", (plan, user_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def toggle_active(user_id: int) -> Optional[bool]:
        conn = Database.get_connection()
        row = conn.execute("SELECT is_active FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            conn.close()
            return None
        new_val = 0 if row["is_active"] else 1
        conn.execute("UPDATE users SET is_active = ?, updated_at = datetime('now') WHERE id = ?", (new_val, user_id))
        conn.commit()
        conn.close()
        return bool(new_val)

    @staticmethod
    def authenticate(username: str, password_hash: str) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT id, username, email, role, plan, created_at "
            "FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
            (username, password_hash),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_attempts(user_id: int, attempts: int, reset_date: str) -> None:
        conn = Database.get_connection()
        conn.execute(
            "UPDATE users SET attempts = ?, last_reset_date = ?, updated_at = datetime('now') WHERE id = ?",
            (attempts, reset_date, user_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_subscription(user_id: int, plan: str, expires_at: str) -> None:
        conn = Database.get_connection()
        conn.execute(
            "UPDATE users SET plan = ?, subscription_expires_at = ?, updated_at = datetime('now') WHERE id = ?",
            (plan, expires_at, user_id),
        )
        conn.commit()
        conn.close()
