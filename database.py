import sqlite3

DATABASE = "sessions.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at REAL NOT NULL,
            last_activity REAL NOT NULL,
            is_active INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()
