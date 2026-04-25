import sqlite3
import json
from datetime import datetime

DB_PATH = "data/recsys.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS feedback (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            artist_id   INTEGER NOT NULL,
            event       TEXT NOT NULL,
            variant     TEXT NOT NULL,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            variant     TEXT NOT NULL,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_feedback(user_id: int, artist_id: int,
                  event: str, variant: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO feedback (user_id, artist_id, event, variant) VALUES (?,?,?,?)",
        (user_id, artist_id, event, variant)
    )
    conn.commit()
    conn.close()


def get_feedback_stats() -> dict:
    conn = get_conn()
    rows = conn.execute("""
        SELECT variant, event, COUNT(*) as count
        FROM feedback
        GROUP BY variant, event
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]