
import sqlite3
from datetime import datetime
from pathlib import Path

# Keep the database in the backend folder,
# regardless of the directory used to start the server.
DATABASE_NAME = Path(__file__).resolve().parent / "chat_history.db"


def get_connection():
    connection = sqlite3.connect(str(DATABASE_NAME))
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                language TEXT,
                intent TEXT,
                timestamp TEXT
            )
        """)


def save_chat(
    user_id,
    user_message,
    bot_response,
    language,
    intent
):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO chat_history (
                user_id,
                user_message,
                bot_response,
                language,
                intent,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_message,
            bot_response,
            language,
            intent,
            datetime.now().isoformat(timespec="seconds")
        ))


def get_chat_history(user_id, language=None):
    with get_connection() as connection:
        if language:
            rows = connection.execute("""
                SELECT
                    user_message,
                    bot_response,
                    language,
                    intent,
                    timestamp
                FROM chat_history
                WHERE user_id = ? AND language = ?
                ORDER BY id ASC
            """, (user_id, language)).fetchall()
        else:
            rows = connection.execute("""
                SELECT
                    user_message,
                    bot_response,
                    language,
                    intent,
                    timestamp
                FROM chat_history
                WHERE user_id = ?
                ORDER BY id ASC
            """, (user_id,)).fetchall()

    return [
        {
            "user_message": row["user_message"],
            "bot_response": row["bot_response"],
            "language": row["language"],
            "intent": row["intent"],
            "timestamp": row["timestamp"]
        }
        for row in rows
    ]
