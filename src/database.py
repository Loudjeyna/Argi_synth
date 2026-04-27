import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Tuple, List, Dict
import os


class Database:
    """SQLite database management."""
    
    DB_PATH = "data/agroai.db"
    
    @classmethod
    def init_db(cls):
        """Initialize database tables."""
        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'farmer',
                plan TEXT DEFAULT 'free',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rows_generated INTEGER DEFAULT 0,
                generation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_status (
                id INTEGER PRIMARY KEY,
                is_trained INTEGER DEFAULT 0,
                model_type TEXT DEFAULT 'CTGAN',
                last_trained TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                prediction_type TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_result TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthetic_datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                rows_generated INTEGER NOT NULL,
                file_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, plan)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", "admin@agroai.com", admin_password, "admin", "premium"))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(cls.DB_PATH)
    
    @classmethod
    def add_user(cls, username: str, email: str, password: str, role: str = "farmer") -> bool:
        """Add new user."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[dict]:
        """Authenticate user."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            SELECT id, username, email, role, plan, created_at
            FROM users WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "role": result[3],
                "plan": result[4],
                "created_at": result[5]
            }
        return None
    
    @classmethod
    def get_all_users(cls) -> list:
        """Get all users."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, role, plan, created_at
            FROM users ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        return users
    
    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, role, plan, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "role": result[3],
                "plan": result[4],
                "created_at": result[5]
            }
        return None
    
    @classmethod
    def update_plan(cls, username: str, plan: str) -> bool:
        """Update user plan."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET plan = ? WHERE username = ?
        """, (plan, username))
        conn.commit()
        conn.close()
        return True
    
    @classmethod
    def get_usage_today(cls, user_id: int) -> int:
        """Get today's usage."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COALESCE(SUM(rows_generated), 0)
            FROM usage_logs
            WHERE user_id = ? AND generation_date LIKE ?
        """, (user_id, f"{today}%"))
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    @classmethod
    def add_usage(cls, user_id: int, rows: int) -> None:
        """Add usage record."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usage_logs (user_id, rows_generated)
            VALUES (?, ?)
        """, (user_id, rows))
        conn.commit()
        conn.close()
    
    @classmethod
    def check_quota(cls, user_id: int, rows: int) -> bool:
        """Check if user has quota."""
        user = cls.get_user_by_id(user_id)
        if not user:
            return False
        
        if user["plan"] == "premium":
            return True
        
        today_usage = cls.get_usage_today(user_id)
        return (today_usage + rows) <= 100
    
    @classmethod
    def is_model_trained(cls) -> Tuple[bool, str]:
        """Check if model is trained."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_trained, model_type FROM model_status WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return bool(result[0]), result[1]
        return False, "CTGAN"
    
    @classmethod
    def set_model_trained(cls, trained: bool, model_type: str = "CTGAN") -> None:
        """Set model trained status."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO model_status (id, is_trained, model_type, last_trained)
            VALUES (1, ?, ?, ?)
        """, (int(trained), model_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    
    # ============ PREDICTION HISTORY ============
    
    @classmethod
    def add_prediction(cls, user_id: int, prediction_type: str, input_data: str, output_result: str) -> int:
        """Add prediction to history."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (user_id, prediction_type, input_data, output_result)
            VALUES (?, ?, ?, ?)
        """, (user_id, prediction_type, input_data, output_result))
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        return prediction_id
    
    @classmethod
    def get_user_predictions(cls, user_id: int, limit: int = 100) -> List[Dict]:
        """Get prediction history for a user."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prediction_type, input_data, output_result, created_at
            FROM predictions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "id": row[0],
                "prediction_type": row[1],
                "input_data": row[2],
                "output_result": row[3],
                "created_at": row[4]
            })
        conn.close()
        return predictions
    
    @classmethod
    def get_prediction_count(cls, user_id: int) -> int:
        """Get total prediction count for a user."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @classmethod
    def get_predictions_by_crop(cls, user_id: int, crop: str) -> List[Dict]:
        """Get predictions filtered by crop."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prediction_type, input_data, output_result, created_at
            FROM predictions
            WHERE user_id = ? AND output_result LIKE ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id, "%" + crop + "%"))
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "id": row[0],
                "prediction_type": row[1],
                "input_data": row[2],
                "output_result": row[3],
                "created_at": row[4]
            })
        conn.close()
        return predictions
    
    @classmethod
    def get_predictions_by_date(cls, user_id: int, date: str) -> List[Dict]:
        """Get predictions filtered by date."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prediction_type, input_data, output_result, created_at
            FROM predictions
            WHERE user_id = ? AND created_at LIKE ?
            ORDER BY created_at DESC
        """, (user_id, date + "%"))
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "id": row[0],
                "prediction_type": row[1],
                "input_data": row[2],
                "output_result": row[3],
                "created_at": row[4]
            })
        conn.close()
        return predictions
    
    @classmethod
    def get_recent_predictions(cls, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent predictions (limited by plan)."""
        user = cls.get_user_by_id(user_id)
        if user and user["plan"] == "free":
            return cls.get_user_predictions(user_id, limit)
        return cls.get_user_predictions(user_id, limit * 10)
    
    # ============ SYNTHETIC DATASETS ============
    
    @classmethod
    def add_synthetic_dataset(cls, admin_id: int, rows_generated: int, file_path: str = None) -> int:
        """Record synthetic dataset generation."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO synthetic_datasets (admin_id, rows_generated, file_path)
            VALUES (?, ?, ?)
        """, (admin_id, rows_generated, file_path))
        conn.commit()
        dataset_id = cursor.lastrowid
        conn.close()
        return dataset_id
    
    @classmethod
    def get_all_datasets(cls) -> List[Dict]:
        """Get all synthetic datasets."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sd.id, sd.rows_generated, sd.file_path, sd.created_at, u.username
            FROM synthetic_datasets sd
            JOIN users u ON sd.admin_id = u.id
            ORDER BY sd.created_at DESC
        """)
        datasets = []
        for row in cursor.fetchall():
            datasets.append({
                "id": row[0],
                "rows_generated": row[1],
                "file_path": row[2],
                "created_at": row[3],
                "admin": row[4]
            })
        conn.close()
        return datasets
    
    @classmethod
    def get_dataset_count(cls) -> int:
        """Get total dataset count."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM synthetic_datasets")
        count = cursor.fetchone()[0]
        conn.close()
        return count