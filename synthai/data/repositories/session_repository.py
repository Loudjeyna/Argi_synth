"""Data Layer — session persistence for authentication tokens."""

from typing import Optional
from synthai.data.database import Database


class SessionRepository:
    """CRUD for the `sessions` table."""

    @staticmethod
    def create(user_id: int, token: str, expires_at: str) -> int:
        conn = Database.get_connection()
        c = conn.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at),
        )
        conn.commit()
        conn.close()
        return c.lastrowid

    @staticmethod
    def delete(token: str) -> None:
        conn = Database.get_connection()
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    @staticmethod
    def find_user_by_token(token: str) -> Optional[dict]:
        conn = Database.get_connection()
        row = conn.execute(
            "SELECT u.id, u.username, u.email, u.role, u.plan, u.created_at "
            "FROM sessions s JOIN users u ON s.user_id = u.id "
            "WHERE s.token = ? AND s.expires_at > datetime('now')",
            (token,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None
