# storage.py
import sqlite3

DB_NAME = "data/habits.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates tables if they do not exist."""
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            periodicity TEXT CHECK(periodicity IN ('daily','weekly','monthly','yearly')),
            created_at TEXT NOT NULL,
            start_date TEXT,
            due_date TEXT,
            active_days TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    ''')

    conn.commit()
    conn.close()
