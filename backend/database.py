import sqlite3
from datetime import datetime


DATABASE_NAME = "chat_history.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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

    connection.commit()
    connection.close()


def save_chat(
    user_id,
    user_message,
    bot_response,
    language,
    intent
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (
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
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_chat_history(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_message,
            bot_response,
            language,
            intent,
            timestamp
        FROM chat_history
        WHERE user_id = ?
        ORDER BY id ASC
    """, (user_id,))

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:
        history.append({
            "user_message": row[0],
            "bot_response": row[1],
            "language": row[2],
            "intent": row[3],
            "timestamp": row[4]
        })

    return history