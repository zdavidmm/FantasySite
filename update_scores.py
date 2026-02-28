import datetime
import logging
import os
import sqlite3
import sys
from typing import Dict, Optional

import db
import requests

SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
DB_FILE = os.environ.get("DB_FILE", db.DB_FILE)

# Opening Day for the season. Used when no start date is supplied.
# Override with OPENING_DAY env var to avoid hardcoding each year.
OPENING_DAY = os.environ.get("OPENING_DAY", "2026-03-26")

logger = logging.getLogger(__name__)


def load_scoreboard(conn: Optional[sqlite3.Connection] = None) -> Dict[str, dict]:
    if conn is None:
        conn = db.connect(DB_FILE)
    logger.debug("Loading scoreboard from database %s", DB_FILE)
    db.init_db(conn)
    return db.load_scoreboard(conn)


def save_run(conn: sqlite3.Connection, team: str, run_total: int, date: str, game_pk: int):
    db.record_run(conn, team, run_total, date, game_pk)


def fetch_games(date: str) -> list:
    url = SCHEDULE_URL.format(date=date)
    logger.debug("Fetching games from %s", url)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    dates = data.get("dates", [])
    if not dates:
        logger.debug("No games found for %s", date)
        return []
    games = dates[0].get("games", [])
    logger.debug("Fetched %d games", len(games))
    return games


def update_for_date(
    date: str,
    scoreboard: Optional[Dict[str, dict]] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Dict[str, dict]:
    """Update the scoreboard for a single date.

    If *scoreboard* is provided it will be updated in place and returned. When
    *conn* is ``None`` a new connection is opened and closed automatically.
    """
    logger.debug("Updating scores for %s", date)
    games = fetch_games(date)
    close_conn = False
    if conn is None:
        conn = db.connect(DB_FILE)
        close_conn = True
    db.init_db(conn)
    if scoreboard is None:
        scoreboard = db.load_scoreboard(conn)

    for game in games:
        game_pk = game.get("gamePk")
        for side in ["home", "away"]:
            team = game["teams"][side]["team"]["name"]
            team_data = game["teams"][side]
            if "score" not in team_data:
                # Skip if this game has no score yet (e.g., not started)
                continue
            runs = team_data["score"]
            if team not in scoreboard:
                scoreboard[team] = {}
            run_key = str(runs)
            if run_key not in scoreboard[team]:
                logger.debug("Adding run total %s for %s", runs, team)
                scoreboard[team][run_key] = {
                    "date": date,
                    "game_pk": game_pk,
                }
                save_run(conn, team, runs, date, game_pk)

    if close_conn:
        conn.close()
        print(f"Updated scores for {date}")

    return scoreboard


def update_since(start_date: str):
    """Update scores for every day from *start_date* through yesterday."""
    logger.debug("Updating scores since %s", start_date)
    current = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    conn = db.connect(DB_FILE)
    db.init_db(conn)
    scoreboard = db.load_scoreboard(conn)
    while current <= end_date:
        update_for_date(current.isoformat(), scoreboard, conn)
        current += datetime.timedelta(days=1)
    conn.close()
    print(f"Updated scores for {start_date} through {end_date.isoformat()}")


def main():
    logging.basicConfig(level=logging.DEBUG if os.environ.get("LOG_LEVEL") == "DEBUG" else logging.INFO)
    if len(sys.argv) > 1:
        start_date = sys.argv[1]
    else:
        start_date = OPENING_DAY
    update_since(start_date)


if __name__ == "__main__":
    main()
