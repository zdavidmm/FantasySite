import os
import sqlite3
from typing import Dict, Optional

DB_FILE = os.environ.get("DB_FILE", "fantasy.db")


def connect(db_file: Optional[str] = None):
    """Return a SQLite connection to the database."""
    if db_file is None:
        db_file = DB_FILE
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection):
    """Create required tables if they do not exist."""
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS participants (
            participant TEXT PRIMARY KEY,
            team TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS scoreboard (
            team TEXT,
            run_total INTEGER,
            date TEXT,
            game_pk INTEGER,
            PRIMARY KEY (team, run_total)
        )"""
    )
    conn.commit()


def save_assignments(assignments: Dict[str, str], conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("DELETE FROM participants")
    cur.executemany(
        "INSERT INTO participants (participant, team) VALUES (?, ?)",
        list(assignments.items()),
    )
    conn.commit()


def get_assignments(conn: sqlite3.Connection) -> Dict[str, str]:
    cur = conn.cursor()
    rows = cur.execute("SELECT participant, team FROM participants").fetchall()
    return {row[0]: row[1] for row in rows}


def record_run(
    conn: sqlite3.Connection, team: str, run_total: int, date: str, game_pk: int
):
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO scoreboard (team, run_total, date, game_pk) VALUES (?, ?, ?, ?)",
        (team, run_total, date, game_pk),
    )
    conn.commit()


def load_scoreboard(conn: sqlite3.Connection) -> Dict[str, Dict[str, Dict[str, int]]]:
    scoreboard: Dict[str, Dict[str, Dict[str, int]]] = {}
    cur = conn.cursor()
    for row in cur.execute("SELECT team, run_total, date, game_pk FROM scoreboard"):
        scoreboard.setdefault(row[0], {})[str(row[1])] = {
            "date": row[2],
            "game_pk": row[3],
        }
    return scoreboard
